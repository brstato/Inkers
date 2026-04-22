import flet as ft
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from controller.portfoliocontroller import PortfolioController


class PortfolioView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/portfolio",
            bgcolor=AppColors.BLACK,
            padding=ft.padding.all(20),
            scroll=ft.ScrollMode.AUTO
        )

        self.id_loja:str = ''
        self.token:  str = ''
        self.r_token:str = ''
        self.slug:   str = ''       

        self.controller = PortfolioController(page=page, instance=self)

        # self.file_picker = ft.FilePicker()
        # page.overlay.append(self.file_picker)        

        self.loading = CustonProgressRing()

        self.img_avatar = ft.Image(
            src='https://brunotattoo.inkers.com.br/imagens/eu.JPG?v=1',
            fit=ft.BoxFit.COVER,
            repeat=ft.ImageRepeat.NO_REPEAT,
            height=100,
            width=100,
        )

        self.avatar = ft.Container(
            width=100,
            height=100,
            border_radius=ft.border_radius.all(10),
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[
                    self.img_avatar,
                    ft.IconButton(
                        icon=ft.Icons.CAMERA_ALT,
                        icon_color=AppColors.GRAY_LIGHT,
                        bottom=2,
                        right=2,
                    ),
                ]
            )
        )

        self.area_avatar = ft.Row(
            controls=[
                ft.Container(expand=True),
                self.avatar,
                ft.Container(expand=True),
            ]
        )

        self.edt_titulo = CustomTextField(
            label='Titulo',
            max_length=100,
            multiline=True,            
        )

        self.edt_subtitulo = CustomTextField(
            label='Subtitulo',
            max_length=500, 
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

        self.bio_image = ft.Image(
            src='https://brunotattoo.inkers.com.br/imagens/bio.JPG?v=1',
            fit=ft.BoxFit.COVER,
            repeat=ft.ImageRepeat.NO_REPEAT,
            width=100,
            height=100,
        )

        self.bio_foto = ft.Container(
            width=100,
            height=100,
            border_radius=ft.border_radius.all(50),
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[
                    self.bio_image,
                    ft.IconButton(
                        icon=ft.Icons.CAMERA_ALT,
                        icon_color=AppColors.GRAY_LIGHT,
                        bottom=2,
                        right=10,
                    ),
                ]
            )            
        )

        self.edt_bio = CustomTextField(
            label='Bio',
            multiline=True,
            max_length=1000,
        )

        self.area_bio = ft.Container(
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
                    self.edt_bio,
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),            
        )        

        self.area_bio_foto = ft.Row(
            controls=[
                ft.Container(expand=True),
                self.bio_foto,
                ft.Container(expand=True),
            ]
        )

        self.galeria = ft.Row(scroll=ft.ScrollMode.AUTO)

        self.area_galeria = ft.Container(
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
                    ft.Text(value='Galeria', color=AppColors.GRAY_LIGHT2, weight=ft.FontWeight.BOLD),
                    self.galeria,
                    ft.Row(
                        controls=[
                            ft.Button(
                                expand=True,
                                content=ft.Text(
                                    value='Adicionar', 
                                    color=AppColors.GRAY_LIGHT2,
                                    weight=ft.FontWeight.BOLD
                                ),
                                icon=ft.Icons.ADD,
                                icon_color=AppColors.GRAY_LIGHT2,
                                bgcolor=AppColors.TRANSPARENT,
                                on_click=self.controller.pick_and_upload_foto
                            )                             
                        ]
                    )
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
                    #on_click=self.controller.update_site
                ) 
            ]
        )  

        self.controls = [
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            self.area_avatar,
                            self.area_titulo,
                            self.area_bio_foto,
                            self.area_bio,
                            self.area_galeria,
                            self.btn_salvar
                        ]
                    ),
                    self.loading
                ]
            ),
        ]


    def did_mount(self):
        self.page.run_task(self.controller.get_data)    