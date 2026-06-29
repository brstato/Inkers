import flet as ft
from view.controls.colors import AppColors
from controller.relatorioentradascontroller import RelatorioEntradasController
from view.controls.custongraphics import BackgroundRod, CustombarChart
from view.controls.custonlist import CustonList
from view.controls.custonprogressring import CustonProgressRing
import flet_charts as flc
from utils.formatcurr import formatar_moeda_brasileira


class RelatorioEntradasView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/relatorioentradas",
            bgcolor=AppColors.BLACK,
            scroll = ft.ScrollMode.AUTO,
        )

        self.id_loja:str = '' 
        self.r_token:str   = '' 

        self.id:int = 0
        
        self.date:str = ''

        self.progress_ring = CustonProgressRing(page.height)

        self.controller = RelatorioEntradasController(page, self)

        self.text_total = ft.Text(color=AppColors.GRAY_LIGHT2)

        self.text_nome_artista = ft.Text(color=AppColors.GRAY_LIGHT2)
        self.text_nome_cliente = ft.Text(color=AppColors.GRAY_LIGHT2)
        self.text_forma_pagamento = ft.Text(color=AppColors.GRAY_LIGHT2)
        self.text_produto = ft.Text(color=AppColors.GRAY_LIGHT2)

        self.lista_detalhes = CustonList(page, self)

        self.modal_detalhes = ft.BottomSheet(
            bgcolor=AppColors.BLACK,
            content=ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(
                    controls=[
                        self.text_nome_artista,
                        self.text_nome_cliente,
                        self.text_forma_pagamento,
                        self.lista_detalhes,
                    ],
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
            ft.Stack(
                controls =[
                    ft.Column(
                        controls=[
                            self.hero_container,
                            self.list,
                        ]
                    ),
                    self.progress_ring,
                ]
            ),
        ]


    def did_mount(self):
        self.page.run_task(self.aux)


    async def aux(self):
        await self.controller.get_data()
        await self.controller.listar_vendas_resumo()
        self.grafico.update()
        self.page.update()
 

    def update_actions_visibility(self):
        is_visible = self.id != 0
        self.page.show_dialog(self.modal_detalhes)

        self.page.run_task(self.update_modal_detalhes)

  


    async def update_modal_detalhes(self):
        self.progress_ring.visible = True
        self.page.update()

        message = await self.controller.venda_detalhes(self.id)

        self.text_nome_artista.value = f"Artista: {message[0]['nome_artista']}"
        self.text_nome_cliente.value = f"Cliente: {message[0]['nome_cliente']}"
        
        forma_pagamento: str = ''

        if message[0]['dinheiro'] > 0:
            forma_pagamento += f"Dinheiro: R$ {formatar_moeda_brasileira(message[0]['dinheiro'])}"
        if message[0]['pix'] > 0:
            forma_pagamento += f"\nPIX: R$ {formatar_moeda_brasileira(message[0]['pix'])}"
        if message[0]['debito'] > 0:
            forma_pagamento += f"\nDébito: R$ {formatar_moeda_brasileira(message[0]['debito'])}"
        if message[0]['credito'] > 0:
            forma_pagamento += f"\nCrédito: R$ {formatar_moeda_brasileira(message[0]['credito'])}"
        if message[0]['troco'] > 0:
            forma_pagamento += f"\nTroco: R$ {formatar_moeda_brasileira(message[0]['troco'])}"

        self.text_forma_pagamento.value = f"Forma de pagamento: {forma_pagamento}"
        
        self.lista_detalhes.controls.clear()

        for item in message:
            self.lista_detalhes.controls.append(
                ft.Text(
                    f"{item['nome_produto']}: R$ {formatar_moeda_brasileira(item['valor'])} X {item['quantidade']} = R$ {formatar_moeda_brasileira(item['total'])} - Comissão do artista: {formatar_moeda_brasileira(item['comissao'])}"
                )
            )

        self.progress_ring.visible = False
        self.page.update()         

        





