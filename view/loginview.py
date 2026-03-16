import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.logincontroller import LoginController
from view.controls.custonprogressring import CustonProgressRing


class LoginView(ft.View):
    
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=0,
           
        )
        #self.page = page

        self.controller = LoginController(page)

        self.progress_ring = CustonProgressRing(page.height)

        self.logo = ft.Image(
            width=300,
            src=f"inkers_logo.png", 
        )


        self.txt_username = CustomTextField("Email", keyboard_type=ft.KeyboardType.EMAIL)
        self.txt_password = CustomTextField("Senha", password=True, can_reveal_password=True)


        self.btn_login_google = ft.Row(
            expand=True,
            controls=[
                ft.Button(
                    content=ft.Text("Entrar"),
                    bgcolor=AppColors.ORANGE_DARK,
                    color=AppColors.WHITE,
                    elevation=5,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        #side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    on_click=self._on_click_login_google,
                )
            ],
        )

        self.btn_login = ft.Row(
            expand=True,
            controls=[
                ft.Button(
                    content=ft.Text("Entrar"),
                    bgcolor=AppColors.ORANGE_BURNT,
                    color=AppColors.WHITE,
                    elevation=5,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        #side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    on_click=self._on_click_login,
                )
            ],
        )


        self.btn_create_account = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Criar Conta",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    on_click=self._go_to_account
                )
            ],
        )


        self.btn_forgot_password = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Esqueci minha senha",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        #side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    on_click=self._on_click_forgot,
                )
            ]
        )


        self.btn_support = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Suporte",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        #side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    url="https://wa.me/5524998564421"
                )
            ],
        )

        self.infor = ft.Row(
            expand=True,
            controls=[
                ft.TextButton(content='inkers.com.br', expand=True, url='inkers.com.br')
            ]
        )
        

        main_container = ft.Container(
            expand=True,
            content=ft.Column(
                #expand=True,
                controls=[
                    self.logo,
                    #self.txt_username,
                    #self.txt_password,
                    #ft.Container(height=20), # Espaçamento
                    #self.btn_login,
                    self.btn_login_google,
                    #self.btn_create_account,
                    #self.btn_forgot_password,
                    self.btn_support,
                    self.infor
                ],
                #horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                #spacing=15,
            ),

            padding=40,
        )

        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        content=main_container,
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    self.progress_ring,
                ],
            ),
        ]


    def did_mount(self):
       self.page.run_task(self._refresh_token_task)
       
       

    async def _go_to_account(self, e):
        await self.page.push_route("/account")       


    async def _refresh_token_task(self):
        await self.controller.refresh_token(self)        


    async def _on_click_forgot(self, e):
        await self.controller.handler_forgot_password(e, self)         


    async def _on_click_login_google(self, e):
        await self.controller.handle_login_google()


    async def _on_click_login(self, e):
        await self.controller.handle_login(e, self)        