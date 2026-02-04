import flet as ft
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
from model.professionalmodel import ProfessionlModel
from model.clientmodel import ClientModel
from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
from model.mainmodel import mainModel
from utils.formatcurr import formatar_moeda_brasileira, _parse_currency
import json
from view.controls.custoncardsimples import CustonCardSimples
from view.controls.colors import AppColors
from controller.call_api import ProtectedApiCall
from view.controls.custondialog import CustonDialog
from model.accountmodel import AccountModel
from urllib.parse import quote, urlparse
import datetime
from model.zapmodel import ZapModel
import asyncio


class MainController:
    def __init__(self, page:ft.Page, instance):
        
        self.instance = instance
        self.page = page
        self.model = mainModel()
        self.model_professional = ProfessionlModel()
        self.model_clientes = ClientModel()
        self.account_model = AccountModel()
        self.zap_model = ZapModel()


    async def show_drawer(self):
        await self.page.show_drawer()


    async def create_link_anamnese(self, e):
        account_name = quote(self.instance.account_name)
        parsed_url = urlparse(self.page.url)
        base_domain = f"https://{parsed_url.netloc}"
        base_url = f"{base_domain}/anamnese/{account_name}/{self.instance.account_tel}"
        await ft.Clipboard().set(base_url)
        await self.page.close_drawer()
        self.page.show_dialog(ft.SnackBar(content=ft.Text("Link copiado para a área de transferência!")))
        self.page.update()


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

            self.page.clipboard(par_code)

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
            self.page, self.instance, self.zap_model.GetConnectionZap,
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
                self.page, self.instance, self.account_model.getAccountData,
                id=self.instance.id_loja,
                token=self.instance.token
            ).call_api_refresh_token()
            
            data = json.loads(response.content)

            self.instance.account_name = data["nome"        ]
            self.instance.account_tel  = data["telefone"    ]
            self.instance.zap_instance = data["zap_instance"]

            await ft.SharedPreferences().set("zap_instance", self.instance.zap_instance)

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

        await ft.SharedPreferences().set("status_caixa", self.instance.status_caixa)
        await ft.SharedPreferences().set("id_caixa", str(self.instance.id_caixa))


    def _collect_payment_values(self):
        dinheiro = _parse_currency(self.instance.edt_dinheiro.value)
        pix      = _parse_currency(self.instance.edt_pix.value)
        debito   = _parse_currency(self.instance.edt_debito.value)
        credito  = _parse_currency(self.instance.edt_credito.value)
        
        return dinheiro, pix, debito, credito


    def filter_clients(self, e):
        search_term = self.instance.edtPesquisaClientes.value.lower()
        
        # Percorre todos os cards na lista
        for card in self.instance.list_clients.controls:
            if isinstance(card, CustonCardSimples):
                client_name = card.title.lower()
                # Se o termo de busca estiver no nome do cliente, torna o card visível
                if search_term in client_name:
                    card.visible = True
                # Caso contrário, oculta o card
                else:
                    card.visible = False
        
        self.page.update()          


    def on_exit_edt_pesquisa(self, e):
        self.instance.edtPesquisa.border_color=AppColors.GRAY_MED3
        self.page.update()   


    def on_enter_edt_pesquisa(self, e):
        self.instance.edtPesquisa.border_color=AppColors.ORANGE_DARK
        self.page.update()


    async def get_Data(self):
        try:
            try:
                self.instance.id_loja = await asyncio.wait_for(ft.SharedPreferences().get("id"), timeout=5.0)
                self.instance.token = await asyncio.wait_for(ft.SharedPreferences().get("token"), timeout=5.0)
                self.instance.r_token = await asyncio.wait_for(ft.SharedPreferences().get("r_token"), timeout=5.0)
            except asyncio.TimeoutError:
                self.instance.id_loja = None
            except Exception as e:
                print(f"DEBUG: Erro ao obter id_loja: {e}")
                self.instance.id_loja = None
                self.instance.token = None
            
            if not self.instance.token or not self.instance.id_loja:    
                await self.page.push_route("/")
                return
            
            await self.get_status_caixa()

            if self.instance.total == 0:            
                self.instance.btn_total.visible = False
                self.instance.btn_fechar_caixa.visible = True  

            if self.instance.status_caixa == 'F':
                self.instance.btn_abrir_caixa.visible = True
                self.instance.btn_fechar_caixa.visible = False

            elif self.instance.status_caixa == 'A':   
                self.instance.btn_fechar_caixa.visible = True
                self.instance.btn_abrir_caixa.visible = False        

            self.instance.progressRing.visible = True
            self.page.update()

            await self.get_account_data()
            await self.listPorfissionais()
            await self.listItens()
            await self.listClientes()
            await self.listInsumos()
            await self.get_connection_zap()

            self.instance.progressRing.visible = False
            self.page.update()
        except Exception as ex:
            print(f"ERROR em get_Data: {ex}")
            import traceback
            traceback.print_exc()         


    def exibir_edt_pesquisa_produtos(self, e):
        self.instance.edtPesquisa.visible = True
        self.instance.btn_pesquisa_produtos.visible = False
        self.instance.btn_pesquisa_clientes.visible = False
        self.instance.btn_fechar_pesquisa.visible = True
        self.page.update()  


    def exibir_lista_clientes(self, e):
        self.page.show_dialog(self.instance.modal_pesquisa_clientes)
        self.instance.btn_agenda.visible = False
        self.instance.btn_cancelar.visible = True
        self.instance.btn_fechar_caixa.visible = False

        self.page.update()        


    def cancelar_modal_pesquisa_clientes(self, e):
        self.instance.id_client = 0
        self.instance.text_client.visible = False
        self.page.pop_dialog()
        self.page.update()           


    async def confirmar_pequisa_clientes(self, e):
        self.page.pop_dialog()
        self.page.update()


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
        await self.listItens()     


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

        await ft.SharedPreferences().set("status_caixa", self.instance.status_caixa)   
        await ft.SharedPreferences().set("id_caixa", "0")   

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

        await ft.SharedPreferences().set("status_caixa", self.instance.status_caixa )    

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
            await ft.SharedPreferences().set("id_caixa", self.instance.id_caixa)

            self.instance.btn_abrir_caixa.visible = False
            self.instance.btn_fechar_caixa.visible = True
            self.page.pop_dialog()
            self.page.update()
        else:
            self.instance.status_caixa = 'F'
            await ft.SharedPreferences().set("status_caixa", self.instance.status_caixa)
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

        await ProtectedApiCall(
            self.page, self.instance, self.model.UpdateInsumoData, 
            itens=itens_insumo,
            token=self.instance.token
        ).call_api_refresh_token()

        self.page.pop_dialog()
        self.page.show_dialog(self.instance.dialog_nota_cliente)
        self.page.update()
        #await self.limpar_venda(e)
        #await self.abrir_dialogo_nota_clientes(e)
        

    async def listInsumos(self):         
        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetInsumosData, 
            id_loja=self.instance.id_loja, token=self.instance.token
        ).call_api_refresh_token()
           
        array = json.loads(response.content)

        self.instance.list_insumos.controls.clear()

        for item in array:
            id_prod      = item["id"     ]
            name         = item["nome"   ]
            estoque      = item["estoque"]
            valor        = item["valor"  ]

            card = CustonCardItensVenda(
                page=self.page,
                width=280,
                instance=self.instance,
                icon=None,
                name=name,
                id=id_prod,
                estoque=estoque,
                valor=valor,
                tap=self.instance.list_itens.on_card_selected,
                on_change=self.instance.list_insumos.recalculate_total
            )

            self.instance.list_insumos.controls.append(card) 
            
        self.page.update()  


    async def listItens(self):         
        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetItensData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()
           
        array = json.loads(response.content)["message"]

        self.instance.list_itens.controls.clear()

        for item in array:
            id_prod      = item["id"                ]
            name         = item["nome"              ]
            ident        = item["ident_serv"        ]
            estoque      = item["quantidade_estoque"]
            valor        = item["valor_venda"       ]
            inf_valor    = item["inf_valor"         ]
            comissionado = item["comissionado"      ]

            if ident == 0:
                icon = ft.Icons.CATEGORY
            elif ident == 1:
                icon = ft.Icons.MISCELLANEOUS_SERVICES

            card = CustonCardItensVenda(
                ident_serv=ident,
                page=self.page,
                width=self.instance.page.width,
                instance=self.instance,
                icon=icon,
                name=name,
                id=id_prod,
                estoque=estoque,
                valor=valor,
                inf_valor=inf_valor,
                comissionado=comissionado,
                tap=self.instance.list_itens.on_card_selected,
                on_change=self.instance.list_itens.recalculate_total
            )

            self.instance.list_itens.controls.append(card) 
            
        self.page.update()  


    async def listPorfissionais(self):

        response = await ProtectedApiCall(
            self.page, self.instance, self.model_professional.getProfessionalData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()
            
        array = json.loads(response.content)["message"]

        self.instance.list_profissionais.controls.clear()

        for item in array:
            name      = item["name"    ]
            id_prof   = item["id"      ]
            comission = item["comissao"]

            if len(array) == 1:
                self.instance.id_prof = id_prof
                self.instance.comission = comission

            card = CustonCardProfessional(
                instance=self.instance,
                name=name,
                id=id_prof,
                comission=comission,
                tap=self.instance.list_profissionais.on_card_selected
            )

            self.instance.list_profissionais.controls.append(card) 
        
        self.page.update()
       

    async def listClientes(self):

        response = await ProtectedApiCall(
            self.page, self.instance, self.model.GetClientsData, 
            id=self.instance.id_loja, token=self.instance.token).call_api_refresh_token()        
            
        array = json.loads(response.content)["message"]

        self.instance.list_clients.controls.clear()

        for item in array:
            name      = item["nome"]
            id_client = item["id"  ]

            card = CustonCardSimples(
                page=self.page,
                title=name,
                id=id_client,
                tap=self.instance.list_clients.on_card_selected,
                instance=self.instance
            )

            self.instance.list_clients.controls.append(card) 
        
        self.page.update()


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
        if self.instance.id_prof == 0:
            self.dialog = CustonDialog(
                self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        text="Voltar",
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

        await ProtectedApiCall(
            self.page, self.instance, self.model.receber_venda,
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

        self.page.pop_dialog()

        if self.instance.ident_serv == 1:
            self.page.show_dialog(self.instance.dialog_insumo)
        else:
            await self.limpar_venda(e)

        self.page.update()


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
        await self.abrir_dialogo_nota_clientes(e)        


    async def abrir_modal_insumos(self, e):
        self.page.pop_dialog()
        self.page.show_dialog(self.instance.modal_insumos)
        self.page.update()


    def fechar_modal_insumos(self, e):
        self.page.pop_dialog()
        self.page.update() 
        self.abrir_dialogo_nota_clientes(e)   


    async def handler_logout(self):
        await asyncio.wait_for(ft.SharedPreferences().set("token",        ''), 5), 
        await asyncio.wait_for(ft.SharedPreferences().set("r_token",      ''), 5), 
        await asyncio.wait_for(ft.SharedPreferences().set("id",           ''), 5),
        await asyncio.wait_for(ft.SharedPreferences().set("status_caixa", ''), 5),
        await self.page.push_route("/")    
    


