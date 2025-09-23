import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.accountcontroller import AccountController
from view.controls.custonprogressring import CustonProgressRing
import asyncio

class AccountView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/account",
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=0 
        )

        self.page = page

        self.progressRing = CustonProgressRing(self.page.height)             

        self.controller = AccountController(self.page)    

        self.txt_username = CustomTextField("Usuário") 
        self.txt_telefone = CustomTextField("Telefone", chars=r"^[0-9]*$") 
        self.txt_email    = CustomTextField("e-mail") 
        self.txt_password = CustomTextField("Senha", password=True, can_reveal_password=True) 
        self.txt_conf_password = CustomTextField("Confirme a senha", password=True, can_reveal_password=True)

        self.btn_save = ft.Row(
            controls=[
                ft.ElevatedButton(
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, AppColors.GRAY_DARK),
                    ),
                    expand=True,
                    height=45,
                    elevation=5,
                    text='Salvar',
                    bgcolor=AppColors.ORANGE_BURNT,
                    color=AppColors.GRAY_LIGHT,

                    on_click=lambda e:asyncio.run(self.controller.handle_save(e, self))
                )
            ],
        )


        self.btn_return = ft.Row(
            controls=[
                ft.OutlinedButton(
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    text='Voltar',
                    on_click=lambda e:self.controller.navigation(e, self.id)
                )
            ],
        )        

        main_container = ft.Container(
            padding=ft.padding.all(20),
            bgcolor=AppColors.BACKGROUND_DARK,
            content=ft.Column(
                controls=[
                    self.txt_username,
                    self.txt_telefone,
                    self.txt_email,
                    self.txt_password,
                    self.txt_conf_password,
                    ft.Container(height=20),
                    self.btn_save,
                    self.btn_return 
                ],
            ),
        )

        self.controls = [
            ft.Stack(
                controls=[
                    ft.Container(
                        content=main_container,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                    self.progressRing
                ],
            ),
        ]


    def did_mount(self):
       self.page.run_task(self._getAccountData)


    async def _getAccountData(self):
        self.id      = await self.page.client_storage.get_async("id")
        self.token   = await self.page.client_storage.get_async("token")
        self.r_token = await self.page.client_storage.get_async("r_token") 

        await self.controller.getAccountData(self)          