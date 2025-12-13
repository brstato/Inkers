import flet as ft
from controller.servicecontroller import ServiceController
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList


class ServiceView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/services",
            bgcolor=AppColors.BACKGROUND_DARK,
            scroll = ft.ScrollMode.AUTO
        )
        
        self.page    = page

        self.width = self.page.width

        self.id_loja = None
        self.token   = None
        self.r_token = None
        self.id_serv = None

        self.controller  = ServiceController(self.page, self)

        self.edtNome     = CustomTextField(label="Nome do produto:")    
        self.edtValcusto = CustomTextField(label="Valor de custo:", chars=r"^[0-9,]*$")
        self.edtValVenda = CustomTextField(label="Valor de venda:", chars=r"^[0-9,]*$")
        self.edtComissao = CustomTextField(label="Comissão do serviço em %:", chars=r"^[0-9]*$")

        self.Comissionado  = ft.Switch(
            label="Comissionado",
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),            
            value=False,
            active_color=AppColors.ORANGE_DARK
        )        


        self.infvalor  = ft.Switch(
            label="Informar valor na venda",
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),            
            value=False,
            active_color=AppColors.ORANGE_DARK
        )   


        self.modalviewCreateService = CustonModalView(
            self.page,
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
            self.page,
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
        self.list = CustonList(self.page)
        self.progressRing = CustonProgressRing(self.page.height)  
        
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
        self.page.open(self.modalviewCreateService)
        self.page.update()


    def close_modal_view_create_service(self, e):
        self.page.close(self.modalviewCreateService)
        self.page.update()


    def close_modal_view(self, e):
        self.page.close(self.modalview)
        self.page.update()


    async def _get_service_data(self):
        
        self.id_loja: str = await self.page.client_storage.get_async("id"     )
        self.token:   str = await self.page.client_storage.get_async("token"  )
        self.r_token: str = await self.page.client_storage.get_async("r_token")      

        self.controller = ServiceController(self.page, self)

        await self.controller.listServiceData()         