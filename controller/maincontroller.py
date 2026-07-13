import flet as ft
from model.professionalmodel import ProfessionlModel
from model.clientmodel import ClientModel
from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
from model.mainmodel import mainModel
from utils.formatcurr import formatar_moeda_brasileira, _parse_currency
from utils.secure_storage import SecureStorage
import json
from view.controls.colors import AppColors
from controller.call_api import ProtectedApiCall
from view.controls.custondialog import CustonDialog
from model.accountmodel import AccountModel
from urllib.parse import quote, urlparse
import datetime
from model.zapmodel import ZapModel
import asyncio
from controller.integracaocontroller import IntegracaoController
from flet.security import decrypt


class MainController:
    def __init__(self, page:ft.Page, instance):
        
        self.instance = instance
        self.page = page
        self.model = mainModel()
        self.model_professional = ProfessionlModel()
        self.model_clientes = ClientModel()
        self.account_model = AccountModel()
        self.zap_model = ZapModel()
        self.meta_integracao = IntegracaoController(self.page, self.instance)


    async def on_switch_ads(self, e):
        await self.meta_integracao.on_switch_ads(e.control.value)


    async def init_onesignal(self):
        if self.page.session.store.get("onesignal_initialized"):
            return
        if self.instance.account_tel:
            js_login = f"javascript:window.OneSignalDeferred?.push(function(OS) {{ OS.login('{self.instance.account_tel}'); }});"
            await self.page.launch_url(js_login)
            self.page.session.store.set("onesignal_initialized", True)


    async def notify_agenda_pendentes(self):
        response = await ProtectedApiCall(
            self.page, 
            self.instance, 
            self.model.notify_pendentes_agenda,
            id_loja=self.instance.id_loja,
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code == 200:
            resposta = json.loads(response.content)
            pendentes = resposta.get("count", 0)

            if pendentes > 0:
                self.page.session.store.set("is_pendent", True)
                self.page.run_task(self.animar_notificacao, True)
            else:
                self.page.session.store.set("is_pendent", False)
                self.page.run_task(self.animar_notificacao, False)

        
    async def animar_notificacao(self, ativar: bool):
        if ativar:
            # Se já estiver visível e animando, não faz nada para evitar duplo loop
            if self.instance.icon_notification.visible:
                return
                
            self.instance.icon_notification.visible = True
            self.instance.icon_notification.scale = 1.0
            self.page.update()
            
            # Loop de animação (Batimento)
            while self.instance.icon_notification.visible:
                # Alterna o tamanho entre o normal (1.0) e maior (1.3)
                self.instance.icon_notification.scale = 1.3 if self.instance.icon_notification.scale == 1.0 else 1.0
                self.page.update()
                await asyncio.sleep(0.5) # Aguarda a transição terminar antes de inverter
        else:
            # Desliga a notificação e reseta o tamanho
            self.instance.icon_notification.visible = False
            self.instance.icon_notification.scale = 1.0
            self.page.update()        


    async def show_drawer(self):
        await self.page.show_drawer()


    async def create_link_agenda_turnos(self, e):
        parsed_url = urlparse(self.page.url)
        base_domain = f"https://{parsed_url.netloc}"
        base_url = f"{base_domain}/agendaturnos"
        await ft.Clipboard().set(base_url)
        await self.page.close_drawer()
        self.page.show_dialog(ft.SnackBar(content=ft.Text("Link copiado para a área de transferência!")))
        self.page.update()


    async def create_link_anamnese(self, e):
        account_name = quote(self.instance.account_name)
        parsed_url = urlparse(self.page.url)
        base_domain = f"https://{parsed_url.netloc}"
        base_url = f"{base_domain}/anamnese/{account_name}/{self.instance.account_tel}"
        await ft.Clipboard().set(base_url)
        await self.page.close_drawer()
        self.page.show_dialog(ft.SnackBar(content=ft.Text("Link copiado para a área de transferência!")))
        self.page.update()


    async def login_meta(self, e):
        if self.instance.meta_long_token:
            await self.meta_integracao.desconectar_meta_ads(e)
        else:
            await self.meta_integracao.vincular_meta_ads(e)


    async def create_instance_zap(self, e):
        await self.page.close_drawer()

        self.instance.progressRing.visible = True
        self.page.update()


        response = await ProtectedApiCall(
            self.page, self.instance, self.zap_model.CreateInstanceZap,
            id_loja=self.instance.id_loja,
            zap_number=self.instance.account_tel,
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code in [200, 201]:
            resposta = json.loads(response.content)

            qr_code = resposta.get('qrcode', {})
            par_code = qr_code.get('pairingCode', '')

            await ft.Clipboard().set(par_code)

            zap_dialog = CustonDialog(
                page=self.page,
                title='Atenção!',
                content=f'O código {par_code} foi colado na sua area de transferência, informe este código no seu whatsapp.',
                actions=[
                    ft.TextButton(
                        'OK',
                        on_click=lambda e: [self.page.pop_dialog(), self.page.update()]
                    ),
                ]
            )

            self.page.show_dialog(zap_dialog)

        self.instance.progressRing.visible = False

        self.page.update()    


    async def get_connection_zap(self):
        response = await ProtectedApiCall(
            self.page, 
            self.instance, 
            self.zap_model.GetConnectionZap,
            zap_instance=self.instance.zap_instance,
            token=self.instance.token
        ).call_api_refresh_token()
        
        resposta = json.loads(response.content)

        instance = resposta.get("instance", {})
        state = instance.get("state", '')

        self.instance.zap_status = state

        if self.instance.zap_status != 'open':
            self.instance.botao_whatsapp.content = 'Conectar'
            self.instance.status_whatsapp.value = 'Desconectado'
        else:
            self.instance.botao_whatsapp.content = 'Desconectar'
            self.instance.status_whatsapp.value = 'Conectado'

        self.page.update()


    async def atribuir_nota_cliente(self, e):
        nota = self.instance.radio_group_nota_cliente.value
        id_cliente = self.instance.id_client

        await ProtectedApiCall(self.page, self.instance, self.model.UpdateNotaCliente,
            id_cliente=id_cliente,
            nota=nota,
            token=self.instance.token
        ).call_api_refresh_token()

        self.page.pop_dialog()
        self.page.update()
        await self.limpar_venda(e)


    def open_modal_recebimento(self, e):
        self.instance.edt_dinheiro.value = ''
        self.instance.edt_pix.value      = ''
        self.instance.edt_debito.value   = ''
        self.instance.edt_credito.value  = ''

        self.instance.text_troco.value   = 'Troco: R$ 0,00'
        
        self.instance.text_total.value = f'Total: R$ {formatar_moeda_brasileira(self.instance.total)}'
        self.page.show_dialog(self.instance.modal_recebimento)                
        self.page.update()
    
    
    async def get_account_data(self):
        try:
            response = await ProtectedApiCall(
                self.page, self.instance, 
                self.account_model.getAccountData,
                id=self.instance.id_loja,
                token=self.instance.token
            ).call_api_refresh_token()
            
            data = json.loads(response.content)

            meta_long_token_encrypted = data.get("meta_long_token", "")
            
            self.instance.meta_long_token = ''
            if meta_long_token_encrypted:
                try:
                    decrypted_token = await self.meta_integracao.secure_storage.decrypt_value(meta_long_token_encrypted)
                    self.instance.meta_long_token = decrypted_token
                except Exception as dec_ex:
                    print(f"ERROR ao descriptografar token Meta: {dec_ex}")

            self.instance.account_name    = data["nome"           ]
            self.instance.account_tel     = data["telefone"       ]
            self.instance.zap_instance    = data["zap_instance"   ]
            self.instance.slug            = data["slug"           ]
            self.instance.status_campanha = data["status_campanha"]

            self.page.session.store.set("account_name", self.instance.account_name)
            self.page.session.store.set("account_tel",  self.instance.account_tel)
            self.page.session.store.set("zap_instance", self.instance.zap_instance)
            self.page.session.store.set("slug",                 self.instance.slug)
            self.page.session.store.set("meta_long_token", self.instance.meta_long_token)
            self.page.session.store.set("status_campanha", self.instance.status_campanha)

            await self.meta_integracao.atualizar_ui_meta()

            if not self.instance.account_tel:
                await self.page.push_route("/account")
        except Exception as ex:
            print(f"ERROR em get_account_data: {ex}")
            import traceback
            traceback.print_exc()


    async def get_status_caixa(self):

        response = await ProtectedApiCall(
            self.page, self.instance, self.model.status_caixa, 
            id_loja=self.instance.id_loja,
            token=self.instance.token
        ).call_api_refresh_token()       
                
        self.instance.status_caixa = json.loads(response.content)["status"]
        self.instance.id_caixa = json.loads(response.content)["id_caixa"]

        self.page.session.store.set("status_caixa", self.instance.status_caixa)
        self.page.session.store.set("id_caixa", str(self.instance.id_caixa))


    def _collect_payment_values(self):
        dinheiro = _parse_currency(self.instance.edt_dinheiro.value)
        pix      = _parse_currency(self.instance.edt_pix.value)
        debito   = _parse_currency(self.instance.edt_debito.value)
        credito  = _parse_currency(self.instance.edt_credito.value)
        
        return dinheiro, pix, debito, credito


    async def get_Data(self):
        try:
            try:
                self.instance.id_loja = self.page.session.store.get(     "id")
                self.instance.token   = self.page.session.store.get(  "token")
                self.instance.r_token = self.page.session.store.get("r_token")
            except Exception as e:
                print(f"DEBUG: Erro ao obter id_loja: {e}")
                self.instance.id_loja = None
                self.instance.token = None
            
            if not self.instance.token or not self.instance.id_loja:    
                await self.page.push_route("/")
                return

            self.instance.progressRing.visible = True
            self.page.update()
            
            #await self.get_status_caixa()

            if self.instance.total == 0:            
                self.instance.btn_total.visible = False
                #self.instance.btn_fechar_caixa.visible = True  

            #if self.instance.status_caixa == 'F':
            #    self.instance.btn_abrir_caixa.visible = True
            #    self.instance.btn_fechar_caixa.visible = False

            #elif self.instance.status_caixa == 'A':   
            #    self.instance.btn_fechar_caixa.visible = True
            #    self.instance.btn_abrir_caixa.visible = False        

            self.page.update()

            # Verificação e carregamento dos dados da conta com cache em sessão
            cached_name = self.page.session.store.get("account_name")
            cached_tel = self.page.session.store.get("account_tel")

            if cached_name and cached_tel:
                self.instance.account_name = cached_name
                self.instance.account_tel = cached_tel
                self.instance.zap_instance = self.page.session.store.get("zap_instance") or ''
                self.instance.slug = self.page.session.store.get("slug") or ''
                self.instance.meta_long_token = self.page.session.store.get("meta_long_token") or ''
                self.instance.status_campanha = self.page.session.store.get("status_campanha") or 'False'
            #else:
            await self.get_account_data()

            # Atualiza a UI da integração Meta em qualquer cenário (cache ou API)
            await self.meta_integracao.atualizar_ui_meta()

            # Dispara requisições paralelas para otimização extrema de performance
            tasks = [
                self.instance.carregar_profissionais(),
                self.instance.carregar_itens(),
                self.instance.carregar_clientes(),
                self.get_connection_zap(),
                self.notify_agenda_pendentes(),
                #self.init_onesignal(),
                self.meta_integracao.salvar_google_analytics()
            ]
            await asyncio.gather(*tasks)

            self.instance.progressRing.visible = False
            self.page.update()
        except Exception as ex:
            print(f"ERROR em get_Data: {ex}")
            import traceback
            traceback.print_exc()         


    def cancelar_receber_venda(self, e):
        self.instance.text_total.value   = ''
        self.instance.edt_dinheiro.value = ''
        self.instance.edt_pix.value      = ''
        self.instance.edt_debito.value   = ''
        self.instance.edt_credito.value  = ''

        self.page.pop_dialog()
        self.page.update()   


    async def limpar_venda(self, e):
        self.instance.btn_fechar_caixa.visible = True
        self.instance.btn_total.visible = False
        self.instance.btn_agenda.visible = True
        self.instance.btn_fechar_caixa.visible = True       
        self.instance.total = 0
        self.instance.text_client.value = ''
        self.instance.id_client = 0
        self.instance.comission = 0
        self.instance.id_prof = 0
        self.instance.area_dinheiro.value = ''
        self.instance.area_pix.value = ''
        self.instance.area_debito.value = ''
        self.instance.area_credito.value = ''
        self.instance.list_itens.cancelar()
        self.instance.list_profissionais.cancelar()   
        self.page.update()
        await self.instance.carregar_itens()     


    def handle_filter_itens(self, e):
        """Filtra a lista de cards com base no texto digitado."""
        search_term = self.instance.edtPesquisa.value.lower()
        
        # Percorre todos os cards na lista
        for card in self.instance.list_itens.controls:
            if isinstance(card, CustonCardItensVenda):
                client_name = card.name.lower()
                # Se o termo de busca estiver no nome do cliente, torna o card visível
                if search_term in client_name:
                    card.visible = True
                # Caso contrário, oculta o card
                else:
                    card.visible = False
        
        self.page.update()  


    def handle_fechar_pesquisa(self, e):
        self.instance.edtPesquisa.visible = False
        self.instance.edtPesquisa.value = ''    
        
        self.handle_filter_itens(e)
        
        self.instance.btn_pesquisa_produtos.visible = True
        self.instance.btn_pesquisa_clientes.visible = True
        self.instance.btn_fechar_pesquisa.visible = False        

        self.page.update()


    async def confirmar_fechamento_caixa(self, e):

        id_caixa = self.instance.id_caixa
        id_prof  = self.instance.id_prof
        
        _troco    = _parse_currency(self.instance.edt_troco_fechamento.value)
        _dinheiro = _parse_currency(self.instance.edt_dinheiro_fechamento.value)
        _pix      = _parse_currency(self.instance.edt_pix_fechamento.value)
        _debito   = _parse_currency(self.instance.edt_debito_fechamento.value)
        _credito  = _parse_currency(self.instance.edt_credito_fechamento.value)       

        await ProtectedApiCall(
            self.page, self.instance, self.model.fechar_caixa,
            id_caixa =id_caixa,
            pr_fechou=id_prof,
            troco    =_troco,
            dinheiro =_dinheiro,
            pix      =_pix,
            debito   =_debito,
            credito  =_credito,
            token    =self.instance.token             
        ).call_api_refresh_token()

        self.instance.status_caixa = "F"

        self.page.session.store.set("status_caixa", self.instance.status_caixa)   
        self.page.session.store.set("id_caixa", "0")   

        self.instance.btn_fechar_caixa.visible = False                    
        self.instance.btn_abrir_caixa.visible = True
        self.page.pop_dialog()
        self.page.update()


    async def fechar_caixa(self, e):
        if self.instance.id_prof == 0:
            self.dialog_profissional_caixa = CustonDialog(
                page = self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        content="Voltar",
                        on_click=lambda e: [
                            self.page.pop_dialog(),
                            self.page.update()
                        ]
                    )
                ]
            )
            
            self.page.show_dialog(self.dialog_profissional_caixa)
            self.page.update()
            return      
        
        self.instance.edt_troco_fechamento.value    = ''
        self.instance.edt_dinheiro_fechamento.value = ''
        self.instance.edt_pix_fechamento.value      = ''
        self.instance.edt_debito_fechamento.value   = ''
        self.instance.edt_credito_fechamento.value  = ''

        self.page.show_dialog(self.instance.modal_fechamento_caixa)
        self.page.update()
   

    def calculo_troco(self, e):
        dinheiro, pix, debito, credito = self._collect_payment_values()
        
        recebido = dinheiro + pix + debito + credito
        troco = recebido - self.instance.total

        self.instance.text_troco.value = f'Troco: R$ {formatar_moeda_brasileira(troco)}'
        self.page.update()        


    def preencher_valor_total(self, target, e):
        if self.instance.total > 0:
            all_fields = [
                self.instance.edt_dinheiro,
                self.instance.edt_pix,
                self.instance.edt_debito,
                self.instance.edt_credito
            ]

            for field in all_fields:
                if field == target:
                    field.value = f'{formatar_moeda_brasileira(self.instance.total)}'
                else:
                    field.value = ''

            self.calculo_troco(e)
            self.page.update()   


    async def confirmar_abertura_caixa(self, e):

        self.instance.status_caixa = 'A'    

        self.page.session.store.set("status_caixa", self.instance.status_caixa )    

        data_abertura = datetime.datetime.now().timestamp()

        if self.instance.edt_troco_inicial.value == '':
            troco_abertura = 0.00    
        else:
            troco_abertura = float(self.instance.edt_troco_inicial.value.replace(',','.'))

        pr_abriu = self.instance.id_prof

        response = await ProtectedApiCall(
            self.page, self.instance, self.model.AbrirCaixa, 
            id_loja=self.instance.id_loja,
            data_abertura=data_abertura,
            troco_abertura=troco_abertura,
            pr_abriu=pr_abriu,
            token=self.instance.token
        ).call_api_refresh_token()        

        if response.status_code == 200:
            self.instance.id_caixa = json.loads(response.content)["id_caixa"]
            self.page.session.store.set("id_caixa", self.instance.id_caixa)

            self.instance.btn_abrir_caixa.visible = False
            self.instance.btn_fechar_caixa.visible = True
            self.page.pop_dialog()
            self.page.update()
        else:
            self.instance.status_caixa = 'F'
            self.page.session.store.set("status_caixa", self.instance.status_caixa)
            self.dialog_erro_abrir_caixa = CustonDialog(
                page = self.page,
                title="Atenção",
                content="Erro ao abrir o caixa!",
                actions=[
                    ft.TextButton(
                        text="OK",
                        on_click=lambda e:[
                            self.page.pop_dialog(),
                            self.page.update()                            
                        ]

                    )
                ]
            )  

            self.page.show_dialog(self.dialog_erro_abrir_caixa)     
            self.page.update()
            return
        
    
    async def abrir_caixa(self):
        if self.instance.id_prof == 0:
            self.dialog_profissional_abrir_caixa = CustonDialog(
                page = self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        content="Voltar",
                        on_click=lambda e: [
                            self.page.pop_dialog(),
                            self.page.update()
                        ]
                    )
                ]
            )

            self.page.show_dialog(self.dialog_profissional_abrir_caixa)
            self.page.update()
            return

        self.page.show_dialog(self.instance.modal_caixa)
        self.page.update()  
        

    async def baixa_insumo(self, e):
        itens_insumo = []
        for card in self.instance.list_insumos.controls:
            if isinstance(card, CustonCardItensVenda) and card.quantidade > 0:
                
                id_insumo   = card.id
                quantidade  = card.quantidade                
                
                item_data = {
                    "id":id_insumo,
                    "quantidade":quantidade
                }

                itens_insumo.append(item_data)
            else:
                return
        await ProtectedApiCall(
            self.page, self.instance, self.model.UpdateInsumoData, 
            itens=itens_insumo,
            token=self.instance.token
        ).call_api_refresh_token()

        self.page.pop_dialog()
        self.page.show_dialog(self.instance.dialog_nota_cliente)
        self.page.update()
        

    async def get_insumos_data(self) -> list[dict]:         
        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetInsumosData, 
            id_loja=self.instance.id_loja, token=self.instance.token
        ).call_api_refresh_token()
           
        return json.loads(response.content)


    async def get_itens_data(self) -> list[dict]:         
        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetItensData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()
           
        return json.loads(response.content)["message"]


    async def get_profissionais_data(self) -> list[dict]:
        response = await ProtectedApiCall(
            self.page, self.instance, self.model_professional.getProfessionalData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()
            
        return json.loads(response.content)["message"]
       

    async def get_clientes_data(self) -> list[dict]:
        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetClientsData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()        
            
        return json.loads(response.content)["message"]


    async def itens_venda(self):
        itens_venda = []
        for card in self.instance.list_itens.controls:
            if isinstance(card, CustonCardItensVenda) and card.quantidade > 0:
                item_data = {
                    "id_produto":       card.id,
                    "quantidade":       card.quantidade,
                    "valor_unitario":   card.valor,
                    "valor_total":      card.total,
                    "comissionado":     card.comissionado,       
                    "ident_serv":       card.ident_serv           
                }
                itens_venda.append(item_data)

                if card.ident_serv == 1:
                    self.instance.ident_serv = 1

        payload = {
            "itens": itens_venda
        }

        return payload        


    async def recebimento(self, e):
        if not self.instance.id_prof:
            self.dialog = CustonDialog(
                self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        content="Voltar",
                        on_click=lambda e:[
                            self.page.pop_dialog(),
                            self.page.update()
                        ]
                    )
                ]
            )
            self.page.show_dialog(self.dialog)
            self.page.update()
            return
        
        self.instance.text_total.value = f'Total: R$ {formatar_moeda_brasileira(self.instance.total)}'
        self.instance.text_troco.value = 'Troco: R$ 0,00'        

        dinheiro, pix, debito, credito = self._collect_payment_values()

        recebido = dinheiro + pix + debito + credito
        troco = recebido - self.instance.total

        if recebido < self.instance.total:
            snackbar = ft.SnackBar(
                open=True,
                bgcolor=AppColors.GRAY_DARK,
                content=ft.Text(
                    value="O valor recebido é menor que o total da venda!", 
                    size=20,
                    weight=ft.FontWeight.BOLD, 
                    color=AppColors.GRAY_LIGHT,
                ),
            )
            self.page.show_dialog(snackbar)
            self.page.update()
            return
        
        itens = json.dumps(await self.itens_venda())

        response = await ProtectedApiCall(
            self.page, 
            self.instance, 
            self.model.receber_venda,
            token=self.instance.token,
            id_loja=self.instance.id_loja,
            id_prof=self.instance.id_prof,
            comission=self.instance.comission,
            id_client=self.instance.id_client,
            id_caixa=self.instance.id_caixa,
            total=self.instance.total,
            din=dinheiro,
            pix=pix,
            deb=debito,
            cred=credito,   
            troco=troco,         
            itens=itens
        ).call_api_refresh_token()

        #self.page.pop_dialog()

        #if self.instance.ident_serv == 1:
            #self.page.show_dialog(self.instance.dialog_insumo)
        #else:
        if response.status_code == 200:
            await self.limpar_venda(e)
        else:
            print(response.content)
            snackbar = ft.SnackBar(
                open=True,
                bgcolor=AppColors.GRAY_DARK,
                content=ft.Text(
                    value="Houve um erro ao registrar a venda!", 
                    size=20,
                    weight=ft.FontWeight.BOLD, 
                    color=AppColors.GRAY_LIGHT,
                ),                
            )
            self.page.show_dialog(snackbar)
            self.page.update()
                

        #self.page.update()


    async def fechar_dialogo_nota_clientes(self, e):
        self.page.pop_dialog()
        self.page.update()
        await self.limpar_venda(e)


    def abrir_dialogo_nota_clientes(self, e):
        if not self.instance.id_client == 0:
            self.page.show_dialog(self.instance.dialog_nota_cliente)
            self.page.update()


    async def fechar_modal_nota_clientes(self, e):
        self.page.pop_dialog() 
        self.page.update() 
        await self.limpar_venda(e)


    async def fechar_dialogo_insumos(self, e):
        self.page.pop_dialog()
        self.page.update() 
        self.abrir_dialogo_nota_clientes(e)        


    async def abrir_modal_insumos(self, e):
        await self.listInsumos()
        self.page.pop_dialog()
        self.page.show_dialog(self.instance.modal_insumos)
        self.page.update()


    def fechar_modal_insumos(self, e):
        self.page.pop_dialog()
        self.page.update() 
        self.abrir_dialogo_nota_clientes(e)   


    async def handler_logout(self):
        self.page.session.store.set("token",        '')
        self.page.session.store.set("r_token",      '')
        self.page.session.store.set("id",           '')
        self.page.session.store.set("status_caixa", '')
        self.page.session.store.set("slug",         '')

        # Remove tokens persistidos de forma segura para desabilitar o auto-login
        _storage = SecureStorage()
        for key in ("r_token", "id", "google_refresh_token", "login_method"):
            await _storage.remove(key)

        await self.page.push_route("/")    
    


