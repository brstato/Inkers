import flet as ft
from controller.productcontroller import ProductController
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList


class ProductView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/product",
            bgcolor=AppColors.BACKGROUND_DARK,
            scroll = ft.ScrollMode.AUTO
        )
        
#        page    = page

        self.width = page.width

        self.id_loja = None
        self.token   = None
        self.r_token = None
        self.id_prod = None

        self.controller  = ProductController(page, self)

        self.edtNome     = CustomTextField(label="Nome do produto:")    

        self.edtValcusto = CustomTextField(label="Valor de custo:",  chars=r"^[0-9,]*$", keyboard_type=ft.KeyboardType.NUMBER,)
        self.edtValVenda = CustomTextField(label="Valor de venda:",  chars=r"^[0-9,]*$", keyboard_type=ft.KeyboardType.NUMBER,)

        self.edtEstoque  = CustomTextField(label="Estoque:",         chars=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER,)
        self.edtMEstoque = CustomTextField(label="Estoque mínimo:",  chars=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER,)

        self.insumo = ft.Switch(
            label="Insumo",
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),
            value=False,
            active_color=AppColors.ORANGE_DARK
        )

        self.Comissionado  = ft.Switch(
            label="Comissionado",
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),            
            value=False,
            active_color=AppColors.ORANGE_DARK
        )        

        self.infvalor  = ft.Switch(
            label="Informar valor na venda",
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT,
                size=18,
            ),            
            value=False,
            active_color=AppColors.ORANGE_DARK
        )   


        self.modalview = CustonModalView(
            page,
            height=650,
            callback=self.controller.editProduct,
            callback2=lambda e:self.close_modal_view(e),
            controls=[
                self.edtNome,
                self.edtValcusto,
                self.edtValVenda,
                self.edtEstoque,
                self.edtMEstoque,
                self.insumo,
                self.Comissionado,
                self.infvalor    
            ],
        )        

        self.modalviewCreateProduct = CustonModalView(
            page,
            height=650,
            callback=self.controller.createProduct,
            callback2=lambda e: self.close_modal_view_create_product(e),
            controls=[
                self.edtNome,
                self.edtValcusto,
                self.edtValVenda,
                self.edtEstoque,
                self.edtMEstoque,
                self.insumo,
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
                value="Produtos",
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
                        on_click=lambda e:page.go("/main")
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
       self.page.run_task(self._get_product_data)


    def open_modal_view(self, e):
        self.edtNome.value = ''
        self.edtValcusto.value = ''
        self.edtValVenda.value = ''
        self.edtEstoque.value = ''
        self.edtMEstoque.value = ''
        self.insumo.value = False
        self.Comissionado.value = False
        self.infvalor.value = False  
        self.page.show_dialog(self.modalviewCreateProduct)
        self.page.update()


    def close_modal_view_create_product(self, e):
        self.page.pop_dialog()
        self.page.update()


    def close_modal_view(self, e):
        self.page.pop_dialog()
        self.page.update()


    async def _get_product_data(self):
        
        self.id_loja: str = self.page.session.store.get("id"     )
        self.token:   str = self.page.session.store.get("token"  )
        self.r_token: str = self.page.session.store.get("r_token")      

        self.controller = ProductController(self.page, self)

        await self.controller.listProductData()         