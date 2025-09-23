import flet as ft
from view.controls.colors import AppColors
from view.controls.controls_mainview.custonlistprofessionais import CustonListProfessional
from view.controls.custonprogressring import CustonProgressRing
from controller.maincontroller import MainController
from view.controls.controls_mainview.custonlistitensvenda import CustonList
from view.controls.controls_mainview.custonlistclients import CustonList as CL
from view.controls.formatcurr import formatar_moeda_brasileira
from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
from view.controls.custonmodalview import CustonModalView
from view.controls.custoncardsimples import CustonCardSimples
from view.controls.custontextfield import CustomTextField
from view.controls.custondialog import CustonDialog

class MainView(ft.View):
    def __init__(
            self, 
            page: ft.Page
        ):
        super().__init__(route="/main", bgcolor=AppColors.BACKGROUND_DARK,)

        self.id_loja:str = ''
        self.token:str   = ''
        self.r_token:str = ''

        self.client:str = ''
        self.id_client:int = 0

        self.id_prof:int=0

        self.total:float=0

        self.page = page              

        self.bgcolor = AppColors.BACKGROUND_DARK

        self.controller = MainController(self.page, self)

        self.list_profissionais = CustonListProfessional(self.page)
        
        self.progressRing = CustonProgressRing()
        
        self.list_itens = CustonList(self.page, self)

        self.list_clients = CL(self.page)

        self.text_total = ft.Text(
            color=AppColors.ORANGE_DARK,
            size=20
        )

        self.text_troco = ft.Text(
            color=AppColors.GRAY_LIGHT2,
            size=16
        )        

        self.edt_dinheiro = CustomTextField(
            label="Dinheiro",
            chars=r"^[0-9,]*$",
            on_change=self.calculo_troco
        )

        self.edt_pix = CustomTextField(
            label="Pix",
            chars=r"^[0-9,]*$",
            on_change=self.calculo_troco
        )        

        self.edt_debito = CustomTextField(
            label="Debito",
            chars=r"^[0-9,]*$",
            on_change=self.calculo_troco
        )    

        self.edt_credito = CustomTextField(
            label="Credito",
            chars=r"^[0-9,]*$",
            on_change=self.calculo_troco
        )          

        self.modal_recebimento = CustonModalView(
            height=400,
            page=self.page,
            text_button_1="Receber",
            callback=None,
            callback2=lambda e: self.cancelar_receber_venda(e),
            controls=[
                self.text_total,
                self.text_troco,
                self.edt_dinheiro,
                self.edt_pix,
                self.edt_debito,
                self.edt_credito
            ]    
        )

        self.text_client = ft.Text(
            value=self.client,
            color=AppColors.ORANGE_DARK,
            visible=False,
            size=self.page.width / 2,
        )

        self.edtPesquisaClientes = ft.TextField(
            width=300,
            color=AppColors.GRAY_LIGHT2,
            label="Pesquisar clientes por nome...",
            on_change=self.filter_clients, # Função que fará a mágica
            border_color=AppColors.ORANGE_DARK,
            border=ft.InputBorder.UNDERLINE,  
        ) 

        self.modal_pesquisa_clientes = CustonModalView(
            height=650,
            page=self.page,
            callback=self.fechar_modal_pequisa_clientes,
            callback2=self.cancelar_modal_pesquisa_clientes,
            controls=[
                self.edtPesquisaClientes,
                self.list_clients
            ]
        )

        self.edtPesquisa = ft.TextField(
            width=self.page.width / 1.2,
            visible=False,
            color=AppColors.GRAY_LIGHT2,
            label="Pesquisar produto ou serviço por nome...",
            on_change=self.filter_itens, # Função que fará a mágica
            border_color=AppColors.GRAY_MED3,
            border=ft.InputBorder.UNDERLINE,
            height=40,
            content_padding=10,    
            on_click=lambda e: self.on_enter_edt_pesquisa(e),
            on_blur=lambda e: self.on_exit_edt_pesquisa(e)
        )        

        self.btn_pesquisa_produtos = ft.ElevatedButton(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            text='Produtos',
            elevation=5,            
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),             
            on_click=lambda e: self.exibir_edt_pesquisa_produtos(e)
        )

        self.btn_pesquisa_clientes = ft.ElevatedButton(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            text='Clientes',
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),     
            on_click=lambda e: self.exibir_lista_clientes(e)        
        )

        self.btn_fechar_pesquisa = ft.IconButton(
            alignment=ft.alignment.center_right,
            icon=ft.Icons.CLOSE,
            icon_color=AppColors.ORANGE_DARK,
            visible=False,     
            on_click=lambda e: self.fechar_pesquisa(e)                   
        )

        self.container_pesquisa = ft.Container(
            content=ft.Row(
            controls=[
                ft.Stack(
                    controls=[
                        self.btn_pesquisa_produtos ,
                        self.edtPesquisa,
                    ]
                ),
                ft.Container(expand=True),
                self.btn_pesquisa_clientes,
                self.btn_fechar_pesquisa,
                ]
            ),
        )

        self.controls=[
            ft.Container(
                
                bgcolor=AppColors.GRAY_DARK,
                height=100,
                border_radius=ft.border_radius.all(10),
                padding=ft.padding.all(10),
                content=self.list_profissionais,
            ), 
            #self.edtCliente,
            self.container_pesquisa,
            self.list_itens,
        ]

        self.btn_total = ft.ElevatedButton(
            text=f'Receber: R$ {formatar_moeda_brasileira(self.total)}', 
            color=AppColors.GRAY_LIGHT3,
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),            
            on_click=lambda e:self.receber_venda(e)
        ) 

        self.drawer = ft.NavigationDrawer(
            bgcolor=AppColors.GRAY_DARK,
            elevation=10,
            controls=[
                ft.Container(                    
                    content=ft.Column(                        
                        controls=[
                            ft.ElevatedButton(
                                text="Minha conta",
                                bgcolor=AppColors.GRAY_DARK,
                                color=AppColors.WHITE,
                                elevation=5,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, AppColors.GRAY_LIGHT),
                                    color=AppColors.GRAY_LIGHT,
                                ),
                                width=250,
                                height=45,
                                on_click=lambda e: self.page.go("/account"),
                            ),
                            ft.ElevatedButton(
                                text="Profissionais",
                                bgcolor=AppColors.GRAY_DARK,
                                color=AppColors.WHITE,
                                elevation=5,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, AppColors.GRAY_LIGHT),
                                    color=AppColors.GRAY_LIGHT,
                                ),
                                width=250,
                                height=45,
                                on_click=lambda e: self.page.go("/professional"),
                            ),   
                            ft.ElevatedButton(
                                text="Produtos",
                                bgcolor=AppColors.GRAY_DARK,
                                color=AppColors.WHITE,
                                elevation=5,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, AppColors.GRAY_LIGHT),
                                    color=AppColors.GRAY_LIGHT,
                                ),
                                width=250,
                                height=45,
                                on_click=lambda e: self.page.go("/product"),
                            ),    
                            ft.ElevatedButton(
                                text="Serviços",
                                bgcolor=AppColors.GRAY_DARK,
                                color=AppColors.WHITE,
                                elevation=5,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, AppColors.GRAY_LIGHT),
                                    color=AppColors.GRAY_LIGHT,
                                ),
                                width=250,
                                height=45,
                                on_click=lambda e: self.page.go("/services"),
                            ),                                                                               
                            ft.ElevatedButton(
                                text="Clientes",
                                bgcolor=AppColors.GRAY_DARK,
                                color=AppColors.WHITE,
                                elevation=5,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, AppColors.GRAY_LIGHT),
                                    color=AppColors.GRAY_LIGHT,
                                ),
                                width=250,
                                height=45,
                                on_click=lambda e: self.page.go("/clients"),
                            ),                           
                        ],
                    ),
                    padding=ft.padding.all(20),
                ),
            ],
        )

        self.btn_cancelar = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=AppColors.GRAY_LIGHT3,
            visible=False,
            on_click=lambda e: self.list_itens.cancelar()
        )

        self.bottom_appbar = ft.BottomAppBar(
            height=60,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=lambda e: self.page.open(self.drawer)
                    ),
                    ft.Container(expand=True),
                    self.text_client,
                    self.btn_total,
                    self.btn_cancelar,
                ],
            ),
        )    

    
    def calculo_troco(self, e):
        dinheiro:float = 0.00
        pix:float = 0.00
        debito:float = 0.00
        credito:float = 0.00

        if self.edt_dinheiro.value != '':
            dinheiro = float(self.edt_dinheiro.value.replace(',','.'))
        else:
            dinheiro = 0.00  

        if self.edt_pix.value != '':
            pix = float(self.edt_pix.value.replace(',','.'))
        else:    
            pix = 0.00

        if self.edt_debito.value != '':
            debito = float(self.edt_debito.value.replace(',','.'))
        else:
            debito = 0.00

        if self.edt_credito.value != '':
            credito = float(self.edt_credito.value.replace(',','.'))
        else: 
            credito = 0.00

        recebido = dinheiro + pix + debito + credito
        troco = recebido - self.total

        self.text_troco.value = f'Troco: R$ {formatar_moeda_brasileira(troco)}'
        self.page.update()
        
            



    def cancelar_receber_venda(self, e):
        self.edt_dinheiro.value = ''
        self.edt_pix.value = ''
        self.edt_debito.value = ''
        self.edt_credito.value = ''

        self.page.close(self.modal_recebimento)
        self.page.update()        

    
    def receber_venda(self, e):        
        if self.total > 0:
            if self.id_prof == 0:
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

            self.text_total.value = f'Total: R$ {formatar_moeda_brasileira(self.total)}'
            self.text_troco.value = 'Troco: R$ 0,00'
            self.page.open(self.modal_recebimento)
            self.page.update()


    async def fechar_modal_pequisa_clientes(self, e):
        self.page.close(self.modal_pesquisa_clientes)
        self.page.update()


    def cancelar_modal_pesquisa_clientes(self, e):
        self.id_client = 0
        self.text_client.visible = False
        self.page.close(self.modal_pesquisa_clientes)
        self.page.update()            


    def did_mount(self):
        self.page.run_task(self.get_Data)


    def exibir_lista_clientes(self, e):
        self.page.open(self.modal_pesquisa_clientes)
        self.page.update()


    def exibir_edt_pesquisa_produtos(self, e):
        self.edtPesquisa.visible = True
        self.btn_pesquisa_produtos.visible = False
        self.btn_pesquisa_clientes.visible = False
        self.btn_fechar_pesquisa.visible = True
        self.page.update() 


    def fechar_pesquisa(self, e):
        self.edtPesquisa.visible = False
        self.edtPesquisa.value = ''
        self.filter_itens(e)
        
        self.btn_pesquisa_produtos.visible = True
        self.btn_pesquisa_clientes.visible = True
        self.btn_fechar_pesquisa.visible = False
        
        self.page.update()             


    async def get_Data(self):
        self.id_loja: str = await self.page.client_storage.get_async("id"     )
        self.token:   str = await self.page.client_storage.get_async("token"  )
        self.r_token: str = await self.page.client_storage.get_async("r_token")   

        self.progressRing.visible = True
        self.page.update()

        await self.controller.listPorfissionais()
        await self.controller.listItens()
        await self.controller.listClientes()

        self.progressRing.visible = False
        self.page.update()        


    def on_enter_edt_pesquisa(self, e):
        self.edtPesquisa.border_color=AppColors.ORANGE_DARK
        self.page.update()


    def on_exit_edt_pesquisa(self, e):
        self.edtPesquisa.border_color=AppColors.GRAY_MED3
        self.page.update()   


    def filter_itens(self, e):
        """Filtra a lista de cards com base no texto digitado."""
        search_term = self.edtPesquisa.value.lower()
        
        # Percorre todos os cards na lista
        for card in self.list_itens.controls:
            if isinstance(card, CustonCardItensVenda):
                client_name = card.name.lower()
                # Se o termo de busca estiver no nome do cliente, torna o card visível
                if search_term in client_name:
                    card.visible = True
                # Caso contrário, oculta o card
                else:
                    card.visible = False
        
        self.page.update()    


    def filter_clients(self, e):
        """Filtra a lista de cards com base no texto digitado."""
        search_term = self.edtPesquisaClientes.value.lower()
        
        # Percorre todos os cards na lista
        for card in self.list_clients.controls:
            if isinstance(card, CustonCardSimples):
                client_name = card.title.lower()
                # Se o termo de busca estiver no nome do cliente, torna o card visível
                if search_term in client_name:
                    card.visible = True
                # Caso contrário, oculta o card
                else:
                    card.visible = False
        
        self.page.update()           