import flet as ft
from view.controls.colors import AppColors
from controller.despesascontroller import DespesasController
from view.controls.custongraphics import BackgroundRod, CustombarChart
from view.controls.custonlist import CustonList
import flet_charts as flc


class DespesasView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/despesas",
            bgcolor=AppColors.BLACK,
            scroll = ft.ScrollMode.AUTO,
        )

        self.id_loja:str = '' 
        self.token:str   = '' 

        self.id:int = 0
        
        self.date:str = ''

        self.controller = DespesasController(page, self)

        self.edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color=AppColors.ORANGE_DARK,
            visible=False,
            on_click=lambda e: print("Editar") # Placeholder
        )

        self.delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=AppColors.ORANGE_DARK,
            visible=False,
            on_click=lambda e: page.run_task(self.controller.delete_despesa, self.id)
        )

        self.appbar = ft.AppBar(
            title=ft.Text('Despesas', color=AppColors.ORANGE_DARK),
            bgcolor=AppColors.GRAY_DARK,
            actions=[
                self.edit_btn,
                self.delete_btn,
            ]
        )

        self.text_total = ft.Text('Total: R$ 0,00', color=AppColors.ORANGE_DARK)

        self.bottom_appbar = ft.BottomAppBar(
            height=60,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME, 
                        icon_color=AppColors.ORANGE_DARK,
                        on_click=lambda e:page.go("/main")
                    ),
                    ft.Container(expand=True),
                    self.text_total,
                ]
            ),
        )

        # Criando os grupos usando a classe correta do flet_charts
        self.chart_groups = []

        self.grafico = CustombarChart(
            groups=self.chart_groups,
            on_event=self.controller.on_chart_event
        )

        self.hero_container = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),             
            content=self.grafico,
            height=180,
            padding=ft.Padding.all(10),
            border_radius=ft.border_radius.all(10),
        )

        self.list = CustonList(page=page, instance=self)

        self.controls = [
            ft.Column(
                controls=[
                    self.hero_container,
                    self.list,
                ]
            )
        ]


    def did_mount(self):
        self.page.run_task(self.aux)


    async def aux(self):
        await self.controller.get_data()
        await self.controller.listar_despesas_resumo()
        self.grafico.update()
        self.page.update()
 

    def update_actions_visibility(self):
        is_visible = self.id != 0
        self.edit_btn.visible = is_visible
        self.delete_btn.visible = is_visible
        self.appbar.update()