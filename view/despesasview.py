import flet as ft
from view.controls.colors import AppColors
from controller.despesascontroller import DespesasController
from view.controls.custongraphics import BackgroundRod, CustombarChart
from view.controls.custonlist import CustonList
from view.controls.custonmodalview import CustonModalView
from view.controls.custontextfield import CustomTextField
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
        self.r_token:str = ''

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

        self.text_total = ft.Text('Total: R$ 0,00', color=AppColors.ORANGE_DARK)

        self.btn_dar_baixa = ft.Button(
            content='Dar baixa',
            bgcolor=AppColors.ORANGE_BURNT,
            color=AppColors.GRAY_LIGHT,
            visible=False,
            on_click=self.controller.baixa_despesa
        )

        # Criando os grupos usando a classe correta do flet_charts
        self.chart_groups = []

        self.grafico = CustombarChart(
            groups=self.chart_groups,
            on_event=self.controller.on_chart_event
        )

        self.options_categorias = []

        self.dp_categoria = ft.Dropdown(
            label='Despesas',
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            elevation=5,
            editable=True,
            enable_filter=True,
            expand=True,
            enable_search=True,
            menu_height=300,
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,           
            #on_text_change=self.controller.on_client_selected
        )

        self.edt_valor = CustomTextField(
            label='Valor',
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.data_vencimento = ft.DatePicker(
            on_change=self.selected_date_calendar
        )

        self.edt_vencimento = CustomTextField(
            label='Data do vencimento',
            readOnly=True,
            keyboard_type=ft.KeyboardType.DATETIME,
            regex=r"[0-9/]"
        )        

        self.date_area = ft.Stack(
            controls=[
                self.edt_vencimento,
                ft.IconButton(
                    icon=ft.Icons.DATE_RANGE,
                    icon_color=AppColors.GRAY_LIGHT2,
                    right=5,
                    on_click=lambda e:[page.show_dialog(self.data_vencimento), page.update()]
                )                
            ]
        )        


        self.parcelas = CustomTextField(
            label='Quantidade de parcelas',
            keyboard_type=ft.KeyboardType.NUMBER,
            regex=r"[0-9]"
        )

        self.options_status = [
            ft.dropdown.Option('Pendente'),
            ft.dropdown.Option('Pago')
        ]

        self.status_parcelas = ft.Dropdown(
            label='Status',
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            elevation=5,
            editable=False,
            enable_filter=False,
            expand=True,
            enable_search=False,
            menu_height=100,
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,   
            options=self.options_status,      
        )

        self.modal_create_despesa = CustonModalView(
            height=470,
            page=page,
            controls=[
                self.dp_categoria,
                self.edt_valor,
                self.date_area,
                self.parcelas,
                self.status_parcelas
            ],
            callback2=self.open_modal_create_despesa,
            callback=lambda e: self.create_despesa(e),            
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
                    self.btn_dar_baixa,
                    self.text_total,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=AppColors.ORANGE_DARK,
                        tooltip="Nova Despesa",
                        on_click=self.open_modal_create_despesa
                    )
                ]
            ),
        )        

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
        await self.carregar_categorias()
        self.grafico.update()
        self.page.update()
 

    def update_actions_visibility(self):
        is_visible = self.id != 0
        self.btn_dar_baixa.visible = is_visible
        self.appbar.update()


    async def open_modal_create_despesa(self, e):       
        self.dp_categoria.value     = ''
        self.edt_valor.value        = ''
        self.edt_vencimento.value   = ''
        self.parcelas.value         = ''
        self.status_parcelas.value  = ''        
        
        self.page.show_dialog(self.modal_create_despesa)
        self.page.update()


    async def carregar_categorias(self):
        response = await self.controller.list_categorias()
       
        self.dp_categoria.options.clear()
        self.options_categorias.clear()

        for categoria in response['response']:
            self.options_categorias.append(
                ft.dropdown.Option(
                    key=categoria['descricao'],
                    style=ft.ButtonStyle(
                        color=AppColors.GRAY_LIGHT2,                    
                    ),
                    text=categoria['descricao']                 
                )
            )
        self.dp_categoria.options = self.options_categorias


    async def create_despesa(self, e):
        payload = {
            "descricao": self.dp_categoria.text,
            "valor":     self.edt_valor.value,
            "date":      self.edt_vencimento.value,
            "qtd":       self.parcelas.value,
            "status":    self.status_parcelas.value,
        }

        response = await self.controller.create_despesa(payload, self.token)

        if response:
            self.page.pop_dialog()
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text('Erro ao salvar despesa'),
                open=True,
            )
            self.page.update()


    async def selected_date_calendar(self, e):
       self.edt_vencimento.value = self.data_vencimento.value.strftime("%d/%m/%Y") 
       self.page.update()              
        
    
