import flet as ft
from controller.servicecontroller import ServiceController
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList
import asyncio

class ServiceView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/services",
            bgcolor=AppColors.BACKGROUND_DARK,
            scroll = ft.ScrollMode.AUTO
        )
        
        #page    = page

        self.width = page.width

        self.id_loja = None
        self.token   = None
        self.r_token = None
        self.id_serv = None

        self.controller  = ServiceController(page, self)

        self.edtNome     = CustomTextField(label="Nome do produto:")    
        self.edtValcusto = CustomTextField(label="Valor de custo:", chars=r"^[0-9,]*$", keyboard_type=ft.KeyboardType.NUMBER,)
        self.edtValVenda = CustomTextField(label="Valor de venda:", chars=r"^[0-9,]*$", keyboard_type=ft.KeyboardType.NUMBER,)
        self.edtComissao = CustomTextField(label="Comissão do serviço em %:", chars=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER,)

        self.Comissionado  = ft.Switch(
            label="Comissionado",            
            value=False,
            active_color=AppColors.ORANGE_DARK,
                        label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),
        )        


        self.infvalor  = ft.Switch(
            label="Informar valor na venda",          
            value=False,
            active_color=AppColors.ORANGE_DARK,
                        label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),
        )   


        self.modalviewCreateService = CustonModalView(
            page,
            height=500,
            callback=self.controller.createService,
            callback2=self.close_modal_view_create_service,
            controls=[
                self.edtNome,
                self.edtValcusto,
                self.edtValVenda,
                self.Comissionado,
                self.infvalor                
            ],            
        )        
        
        self.modalview = CustonModalView(
            page,
            height=450,
            callback=self.controller.editService,
            callback2=self.close_modal_view,
            controls=[
                self.edtNome,
                self.edtValcusto,
                self.edtValVenda,
                self.Comissionado,
                self.infvalor    
            ],
        )

        self.selected_card = None
        self.list = CustonList(page)
        self.progressRing = CustonProgressRing(page.height)  
        
        self.appbar = ft.AppBar(
            automatically_imply_leading=False,
            bgcolor=AppColors.GRAY_DARK,
            title=ft.Text(
                value="Serviços",
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
                        on_click=lambda e:self.page.go("/main")
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
       self.page.run_task(self._get_service_data)


    def open_modal_view(self, e):
        self.edtNome.value = ''
        self.edtValcusto.value = ''
        self.edtValVenda.value = ''
        self.Comissionado.value = False
        self.infvalor.value = False  
        self.page.show_dialog(self.modalviewCreateService)
        self.page.update()


    def close_modal_view_create_service(self, e):
        self.page.pop_dialog()
        self.page.update()


    def close_modal_view(self, e):
        self.page.pop_dialog()
        self.page.update()


    async def _get_service_data(self):
        
        self.id_loja: str = await ft.SharedPreferences().get("id"     )
        self.token:   str = await ft.SharedPreferences().get("token"  )
        self.r_token: str = await ft.SharedPreferences().get("r_token")      

        self.controller = ServiceController(self.page, self)

        await self.controller.listServiceData()         