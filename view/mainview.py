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
import asyncio

class MainView(ft.View):
    def __init__(
            self, 
            page: ft.Page
        ):
        super().__init__(route="/main", bgcolor=AppColors.BACKGROUND_DARK,)
        
        #page = page

        self.controller = MainController(page, self)

        self.id_loja:str = ''
        self.token:str   = ''
        self.r_token:str = ''
        self.account_name:str = ''
        self.account_tel:str=''
        self.client:str = ''
        self.zap_instance:str=''
        self.zap_status:str=''

        self.ident_serv:int = 0

        self.status_caixa:str = 'F'

        self.id_caixa:int = 0

        self.id_client:int = 0

        self.id_prof:int=0

        self.comission: int = 0

        self.total:float=0              

        self.bgcolor = AppColors.BACKGROUND_DARK

        self.dialog_nota_cliente = CustonDialog(
            page,
            "Atenção",
            "Deseja atribuir uma nota ao cliente?",
            [
                ft.TextButton(
                    "Cancelar",
                    on_click=self.controller.fechar_dialogo_nota_clientes,
                ),
                ft.TextButton(
                    "OK",
                    on_click=lambda e:[page.open(self.modal_nota_cliente), page.update()]
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
            page,
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

        self.list_insumos = CustonList(page, self)

        self.modal_insumos = CustonModalView(
            page,
            self.controller.baixa_insumo,
            self.controller.fechar_modal_insumos,
            [
                self.list_insumos
            ],
            500,
            380,
            'Dar baixa'
        )

        self.dialog_insumo = CustonDialog(
            page,
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

        self.btn_fechar_caixa = ft.Button(
            visible=False,
            content='Fechar caixa', 
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

        self.btn_abrir_caixa = ft.Button(
            visible=False,
            content='Abrir caixa', 
            color=AppColors.GRAY_LIGHT3,
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),            
            on_click=lambda e: self.page.create_task(self.controller.abrir_caixa())
        )              

        self.edt_troco_inicial = CustomTextField(
            label="Troco inicial",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.controller.calculo_troco
        ) 

        self.edt_troco_fechamento = CustomTextField(
            label="Troco de fechamento",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        ) 

        self.edt_dinheiro_fechamento = CustomTextField(
            label="Total de entrada em dinheiro",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        ) 

        self.edt_pix_fechamento = CustomTextField(
            label="Total de entrada em pix",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )    

        self.edt_debito_fechamento = CustomTextField(
            label="Total de entrada em debito",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )              

        self.edt_credito_fechamento = CustomTextField(
            label="Total de entrada em credito",
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        ) 

        self.modal_fechamento_caixa = CustonModalView(
            height=380,
            page=page,
            callback=self.controller.confirmar_fechamento_caixa,
            callback2=lambda e:[page.pop_dialog(), page.update()],
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
            page,
            callback=self.controller.confirmar_abertura_caixa,
            callback2=lambda e:[page.close(self.modal_caixa), page.update()],
            text_button_1="Abrir caixa",
            height=150,
            controls=[
               self.edt_troco_inicial
            ]
        )

        self.list_profissionais = CustonListProfessional(page)
        
        self.progressRing = CustonProgressRing(page.height)
        
        self.list_itens = CustonList(page, self)

        self.list_clients = CL(page)

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
            on_change=self.controller.calculo_troco,
            keyboard_type=ft.KeyboardType.NUMBER,
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
            on_change=self.controller.calculo_troco,
            keyboard_type=ft.KeyboardType.NUMBER,
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
            on_change=self.controller.calculo_troco,
            keyboard_type=ft.KeyboardType.NUMBER,
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
            on_change=self.controller.calculo_troco,
            keyboard_type=ft.KeyboardType.NUMBER,
        )          

        self.area_credito = ft.Stack(
            controls=[
                self.edt_credito,
                ft.IconButton(
                    alignment=ft.Alignment.CENTER_RIGHT,
                    icon=ft.Icons.MONETIZATION_ON,
                    icon_color=AppColors.GRAY_LIGHT3,
                    on_click=lambda e: self.controller.preencher_valor_total(self.edt_credito, e),
                    right=10,
                )
            ]
        ) 

        self.modal_recebimento = CustonModalView(
            height=400,
            page=page,
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
            width=page.width / 4,
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
            height=600,
            page=page,
            callback=self.controller.confirmar_pequisa_clientes,
            callback2=self.controller.cancelar_modal_pesquisa_clientes,
            controls=[
                self.edtPesquisaClientes,
                self.list_clients
            ]
        )

        self.edtPesquisa = ft.TextField(
            width=page.width / 1.2,
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

        self.btn_pesquisa_produtos = ft.Button(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            content='Produtos',
            bgcolor=AppColors.GRAY_DARK,
            elevation=5,            
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),             
            on_click=lambda e: self.controller.exibir_edt_pesquisa_produtos(e)
        )

        self.btn_pesquisa_clientes = ft.Button(
            width=150,
            icon=ft.Icons.SEARCH,
            icon_color=AppColors.GRAY_LIGHT2,
            content='Clientes',
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
            alignment=ft.Alignment.CENTER_RIGHT,
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
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Container(
                                
                                bgcolor=AppColors.GRAY_DARK,
                                height=100,
                                border_radius=ft.BorderRadius.all(10),
                                padding=ft.Padding.all(10),
                                content=self.list_profissionais,
                            ), 
                            #self.edtCliente,
                            self.container_pesquisa,
                            self.list_itens,
                        ]
                    ),
                    self.progressRing,        
                ],        
            ),
        ]

        self.btn_total = ft.Button(
            content=f'Receber: R$ {formatar_moeda_brasileira(self.total)}', 
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

        self.status_whatsapp = ft.Text(
            'Desconectado',
            size=12,
            color=AppColors.ORANGE_DARK,
        )

        self.botao_whatsapp = ft.Button(
            'Conectar',
            elevation=5,
            expand=True,
            color=AppColors.GRAY_LIGHT2,
            on_click=self.controller.create_instance_zap
        )

        self.span_whatsapp = ft.TextSpan(
            text='',
            style=ft.TextStyle(color=AppColors.GRAY_LIGHT2),
        )

        self.area_whatsapp = ft.Container(
            padding=ft.Padding.all(10),
            #margin=ft.margin.all(10),
            border_radius=ft.BorderRadius.all(10),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK, 
                blur_radius=10,
                offset=ft.Offset(x=0, y=-0.5),
            ),
            height=120,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ), 

            content=ft.Column(
                controls=[
                    ft.Text('Whatsapp: ', size=12, color=AppColors.GRAY_LIGHT2, spans=[self.span_whatsapp]),
                    ft.Row(
                        controls=[
                            ft.Text('status: ', size=12, color=AppColors.GRAY_LIGHT2),
                            self.status_whatsapp,
                        ],
                    ),
                    ft.Row(
                        controls=[self.botao_whatsapp,],
                    ),
                ],
                expand=True,
            ), 
            expand=True,          
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
                                    content="Compartilhar anamnese",
                                    style=ft.ButtonStyle(
                                        color=AppColors.ORANGE_DARK,
                                    ),
                                    on_click=lambda e: asyncio.create_task(self.controller.create_link_anamnese(e)),
                                ),
                            ),

                            self.area_whatsapp,
                            CustonButton(page, "Minha conta", "/account"),
                            CustonButton(page, "Profissionais", "/professional"),
                            CustonButton(page, "Produtos", "/product"),  
                            CustonButton(page, "Serviços", "/services"),  
                            CustonButton(page, "Clientes", "/clients"),                                                
                                               
                            ft.Button(
                                content="Sair",
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
                                on_click=self.controller.handler_logout,
                            ),                                                   
                        ],
                    ),
                    padding=ft.Padding.all(20),
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
            on_click=lambda e: page.go("/agenda"),
            visible=True,
        )

        self.floating_action_button = self.btn_agenda
        self.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

        self.bottom_appbar = ft.BottomAppBar(
            shape=ft.CircularRectangleNotchShape(),   
            height=60,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=self.controller.show_drawer,
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
        asyncio.create_task(self.controller.get_Data())


            
  
           





       


       








  


         