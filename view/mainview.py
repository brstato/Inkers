import flet as ft
from view.controls.colors import AppColors
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
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

        self.id_loja:             str = ''
        self.token:               str = ''
        self.r_token:             str = ''
        self.account_name:        str = ''
        self.account_tel:         str = ''
        self.client:              str = ''
        self.zap_instance:        str = ''
        self.zap_status:          str = ''
        self.slug:                str = ''
        self.meta_long_token:     str = ''
        self.status_caixa:        str = 'F'
        self.status_campanha:     str="False"

        self.ident_serv:          int = 0 
        self.id_caixa:            int = 0
        self.id_client:           int = 0
        self.id_prof:             int = 0
        self.comission:           int = 0

        self.total:               float=0              

        

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
                    on_click=lambda e:[page.show_dialog(self.modal_nota_cliente), page.update()]
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
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.controller.calculo_troco
        ) 

        self.edt_troco_fechamento = CustomTextField(
            label="Troco de fechamento",
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        ) 

        self.edt_dinheiro_fechamento = CustomTextField(
            label="Total de entrada em dinheiro",
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        ) 

        self.edt_pix_fechamento = CustomTextField(
            label="Total de entrada em pix",
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )    

        self.edt_debito_fechamento = CustomTextField(
            label="Total de entrada em debito",
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )              

        self.edt_credito_fechamento = CustomTextField(
            label="Total de entrada em credito",
            regex=r"^[0-9,]*$",
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
            regex=r"^[0-9,]*$",
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
            regex=r"^[0-9,]*$",
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
            regex=r"^[0-9,]*$",
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
            regex=r"^[0-9,]*$",
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
            on_change=self.filter_clients, 
            border_color=AppColors.ORANGE_DARK,
            border=ft.InputBorder.UNDERLINE,  
        ) 

        self.modal_pesquisa_clientes = CustonModalView(
            height=600,
            page=page,
            callback=self.confirmar_pequisa_clientes,
            callback2=self.cancelar_modal_pesquisa_clientes,
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
            on_change=self.handle_filter_itens,
            border_color=AppColors.GRAY_MED3,
            border=ft.InputBorder.UNDERLINE,
            height=40,
            content_padding=10,    
            on_click=lambda e: self.on_enter_edt_pesquisa(e),
            on_blur=lambda e: self.on_exit_edt_pesquisa(e)
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
            on_click=lambda e: self.exibir_edt_pesquisa_produtos(e)
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
            on_click=lambda e: self.exibir_lista_clientes(e)        
        )

        self.btn_fechar_pesquisa = ft.IconButton(
            alignment=ft.Alignment.CENTER_RIGHT,
            icon=ft.Icons.CLOSE,
            icon_color=AppColors.ORANGE_DARK,
            visible=False,     
            on_click=lambda e: self.handle_fechar_pesquisa(e)                   
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
            on_click=self.controller.create_instance_zap,
            bgcolor=AppColors.GRAY_DARK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),
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

        self.status_meta = ft.Text(
            'Desconectado',
            size=12,
            color=AppColors.ORANGE_DARK,
        )

        self.botao_meta = ft.Button(
            'Conectar',
            elevation=5,
            expand=True,
            color=AppColors.GRAY_LIGHT2,
            on_click=self.controller.login_meta,
            bgcolor=AppColors.GRAY_DARK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),
        )

        self.botao_alterar_meta = ft.Button(
            'Alterar Conta',
            elevation=5,
            expand=True,
            visible=False,
            color=AppColors.GRAY_LIGHT2,
            on_click=lambda e: asyncio.create_task(self.controller.meta_integracao.get_meta_ads_id(self.meta_long_token)),
            bgcolor=AppColors.GRAY_DARK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_MED3),
                color=AppColors.GRAY_LIGHT,
            ),
        )

        self.meta_ads_list_dropdown = ft.Dropdown(
            label="Contas Meta Ads",
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),            
            elevation=5,
            editable=True,
            enable_filter=True,
            expand=True,
            enable_search=True,            
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,   
        )

        self.meta_ads_dialog = CustonDialog(
            page=page,
            title='Atenção!',
            content='Selecione a conta de anuncio para começar',
            actions=[
                self.meta_ads_list_dropdown,
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Fechar",  
                            style=ft.ButtonStyle(
                                color=AppColors.GRAY_LIGHT2,
                            ),
                            on_click=lambda _: [self.page.pop_dialog(), self.page.update()]),
                        ft.Container(expand=True),
                        ft.TextButton(
                            "Ok",
                            style=ft.ButtonStyle(
                                color=AppColors.GRAY_LIGHT2,
                            ),
                            on_click=lambda e: asyncio.create_task(self.controller.meta_integracao.salvar_meta_ads_id_selecionado(e))),                        
                    ]
                )
            ]
        )

        self.meta_ads_campaign_activate = ft.Switch(
            active_color=AppColors.ORANGE_BURNT,
            label='Ativar anúncios',
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            #on_change=self.controller.on_switch_ads
        ) 

        self.area_meta = ft.Container(
            padding=ft.Padding.all(10),
            border_radius=ft.BorderRadius.all(10),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK, 
                blur_radius=10,
                offset=ft.Offset(x=0, y=-0.5),
            ),
            #height=150,
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
                    ft.Text('Meta Ads: ', size=12, color=AppColors.GRAY_LIGHT2),
                    ft.Row(
                        controls=[
                            ft.Text('status: ', size=12, color=AppColors.GRAY_LIGHT2),
                            self.status_meta,
                        ],
                    ),
                    ft.Row(
                        controls=[self.botao_meta],
                    ),
                    ft.Row(
                        controls=[self.botao_alterar_meta],
                    ),
                    ft.Row(
                        controls=[self.meta_ads_campaign_activate],
                    ),
                ]
            )
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
                            ft.Container(
                                height=50,
                                content=ft.TextButton(
                                    icon=ft.Icons.SHARE,
                                    icon_color=AppColors.ORANGE_DARK,
                                    content="Compartilhar agenda",
                                    style=ft.ButtonStyle(
                                        color=AppColors.ORANGE_DARK,
                                    ),
                                    on_click=lambda e: asyncio.create_task(self.controller.create_link_agenda_turnos(e)),
                                ),
                            ),                            

                            self.area_whatsapp,
                            CustonButton(page, "Minha conta",        "/account"),
                            CustonButton(page, "Profissionais", "/professional"),
                            CustonButton(page, "Produtos",           "/product"),  
                            CustonButton(page, "Serviços",          "/services"),  
                            CustonButton(page, "Clientes",           "/clients"),    
                            CustonButton(page, "Despesas",          "/despesas"),  
                            CustonButton(page, "Portfólio",        "/portfolio"),                                              
                                               
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

        self.icon_notification = ft.Container(
            width=10, 
            height=10, 
            bgcolor=AppColors.ORANGE_BURNT,
            border_radius=5, 
            right=8, 
            top=8, 
            visible=False,
            border=ft.border.all(1, AppColors.GRAY_DARK),
            animate_scale=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
            scale=1,           
        )

        self.btn_agenda = ft.FloatingActionButton(
            #icon=ft.Icons.EVENT,
            bgcolor=AppColors.GRAY_DARK,
            shape=ft.CircleBorder(),
            tooltip="Agenda",
            on_click=lambda e: page.go("/agenda"),
            visible=True,
            content=ft.Stack(
                controls=[
                    ft.Icon(
                        icon=ft.Icons.EVENT,
                        color=AppColors.GRAY_LIGHT2,
                        size=30,
                        left=12,
                        top=12,
                    ),
                    self.icon_notification 
                ],
                height=55,
                width=55,
            ),
            # ft.Icon(
            #     icon=ft.Icons.NOTIFICATIONS,
            #     color=AppColors.WHITE,
            #     size=20,
            # ),
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


    def filter_clients(self, e):
        search_term = self.edtPesquisaClientes.value.lower()
        
        for card in self.list_clients.controls:
            from view.controls.custoncardsimples import CustonCardSimples
            if isinstance(card, CustonCardSimples):
                client_name = card.title.lower()
                if search_term in client_name:
                    card.visible = True
                else:
                    card.visible = False
        
        self.page.update()          


    def on_exit_edt_pesquisa(self, e):
        self.edtPesquisa.border_color=AppColors.GRAY_MED3
        self.page.update()   


    def on_enter_edt_pesquisa(self, e):
        self.edtPesquisa.border_color=AppColors.ORANGE_DARK
        self.page.update()


    def exibir_edt_pesquisa_produtos(self, e):
        self.edtPesquisa.visible = True
        self.btn_pesquisa_produtos.visible = False
        self.btn_pesquisa_clientes.visible = False
        self.btn_fechar_pesquisa.visible = True
        self.page.update()  


    def exibir_lista_clientes(self, e):
        self.page.show_dialog(self.modal_pesquisa_clientes)
        self.btn_agenda.visible = False
        self.btn_cancelar.visible = True
        self.btn_fechar_caixa.visible = False
        self.page.update()        


    def cancelar_modal_pesquisa_clientes(self, e):
        self.id_client = 0
        self.text_client.visible = False
        self.page.pop_dialog()
        self.page.update()           


    async def confirmar_pequisa_clientes(self, e):
        self.page.pop_dialog()
        self.page.update()


    def handle_filter_itens(self, e):
        search_term = self.edtPesquisa.value.lower()
        for card in self.list_itens.controls:
            from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
            if isinstance(card, CustonCardItensVenda):
                client_name = card.name.lower()
                if search_term in client_name:
                    card.visible = True
                else:
                    card.visible = False
        self.page.update()  


    def handle_fechar_pesquisa(self, e):
        self.edtPesquisa.visible = False
        self.edtPesquisa.value = ''    
        self.handle_filter_itens(e)
        self.btn_pesquisa_produtos.visible = True
        self.btn_pesquisa_clientes.visible = True
        self.btn_fechar_pesquisa.visible = False        
        self.page.update()


    async def carregar_insumos(self):
        array = await self.controller.get_insumos_data()
        self.list_insumos.controls.clear()
        for item in array:
            from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
            card = CustonCardItensVenda(
                page=self.page,
                width=280,
                instance=self,
                icon=None,
                name=item["nome"],
                id=item["id"],
                estoque=item["estoque"],
                valor=item["valor"],
                tap=self.list_itens.on_card_selected,
                on_change=self.list_insumos.recalculate_total
            )
            self.list_insumos.controls.append(card) 
        self.page.update()


    async def carregar_itens(self):
        array = await self.controller.get_itens_data()
        self.list_itens.controls.clear()
        for item in array:
            ident = item["ident_serv"]
            icon = ft.Icons.CATEGORY if ident == 0 else ft.Icons.MISCELLANEOUS_SERVICES
            
            from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
            card = CustonCardItensVenda(
                ident_serv=ident,
                page=self.page,
                width=self.page.width,
                instance=self,
                icon=icon,
                name=item["nome"],
                id=item["id"],
                estoque=item["quantidade_estoque"],
                valor=item["valor_venda"],
                inf_valor=item["inf_valor"],
                comissionado=item["comissionado"],
                tap=self.list_itens.on_card_selected,
                on_change=self.list_itens.recalculate_total
            )
            self.list_itens.controls.append(card) 
        self.page.update()


    async def carregar_profissionais(self):
        array = await self.controller.get_profissionais_data()
        self.list_profissionais.controls.clear()
        for item in array:
            if len(array) == 1:
                self.id_prof = item["id"]
                self.comission = item["comissao"]

            from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
            card = CustonCardProfessional(
                instance=self,
                name=item["name"],
                id=item["id"],
                comission=item["comissao"],
                tap=self.list_profissionais.on_card_selected
            )
            self.list_profissionais.controls.append(card) 
        self.page.update()


    async def carregar_clientes(self):
        array = await self.controller.get_clientes_data()
        self.list_clients.controls.clear()
        for item in array:
            from view.controls.custoncardsimples import CustonCardSimples
            card = CustonCardSimples(
                page=self.page,
                id=item["id"],
                title=item["nome"],
                tap=self.list_clients.on_card_selected,
                instance=self
            )
            self.list_clients.controls.append(card)
        self.page.update()