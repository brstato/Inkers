import flet as ft
import datetime
from urllib.parse import unquote
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from view.controls.custonprogressring import CustonProgressRing
from controller.agendaturnoscontroller import AgendaTurnosController

class AgendaTurnosView(ft.View):
    def __init__(self, page: ft.Page, name: str, tel: str):
        super().__init__(
            route="/agendaturnos", 
            scroll=ft.ScrollMode.AUTO,
            bgcolor=AppColors.BLACK,
            padding=0 # Remove padding padrão para controle total
        )
        
        
        self.name = unquote(name)
        self.tel = unquote(tel)
        
        # Inicializa o Controller passando a View (self)
        self.controller = AgendaTurnosController(page, self)

        # --- Estado (Dados) ---
        self.now = datetime.datetime.now()
        self.dates_data = [self.now + datetime.timedelta(days=i) for i in range(31)]
        self.selected_date_index = 0
        self.selected_shift = None

        # --- Elementos de UI ---
        self.month_label = ft.Text("", size=14, color=AppColors.GRAY_LIGHT2, weight="bold")
        
        # Linha horizontal de dias (será preenchida pelo Controller)
        self.date_controls_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=20)
        
        # Loading (Indicador de carregamento)
        self.progress_ring = CustonProgressRing()

        # Linha de Turnos (Será preenchida dinamicamente pelo Controller: Manhã/Tarde/Noite)
        self.shifts_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[] 
        )

        self.phone_input = CustomTextField(
            label="Informe seu telefone",
            keyboard_type=ft.KeyboardType.PHONE,
            regex=r"[0-9]"
        )
        
        # --- Configurar BottomSheet ---
        self.bottom_sheet = ft.BottomSheet(
            ft.Container(
                padding=ft.padding.all(20),
                bgcolor=AppColors.BACKGROUND_DARK,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text("Confirmar Agendamento", size=20, weight="bold"),
                        ft.Divider(color="transparent", height=10),
                        self.phone_input,
                        ft.Divider(color="transparent", height=20),
                        ft.ElevatedButton(
                            "Confirmar", 
                            style=ft.ButtonStyle(
                                bgcolor=AppColors.ORANGE_DARK,
                                color=AppColors.GRAY_LIGHT2,
                                shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            width=300,
                            height=50,
                            on_click=self.controller.close_sheet
                        )
                    ]
                )
            )
        )

        # --- Definição do Layout ---
        self.controls = [
            ft.Container(height=10),
            
            # Loading centralizado (aparece só ao carregar)
#            ft.Center(self.progress_ring),

            # Header Calendário (Mês + Dias)
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        self.month_label,
                        ft.Container(height=10),
                        self.date_controls_row,
                    ]
                )
            ),

            ft.Divider(color="transparent", height=30),

            # Título Turnos
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=ft.Text("Turnos Disponíveis", size=18, weight="bold")
            ),
            
            ft.Container(height=10),

            # Lista de Turnos (Manipulada pelo Controller)
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=self.shifts_row
            ),
            
            # Espaço extra no final
            ft.Container(height=50)
        ]

    def did_mount(self):
        # Configura o AppBar
        self.controller._setup_appbar()
        
        # Inicia a busca de dados na API (Disponibilidade) e monta a tela
        self.page.run_task(self.controller.init_data)