import flet as ft
import datetime
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from view.controls.custonprogressring import CustonProgressRing
from controller.agendaturnoscontroller import AgendaTurnosController
from view.controls.custondialog import CustonDialog

class AgendaTurnosView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/agendaturnos", 
            scroll=ft.ScrollMode.AUTO,
            bgcolor=AppColors.BLACK,
            padding=0
        )
        
        self.name:str = ''
        self.tel:str = ''
        self.id_profissional: int = 0
        
        self.controller = AgendaTurnosController(page, self)

        # Estado Local da UI
        self.now = datetime.datetime.now()
        self.dates_data = [self.now + datetime.timedelta(days=i) for i in range(31)]
        self.selected_date_index = 0
        self.selected_shift = None

        # Elementos de UI
        self.month_label = ft.Text("", size=14, color=AppColors.GRAY_LIGHT2, weight="bold")
        self.date_controls_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=20)
        self.progress_ring = CustonProgressRing()
        self.shifts_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY, controls=[])

        self.phone_input = CustomTextField(
            label="Informe seu telefone",
            keyboard_type=ft.KeyboardType.PHONE,
            regex=r"[0-9]",
            on_blur=lambda e: page.run_task(self.controller._get_client_data, e)
        )

        self.name_input = CustomTextField(
            label="Nome",
            readOnly=True,
        )
        
        self.client_area = ft.Container(
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=ft.Padding.all(10),
            content=ft.Column(controls=[self.phone_input, self.name_input]),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[AppColors.GRAY_DARK, AppColors.BACKGROUND_DARK],                
            ),            
        )

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
                            on_click=self.confirm_booking
                        )
                    ]
                )
            )
        )

        self.controls = [
            ft.Container(height=10),
            self.client_area,
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=ft.Column(
                    spacing=10,
                    controls=[self.month_label, ft.Container(height=10), self.date_controls_row]
                )
            ),
            ft.Divider(color="transparent", height=30),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=ft.Text("Turnos Disponíveis", size=18, weight="bold")
            ),
            ft.Container(height=10),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20),
                content=self.shifts_row
            ),
            ft.Container(height=50)
        ]

    def did_mount(self):
        self.page.run_task(self.controller.init_data)

    # =========================================================================
    # MÉTODOS DE MANIPULAÇÃO DA UI (Chamados pelo Controller)
    # =========================================================================

    def setup_appbar(self):
        self.appbar = ft.AppBar(
            title=ft.Text("Agenda", color=AppColors.GRAY_LIGHT2),
            bgcolor=AppColors.BACKGROUND_DARK,
            elevation=0,
            leading=None
        )
        self.page.update()

    def clear_lists(self):
        self.date_controls_row.controls.clear()
        self.shifts_row.controls.clear()
        self.page.update()

    def set_loading(self, is_loading: bool):
        self.progress_ring.visible = is_loading
        self.page.update()

    def show_message_dialog(self, title: str, content: str):
        dialog = CustonDialog(
            self.page, title, content,
            [ft.TextButton('Fechar', on_click=lambda e: self.page.pop_dialog())]
        )
        self.page.show_dialog(dialog)

    # =========================================================================
    # MÉTODOS DE CRIAÇÃO E RENDERIZAÇÃO DE CONTROLES
    # =========================================================================

    def render_calendar(self, availability_map: dict):
        self.date_controls_row.controls.clear()
        dias_pt = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]

        for i, dt in enumerate(self.dates_data):
            data_br = dt.strftime("%d/%m/%Y")
            
            loja_aberta = len(availability_map.get(data_br, [])) > 0
            is_selected = (i == self.selected_date_index)

            # Estilos condicionais
            if not loja_aberta:
                day_color = ft.Colors.GREY_800
                weekday_color = ft.Colors.GREY_900
                weight_day = "normal"
                on_click_action = None
                opacity = 0.3
            else:
                day_color = AppColors.ORANGE_DARK if is_selected else AppColors.GRAY_LIGHT2
                weekday_color = AppColors.GRAY_LIGHT4 if is_selected else AppColors.GRAY_LIGHT2
                weight_day = "bold" if is_selected else "normal"
                on_click_action = lambda e, idx=i: self.page.run_task(self.controller.select_date, idx)
                opacity = 1.0

            # Criação explícita do controle (Append)
            self.date_controls_row.controls.append(
                ft.Container(
                    on_click=on_click_action,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=10,
                    opacity=opacity,
                    animate_opacity=300,
                    content=ft.Column(
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(dias_pt[dt.weekday()], size=12, color=weekday_color),
                            ft.Text(str(dt.day), size=(22 if is_selected else 18), color=day_color, weight=weight_day),
                        ]
                    )
                )
            )
        
        # Após desenhar o calendário, desenha os turnos do dia atual
        data_selecionada = self.dates_data[self.selected_date_index].strftime("%d/%m/%Y")
        turnos = availability_map.get(data_selecionada, [])
        self.render_shifts(turnos)
        
        self.page.update()

    def render_shifts(self, turnos_disponiveis: list):
        self.shifts_row.controls.clear()
        
        if not turnos_disponiveis:
             self.shifts_row.controls.append(
                 ft.Text("Nenhum horário disponível", color=AppColors.GRAY_LIGHT2)
             )
        else:
            info_turnos = {
                "Manhã": {"horario": "08:00 - 12:00", "icon": ft.Icons.SUNNY},
                "Tarde": {"horario": "13:00 - 18:00", "icon": ft.Icons.WB_TWILIGHT},
                "Noite": {"horario": "18:00 - 22:00", "icon": ft.Icons.NIGHTLIGHT_ROUND}
            }
            
            for nome_turno in turnos_disponiveis:
                dados = info_turnos.get(nome_turno)
                if dados:
                    # Criação explícita do controle (Append)
                    self.shifts_row.controls.append(
                        ft.Container(
                            expand=True,
                            bgcolor=AppColors.BACKGROUND_DARK,
                            border_radius=15,
                            padding=ft.Padding.all(15),
                            on_click=lambda e, t=nome_turno: self.open_shift_modal(t),
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(dados["icon"], color=AppColors.ORANGE_DARK, size=30),
                                    ft.Text(nome_turno, weight="bold", size=16),
                                    ft.Text(dados["horario"], size=12, color=AppColors.GRAY_LIGHT2)
                                ]
                            )
                        )
                    )
        
        self.page.update()

    def open_shift_modal(self, shift_name):
        self.selected_shift = shift_name
        self.page.show_dialog(self.bottom_sheet)

    def confirm_booking(self, e):
        self.page.pop_dialog()
        self.page.show_dialog(
            ft.SnackBar(
                ft.Text(f"Agendado para {self.selected_shift}, aguardando aprovação!"), 
                bgcolor=AppColors.ORANGE_DARK
            )
        ) 
        self.page.update()