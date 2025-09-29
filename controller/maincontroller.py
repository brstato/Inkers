import flet as ft
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
from model.loginmodel import LoginModel
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
import datetime


class MainController:
    def __init__(self, page:ft.Page, instance):
        
        self.instance = instance
        self.page = page
        self.model = mainModel()
        self.model_professional = ProfessionlModel()
        self.model_clientes = ClientModel()


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
        self.instance.id_loja      = await self.page.client_storage.get_async("id"     )
        self.instance.token        = await self.page.client_storage.get_async("token"  )
        self.instance.r_token      = await self.page.client_storage.get_async("r_token")   
        self.instance.status_caixa = await self.page.client_storage.get_async("status_caixa")

        self.instance.progressRing.visible = True
        self.page.update()

        await self.listPorfissionais()
        await self.listItens()
        await self.listClientes()

        self.instance.progressRing.visible = False
        self.page.update()         


    def exibir_edt_pesquisa_produtos(self, e):
        self.instance.edtPesquisa.visible = True
        self.instance.btn_pesquisa_produtos.visible = False
        self.instance.btn_pesquisa_clientes.visible = False
        self.instance.btn_fechar_pesquisa.visible = True
        self.page.update()  


    def exibir_lista_clientes(self, e):
        self.page.open(self.instance.modal_pesquisa_clientes)
        self.page.update()        


    def cancelar_modal_pesquisa_clientes(self, e):
        self.instance.id_client = 0
        self.instance.text_client.visible = False
        self.page.close(self.instance.modal_pesquisa_clientes)
        self.page.update()           


    def fechar_modal_pequisa_clientes(self):
        self.page.close(self.instance.modal_pesquisa_clientes)
        self.page.update()


    def cancelar_receber_venda(self):
        self.instance.edt_dinheiro.value = ''
        self.instance.edt_pix.value = ''
        self.instance.edt_debito.value = ''
        self.instance.edt_credito.value = ''

        self.page.close(self.modal_recebimento)
        self.page.update()   


    def limpar_venda(self):
        self.instance.text_client.value = ''
        self.instance.id_client = 0
        self.instance.id_prof = 0
        self.instance.list_itens.cancelar()
        self.instance.list_profissionais.cancelar()        


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


    async def fechar_caixa(self, e):
        self.instance.status_caixa = 'F'
        await self.page.client_storage.set_async("status_caixa", self.instance.status_caixa)
        self.page.open(self.instance.modal_caixa)
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
                    field.value = f'{formatar_moeda_brasileira(self.total)}'
                else:
                    field.value = ''

            self.calculo_troco(e)
            self.page.update()   


    async def abrir_caixa(self):
        if self.instance.id_prof == 0:
            self.dialog_profissional_abrir_caixa = CustonDialog(
                page = self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        text="Voltar",
                        on_click=lambda e: [
                            self.page.close(self.dialog_profissional_abrir_caixa),
                            self.page.update()
                        ]
                    )
                ]
            )
            self.page.open(self.dialog_profissional_abrir_caixa)
            self.page.update()
            return
        
        self.instance.status_caixa = 'A'        

        data_abertura = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

        if self.instance.edt_troco_inicial.value == '':
            troco_abertura = 0.00    
        else:
            troco_abertura = float(self.instance.edt_troco_inicial.value.replace(',','.'))

        pr_abriu = self.instance.id_prof
        id_loja = self.instance.id_loja

        self.model.AbrirCaixa(
            id_loja=id_loja,
            data_abertura=data_abertura,
            troco_abertura=troco_abertura,
            pr_abriu=pr_abriu
        )

        self.page.close(self.instance.modal_caixa)
        self.page.update()
        await self.page.client_storage.set("status_caixa", "A")
        self.listItens()


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
            comissao     = item["comissao"          ]

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
                comissao=comissao,
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
            name      = item["name"]
            id_prof   = item["id"  ]

            card = CustonCardProfessional(
                instance=self.instance,
                name=name,
                id=id_prof,
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


    async def recebimento(self):
        if self.instance.id_prof == 0:
            self.dialog = CustonDialog(
                self.page,
                title="Atenção",
                content="Por favor selecione o profissional!",
                actions=[
                    ft.TextButton(
                        text="Voltar",
                        on_click=lambda e:[
                            self.page.close(self.dialog),
                            self.page.update()
                        ]
                    )
                ]
            )
            self.page.open(self.dialog)
            self.page.update()
            return
        
        self.instance.text_total.value = f'Total: R$ {formatar_moeda_brasileira(self.total)}'
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
            self.page.open(snackbar)
            self.page.update()
            return

        self.instance.limpar_venda()
        self.page.close(self.instance.modal_recebimento)
        self.page.update()