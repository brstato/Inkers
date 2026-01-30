import asyncio
import flet as ft
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from controller.professionalcontroller import ProfessionalController
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList


class ProfessionalView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/professional",
            bgcolor=AppColors.BACKGROUND_DARK,
            scroll = ft.ScrollMode.AUTO
        )
        
#        self.page    = page

        self.width = page.width
        
        self.id_loja = None
        self.token   = None
        self.r_token = None
        self.id_prof = None
        self.controller = ProfessionalController(page, self)
        self.edtName     = CustomTextField(label="Nome do profissional:")    
        self.edtTelefone = CustomTextField(label="Telefone:", chars=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER,)
        self.edtComissao = CustomTextField(label="Comissão, %:", chars=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER,)


        self.modalviewCreateProfessional = CustonModalView(
            page,
            callback=self.controller.createProfessional,
            callback2=self.close_modal_view,
            controls=[
                self.edtName,
                self.edtTelefone,
                self.edtComissao
            ],  
            height=320,          
        )        
        
        self.modalview = CustonModalView(
            page,
            callback=self.controller.editProfessional,
            callback2=self.close_modal_view,
            controls=[
                self.edtName,
                self.edtTelefone,
                self.edtComissao
            ],
            height=320,
        )

        self.selected_card = None
        self.list = CustonList(page)
        self.progressRing = CustonProgressRing(page.height)  
        
        self.appbar = ft.AppBar(
            automatically_imply_leading=False,
            bgcolor=AppColors.GRAY_DARK,
            title=ft.Text(
                value="Profissionais",
                style=ft.TextStyle(
                    color=AppColors.ORANGE_DARK,
                ),
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
                        on_click=lambda _:self.page.go("/main")
                    ),
                    ft.Container(
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=lambda e: self.open_modal_view(e)
                    ),
                ],
            )
        )


        self.controls = [
            ft.Stack(
                controls=[
                    self.list,
                    self.progressRing
                ],
            ),
        ]


    def did_mount(self):
       self.page.run_task(self._get_professional_data)


    def open_modal_view(self, e):
        self.edtName.value = ''
        self.edtTelefone.value = ''
        self.edtComissao.value = ''
        self.page.show_dialog(self.modalviewCreateProfessional)
        self.page.update()


    def close_modal_view_create_professional(self):
        self.page.pop_dialog()
        self.page.update()


    def close_modal_view(self, e):
        self.page.pop_dialog()
        self.page.update()


    async def _get_professional_data(self):
        
        self.id_loja: str = await ft.SharedPreferences().get("id"     )
        self.token:   str = await ft.SharedPreferences().get("token"  )
        self.r_token: str = await ft.SharedPreferences().get("r_token")      

        self.controller = ProfessionalController(self.page, self)

        await self.controller.listProfessionalData()         