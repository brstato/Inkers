import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.agendacontroller import AgendaController
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custoncardcalendar import CustonRowCalendar
from view.controls.custoncardcalendar import CustonRowDays
from view.controls.controls_mainview.custonlistprofessionais import CustonListProfessional
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList



class AgendaView(ft.View):
    def __init__(self, page:ft.Page, is_pendent:bool = False):
        super().__init__(
            route="/agenda", 
            scroll="auto",
            bgcolor=AppColors.BACKGROUND_DARK
        )

        self.id:int = 0
        self.id_prof:int = 0

        self.id_loja:str = ''
        self.token:str   = ''
        self.r_token:str = ''

        self.g_token: str  = ''
        self.g_r_token:str = ''

        self.zap_instance:str = ''

        self.client_name:str = ''
        self.client_telefone:int = 0
        self.client_id:int = 0

        self.progressRing = CustonProgressRing(page.height) 

        self.controller = AgendaController(page, self)

        self.month_row = CustonRowCalendar(page, self)

# --- MODAL E LISTA DE PENDENTES ---
        self.lista_cards_pendentes = CustonList(page, self)

        self.modal_pendentes = ft.BottomSheet(
            bgcolor=AppColors.BLACK,
            content=ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(
                    controls=[
                        self.lista_cards_pendentes,
                    ],
                ),
            ),
        )
        
        # self.modal_pendentes = CustonModalView(
        #     page,
        #     callback=None, # Não tem botão de ação global, a ação é nos cards
        #     callback2=lambda e: [page.pop_dialog(), page.update()],
        #     controls=[
        #         ft.Text("Solicitações Pendentes", size=15, color=AppColors.GRAY_LIGHT2, weight="bold"),
        #         self.lista_cards_pendentes
        #     ],
        #     height=500,
        #     text_button_1="Fechar",
        # )

        # --- SININHO DE NOTIFICAÇÕES ---
        self.notification_badge = ft.Container(
            width=10, 
            height=10, 
            bgcolor=ft.Colors.RED_700,
            border_radius=5, 
            right=8, 
            top=8, 
            #visible=False,
            border=ft.border.all(1, AppColors.GRAY_DARK)
        )
        
        self.btn_notificacoes = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS,
            icon_color=AppColors.GRAY_LIGHT2,
            on_click=self.controller.abrir_lista_pendentes,
        )
        
        self.area_notificacoes = ft.Stack(
            visible=False,
            controls=[
                self.btn_notificacoes, 
                self.notification_badge
            ]
        )        

        self.month_container = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),             
            height=50,
            content=self.month_row,
            padding=ft.padding.all(10),
            margin=ft.margin.all(2),
            bgcolor=AppColors.GRAY_DARK,
            border_radius=ft.border_radius.all(10),            
        )

        self.edt_client_name = ft.Dropdown(
            label='Nome do cliente',
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            elevation=5,
            editable=True,
            enable_filter=True,
            expand=True,
            enable_search=True,
            menu_height=500,
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,           
            on_text_change=self.controller.on_client_selected
        )

        self.edt_client_telefone = CustomTextField(
            label='Telefone',
            readOnly=True,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.client_area = ft.Stack(
            controls=[
                self.edt_client_name,
                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    icon_color=AppColors.GRAY_LIGHT2,
                    right=5
                )
            ]
        )

        self.calendario_agenda = ft.DatePicker(on_change=self.controller.selected_date_calendar)

        self.edt_hora_ini = CustomTextField(
            label='Inicio'
        )


        self.edt_hora_fim = CustomTextField(
            label='Fim'
        )

        self.hora_fim = ft.TimePicker(on_change=self.controller.selected_time_fim)

        self.area_fim = ft.Stack(
            controls=[
                self.edt_hora_fim,
                ft.IconButton(
                    right=5,
                    icon=ft.Icons.SCHEDULE,                    
                    on_click=lambda e:[page.show_dialog(self.hora_fim), page.update()],
                    icon_color=AppColors.GRAY_LIGHT2,                    
                )
            ]
        )


        self.hora_ini = ft.TimePicker(on_change=self.controller.selected_time_ini)

        self.area_ini = ft.Stack(
            controls=[
                self.edt_hora_ini,
                ft.IconButton(
                    right=5,
                    icon=ft.Icons.SCHEDULE,                    
                    on_click=lambda e:[page.show_dialog(self.hora_ini), page.update()],
                    icon_color=AppColors.GRAY_LIGHT2,
                )
            ]
        )

        self.edt_date_agendamento = CustomTextField(
            label='Data do agendamento',
            readOnly=True,
            keyboard_type=ft.KeyboardType.DATETIME,
            regex=r"[0-9/]"
        )

        self.date_area = ft.Stack(
            controls=[
                self.edt_date_agendamento,
                ft.IconButton(
                    icon=ft.Icons.DATE_RANGE,
                    icon_color=AppColors.GRAY_LIGHT2,
                    right=5,
                    on_click=lambda e:[page.show_dialog(self.calendario_agenda), page.update()]
                )                
            ]
        )

        self.edt_edt_valor = CustomTextField(
            label='Valor',
            keyboard_type=ft.KeyboardType.NUMBER,
            regex=r"^[0-9,]*$"
        )

        self.edt_edt_sinal = CustomTextField(
            label='Sinal',
            keyboard_type=ft.KeyboardType.NUMBER,
            regex=r"^[0-9,]*$"
        )


        self.modal_create_agenda = CustonModalView(
            page,
            callback=self.controller.confirm_agendamento,
            callback2=lambda e: page.run_task(self.controller.fechar_modal_agenda, e),
            controls=[
                self.edt_client_name,
                self.edt_client_telefone,
                self.date_area,
                self.area_ini,
                self.area_fim,
                self.edt_edt_valor,
                self.edt_edt_sinal,                
            ],
            height=550,
        )        


        self.calendario = CustonRowDays(page, self)

        self.container_calendario = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),             
            height=90,
            content=self.calendario,
            padding=ft.padding.all(10),
            margin=ft.margin.all(2),
            bgcolor=AppColors.GRAY_DARK,
            border_radius=ft.border_radius.all(10),
        )

        self.list_profissionais = CustonListProfessional(
            page
        )

        self.list_agendamento = CustonList(
            page,
            instance=self
        )

        self.bottom_appbar = ft.BottomAppBar(
            height=60,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=lambda e:page.go("/main")
                    ),
                    ft.Container(
                        expand=True,
                    ),
                    self.area_notificacoes,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=self.controller.create_agenda
                    ),
                ],
            )            
        )        


        self.controls = [
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            self.list_profissionais,
                            self.month_container,
                            self.container_calendario,
                            self.list_agendamento,
                        ]
                    ),
                    self.progressRing
                ]
            ),            
        ]


    def did_mount(self):
        self.page.run_task(self.controller.get_data)    
