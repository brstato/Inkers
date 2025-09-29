import flet as ft
from view.controls.colors import AppColors
from view.controls.controls_mainview.custonlistprofessionais import CustonListProfessional
from view.controls.custonprogressring import CustonProgressRing
from controller.maincontroller import MainController
from view.controls.controls_mainview.custonlistitensvenda import CustonList
from view.controls.controls_mainview.custonlistclients import CustonList as CL
from utils.formatcurr import formatar_moeda_brasileira
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
        
        self.page = page

        self.controller = MainController(self.page, self)

        self.id_loja:str = ''
        self.token:str   = ''
        self.r_token:str = ''

        self.client:str = ''

        self.status_caixa:str = 'F'

        self.id_client:int = 0

        self.id_prof:int=0

        self.total:float=0              

        self.bgcolor = AppColors.BACKGROUND_DARK

        self.btn_fechar_caixa = ft.ElevatedButton(
            visible=False,
            text='Fechar caixa', 
            color=AppColors.GRAY_LIGHT3,
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),            
            on_click=self.controller.fechar_caixa
        )         

        self.edt_troco_inicial = CustomTextField(
            label="Troco inicial",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        ) 

        self.modal_caixa = CustonModalView(
            self.page,
            callback=lambda e:self.controller.abrir_caixa(),
            callback2=lambda e:[self.page.close(self.modal_caixa), self.page.update()],
            text_button_1="Abrir caixa",
            height=150,
            controls=[
               self.edt_troco_inicial
            ]
        )

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
            on_change=self.controller.calculo_troco
        )

        self.area_dinheiro = ft.Row(
            controls=[
                self.edt_dinheiro,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    offset=ft.Offset(x=-1.2, y=0),
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_dinheiro, e)
                )
            ]
        )       

        self.edt_pix = CustomTextField(
            label="Pix",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )        

        self.area_pix = ft.Row(
            controls=[
                self.edt_pix,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    offset=ft.Offset(x=-1.2, y=0),
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_pix, e)
                )
            ]
        ) 

        self.edt_debito = CustomTextField(
            label="Debito",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )    

        self.area_debito = ft.Row(
            controls=[
                self.edt_debito,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    offset=ft.Offset(x=-1.2, y=0),
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_debito, e)
                )
            ]
        ) 

        self.edt_credito = CustomTextField(
            label="Credito",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )          

        self.area_credito = ft.Row(
            controls=[
                self.edt_credito,
                ft.IconButton(
                    alignment=ft.alignment.center_right,
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    offset=ft.Offset(x=-1.2, y=0),
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_credito, e)
                )
            ]
        ) 

        self.modal_recebimento = CustonModalView(
            height=400,
            page=self.page,
            text_button_1="Receber",
            callback=lambda e:self.page.run_task(self.controller.recebimento),
            callback2=self.controller.cancelar_receber_venda,
            controls=[
                self.text_total,
                self.text_troco,
                self.area_dinheiro,
                self.area_pix,
                self.area_debito,
                self.area_credito
            ]    
        )

        self.text_client = ft.Text(
            value=self.client,
            color=AppColors.ORANGE_DARK,
            visible=False,
            #width=self.page.width / 2,
        )

        self.edtPesquisaClientes = ft.TextField(
            width=300,
            color=AppColors.GRAY_LIGHT2,
            label="Pesquisar clientes por nome...",
            on_change=self.controller.filter_clients, # Função que fará a mágica
            border_color=AppColors.ORANGE_DARK,
            border=ft.InputBorder.UNDERLINE,  
        ) 

        self.modal_pesquisa_clientes = CustonModalView(
            height=650,
            page=self.page,
            callback=self.controller.fechar_modal_pequisa_clientes,
            callback2=self.controller.cancelar_modal_pesquisa_clientes,
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
            on_change=self.controller.handle_filter_itens,
            border_color=AppColors.GRAY_MED3,
            border=ft.InputBorder.UNDERLINE,
            height=40,
            content_padding=10,    
            on_click=lambda e: self.controller.on_enter_edt_pesquisa(e),
            on_blur=lambda e: self.controlleron_exit_edt_pesquisa(e)
        )        

        self.btn_pesquisa_produtos = ft.ElevatedButton(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            text='Produtos',
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,            
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),             
            on_click=lambda e: self.controller.exibir_edt_pesquisa_produtos(e)
        )

        self.btn_pesquisa_clientes = ft.ElevatedButton(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            text='Clientes',
            elevation=5,
            bgcolor=AppColors.GRAY_DARK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),     
            on_click=lambda e: self.controller.exibir_lista_clientes(e)        
        )

        self.btn_fechar_pesquisa = ft.IconButton(
            alignment=ft.alignment.center_right,
            icon=ft.Icons.CLOSE,
            icon_color=AppColors.ORANGE_DARK,
            visible=False,     
            on_click=lambda e: self.controller.handle_fechar_pesquisa(e)                   
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
            on_click=self.page.run_task(self.controller.recebimento)
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
                            ft.ElevatedButton(
                                text="Sair",
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
                                on_click=lambda e: [
                                    self.page.client_storage.set("token", ''), 
                                    self.page.client_storage.set("r_token", ''), 
                                    self.page.client_storage.set("status_caixa", ''),
                                    self.page.go("/")
                                ],
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
            on_click=lambda e: self.controller.limpar_venda()
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
                    self.btn_fechar_caixa,
                ],
            ),
        )         


    def did_mount(self):

        if self.total == 0:            
            self.btn_total.visible = False
            self.btn_fechar_caixa.visible = True  

        if self.status_caixa == 'A':
            self.page.close(self.modal_caixa)

        elif self.status_caixa == 'F':
            self.page.open(self.modal_caixa)
        
        self.page.update()    
        self.page.run_task(self.controller.get_Data)    





       


       








  


         