import flet as ft
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from controller.sitecontroller import SiteController

class SiteView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/site",
            bgcolor=AppColors.BLACK,
            padding=ft.padding.all(20),
            scroll=ft.ScrollMode.AUTO
        )

        self.id_loja:str = ''
        self.token:str = ''

        self.controller = SiteController(page=page, instance=self)

        self.loading = CustonProgressRing()

        self.edt_titulo = CustomTextField(
            label='Titulo',
            max_length=500,
            multiline=True,            
        )

        self.edt_subtitulo = CustomTextField(
            label='Subtitulo',
            max_length=1000, 
            multiline=True,            
        )

        self.area_titulo = ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
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
                    self.edt_titulo,
                    self.edt_subtitulo,
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),            
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
                ],
            )            
        )

        self.btn_salvar = ft.Row(
            controls=[
                ft.Button(
                    expand=True,
                    content=ft.Text(
                        value='Salvar', 
                        color=AppColors.GRAY_LIGHT2,
                        weight=ft.FontWeight.BOLD
                    ),
                    icon=ft.Icons.SAVE,
                    icon_color=AppColors.GRAY_LIGHT2,
                    bgcolor=AppColors.ORANGE_BURNT,
                    on_click=self.controller.update_site
                ) 
            ]
        )  

        self.controls = [
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            self.area_titulo,
                            self.btn_salvar
                        ]
                    ),
                    self.loading
                ]
            ),
        ]


    def did_mount(self):
        self.page.run_task(self.controller.get_data)    