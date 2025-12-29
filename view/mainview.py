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
from view.controls.custonbuttons import CustonButton

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

        self.ident_serv:int = 0

        self.status_caixa:str = 'F'

        self.id_caixa:int = 0

        self.id_client:int = 0

        self.id_prof:int=0

        self.comission: int = 0

        self.total:float=0              

        self.bgcolor = AppColors.BACKGROUND_DARK

        self.dialog_nota_cliente = CustonDialog(
            self.page,
            "Atenção",
            "Deseja atribuir uma nota ao cliente?",
            [
                ft.TextButton(
                    "Cancelar",
                    on_click=self.controller.fechar_dialogo_nota_clientes,
                ),
                ft.TextButton(
                    "OK",
                    on_click=lambda e:[self.page.open(self.modal_nota_cliente), self.page.update()]
                )
            ]
        )

        self.radio_button_a = ft.Radio(
            label="A",
            value="A",
            fill_color=AppColors.ORANGE_DARK,
            label_style=ft.TextStyle(
                color=AppColors.ORANGE_DARK
            )
        )

        self.radio_button_b = ft.Radio(
            label="B",
            value="B",
            fill_color=AppColors.ORANGE_DARK,
            label_style=ft.TextStyle(
                color=AppColors.ORANGE_DARK
            )            
        )        

        self.radio_button_c = ft.Radio(
            label="C",
            value="C",
            fill_color=AppColors.ORANGE_DARK,
            label_style=ft.TextStyle(
                color=AppColors.ORANGE_DARK
            )              
            
        )        

        self.radio_group_nota_cliente = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    self.radio_button_a,
                    self.radio_button_b,
                    self.radio_button_c
                ]
            ),
        )

        self.modal_nota_cliente = CustonModalView(
            self.page,
            self.controller.atribuir_nota_cliente,
            self.controller.fechar_modal_nota_clientes,
            controls=[
                ft.Text(
                    'Atribua uma nota ao cliente.',
                    color=AppColors.GRAY_LIGHT2
                ),
                self.radio_group_nota_cliente
            ],
            height=250
        )

        self.list_insumos = CustonList(self.page, self)

        self.modal_insumos = CustonModalView(
            self.page,
            self.controller.baixa_insumo,
            self.controller.fechar_modal_insumos,
            [
                self.list_insumos
            ],
            500,
            350,
            'Dar baixa'
        )

        self.dialog_insumo = CustonDialog(
            self.page,
            'Atenção',
            'Deseja dar baixa nos materiais de insumo usados no atendimento?',
            [
                ft.TextButton(
                    'Cancelar',
                    on_click=self.controller.fechar_dialogo_insumos
                ),
                ft.TextButton(
                    'OK',
                     on_click=self.controller.abrir_modal_insumos
                )
            ]
        )

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

        self.btn_abrir_caixa = ft.ElevatedButton(
            visible=False,
            text='Abrir caixa', 
            color=AppColors.GRAY_LIGHT3,
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),            
            on_click=lambda e:self.page.run_task(self.controller.abrir_caixa)
        )              

        self.edt_troco_inicial = CustomTextField(
            label="Troco inicial",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        ) 

        self.edt_troco_fechamento = CustomTextField(
            label="Troco de fechamento",
            chars=r"^[0-9,]*$",
        ) 

        self.edt_dinheiro_fechamento = CustomTextField(
            label="Total de entrada em dinheiro",
            chars=r"^[0-9,]*$",
        ) 

        self.edt_pix_fechamento = CustomTextField(
            label="Total de entrada em pix",
            chars=r"^[0-9,]*$",
        )    

        self.edt_debito_fechamento = CustomTextField(
            label="Total de entrada em debito",
            chars=r"^[0-9,]*$",
        )              

        self.edt_credito_fechamento = CustomTextField(
            label="Total de entrada em credito",
            chars=r"^[0-9,]*$",
        ) 

        self.modal_fechamento_caixa = CustonModalView(
            height=380,
            page=self.page,
            callback=self.controller.confirmar_fechamento_caixa,
            callback2=lambda e:[self.page.close(self.modal_fechamento_caixa), self.page.update()],
            text_button_1="Fechar caixa",
            controls=[
               self.edt_troco_fechamento,
               self.edt_dinheiro_fechamento,
               self.edt_pix_fechamento,
               self.edt_debito_fechamento,
               self.edt_credito_fechamento
            ]            
        )

        self.modal_caixa = CustonModalView(
            self.page,
            callback=self.controller.confirmar_abertura_caixa,
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

        self.area_dinheiro = ft.Stack(
            controls=[
                self.edt_dinheiro,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    right=10,
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_dinheiro, e)
                )
            ]
        )       

        self.edt_pix = CustomTextField(
            label="Pix",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )        

        self.area_pix = ft.Stack(
            controls=[
                self.edt_pix,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_pix, e),
                    right=10,
                )
            ]
        ) 

        self.edt_debito = CustomTextField(
            label="Debito",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )    

        self.area_debito = ft.Stack(
            controls=[
                self.edt_debito,
                ft.IconButton(
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_debito, e),
                    right=10,
                )
            ]
        ) 

        self.edt_credito = CustomTextField(
            label="Credito",
            chars=r"^[0-9,]*$",
            on_change=self.controller.calculo_troco
        )          

        self.area_credito = ft.Stack(
            controls=[
                self.edt_credito,
                ft.IconButton(
                    alignment=ft.alignment.center_right,
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_credito, e),
                    right=10,
                )
            ]
        ) 

        self.modal_recebimento = CustonModalView(
            height=400,
            page=self.page,
            text_button_1="Receber",
            callback=self.controller.recebimento,
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
            callback=self.controller.confirmar_pequisa_clientes,
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
            on_blur=lambda e: self.controller.on_exit_edt_pesquisa(e)
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
            on_click=self.controller.open_modal_recebimento
        ) 

        self.drawer = ft.NavigationDrawer(
            bgcolor=AppColors.GRAY_DARK,
            elevation=10,
            controls=[
                ft.Container(                    
                    content=ft.Column(                        
                        controls=[
                            ft.Container(
                                height=50,
                                content=ft.TextButton(
                                    icon=ft.Icons.SHARE,
                                    icon_color=AppColors.ORANGE_DARK,
                                    text="Compartilhar anamnese",
                                    style=ft.ButtonStyle(
                                        color=AppColors.ORANGE_DARK,
                                    ),
                                ),
                            ),


                            CustonButton(self.page, "Minha conta", "/account"),
                            CustonButton(self.page, "Profissionais", "/professional"),
                            CustonButton(self.page, "Produtos", "/product"),  
                            CustonButton(self.page, "Serviços", "/services"),  
                            CustonButton(self.page, "Clientes", "/clients"),                                                
                                               
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
            on_click=self.controller.limpar_venda
        )

        self.btn_agenda = ft.FloatingActionButton(
            icon=ft.Icons.EVENT,
            bgcolor=AppColors.ORANGE_BURNT,
            shape=ft.CircleBorder(),
            tooltip="Agenda",
            on_click=lambda e: self.page.go("/agenda")
        )

        self.floating_action_button = self.btn_agenda
        self.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

        self.bottom_appbar = ft.BottomAppBar(
            shape=ft.NotchShape.CIRCULAR,
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
                    self.btn_abrir_caixa
                ],
            ),
        )         


    def did_mount(self):
        self.page.run_task(self.controller.get_Data) 


            
  
           





       


       








  


         