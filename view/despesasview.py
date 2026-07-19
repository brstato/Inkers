import flet as ft
from view.controls.colors import AppColors
from controller.despesascontroller import DespesasController
from view.controls.custongraphics import BackgroundRod, CustombarChart
from view.controls.custonlist import CustonList
from view.controls.custonmodalview import CustonModalView
from view.controls.custontextfield import CustomTextField
from utils.formatcurr import formatar_moeda_brasileira
import flet_charts as flc
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custoncard import CustonCard
import json


class DespesasView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/despesas",
            bgcolor=AppColors.BLACK,
            scroll = ft.ScrollMode.AUTO,
        )

        self.MESES_ABREV = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        self.id_loja:str = '' 
        self.token:str   = '' 
        self.r_token:str = ''

        self.id:int = 0
        
        self.date:str = ''

        self.controller = DespesasController(page, self)

        self.progressring = CustonProgressRing()

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
            on_event=self.on_chart_event
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
            ft.dropdown.Option('ABERTO'),
            ft.dropdown.Option('PAGO')
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
            callback=lambda e: self.create_despesa(e) if self.id == 0 else self.edit_despesa(), 
            callback2=lambda e: self.close_modal_despesa(e),           
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
                    #self.text_total,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=AppColors.ORANGE_DARK,
                        tooltip="Nova Despesa",
                        on_click=self.open_modal_create_despesa
                    )
                ]
            ),
        )        

        self.label_total_a_pagar = ft.Text('Total a pagar: R$ 0,00', color=AppColors.ORANGE_DARK)
        self.label_total_pago = ft.Text('Total pago: R$ 0,00', color=AppColors.GREEN_DARK)
        self.label_total_geral = ft.Text('Total geral: R$ 0,00', color=AppColors.GRAY_LIGHT2)

        self.area_resumo = ft.Row(
            controls=[
                self.label_total_a_pagar,
                self.label_total_pago,
                self.label_total_geral,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            scroll=ft.ScrollMode.AUTO,
        )

        self.controls = [
            ft.Column(
                controls=[
                    self.hero_container,
                    self.area_resumo,
                    self.list,
                ]
            )
        ]


    def close_modal_despesa(self, e):
        self.page.pop_dialog()
        self.page.update()


    def did_mount(self):
        self.page.run_task(self.aux)


    async def aux(self):
        await self.controller.get_data()
        await self.listar_despesas_resumo()
        await self.carregar_categorias()
        self.grafico.update()
        self.page.update()
 

    async def list_despesas_mes(self, date:str):
        try:
            self.progressring.visible = True
            self.page.update()
            self.list.controls.clear()

            message, total, pago, a_pagar = await self.controller.list_despesas_mes(date)

            self.label_total_a_pagar.value = f'Total a pagar: R$ {formatar_moeda_brasileira(a_pagar)}'
            self.label_total_pago.value    = f'Total pago: R$ {   formatar_moeda_brasileira(pago   )}'
            self.label_total_geral.value   = f'Total geral: R$ {  formatar_moeda_brasileira(total  )}'

            #self.text_total.value = f'Total: R$ {formatar_moeda_brasileira(total)}'

            for item in message:

                date = item["data_vencimento"]
                
                card = CustonCard(
                    page=self.page,
                    width=self.page.width,
                    icon=ft.Icons.MONETIZATION_ON,
                    title=item["descricao"],
                    desc=f'Valor: R$ {formatar_moeda_brasileira(item["valor"])}',
                    sub_desc=f'Vencimento: {date.replace("-", "/")}',
                    detail=f'{item["status"]}',
                    sub_detail=f'Parcela: {item["parcela"]}',
                    categoria='',#item["tipo_registro"],
                    id=item["id"],
                    callback=lambda id_depesa:self.delete_despesa(id_depesa),
                    callback2=lambda id_depesa:self.open_modal_edit_despesa(id_depesa),
                    #tap=self.list.on_card_selected
                )
                self.list.controls.append(card)

            self.page.update()
            self.id = 0            
        except Exception as e:
            print(f"Error list_despesas_mes: {e}")
            return
        finally:
            self.progressring.visible = False
            self.page.update()      


    async def open_modal_edit_despesa(self, id_depesa: int):
        try:
            id_despesa, descricao, valor, date, parcela, status = await self.controller.detalhes_despesa(id_depesa)

            self.dp_categoria.text    = descricao
            self.edt_valor.value      = formatar_moeda_brasileira(valor)
            self.edt_vencimento.value = date
            self.parcelas.value       = parcela
            self.status_parcelas.text = status

            self.id = id_despesa

            self.page.show_dialog(self.modal_create_despesa)
        except Exception as e:
            print(f"Error open_modal_edit_despesa: {e}")
            message = "Erro ao editar despesa!"
        
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(message, weight=ft.FontWeight.BOLD),
                    bgcolor=AppColors.ORANGE_DARK,
                )
            )
        self.page.update()              


    async def edit_despesa(self):
        try:
            self.progressring.visible = True
            self.page.update()

            payload = {
                'id_despesa': self.id,
                'descricao': self.dp_categoria.text,
                'valor': self.edt_valor.value,
                'date': self.edt_vencimento.value,
                'parcela': self.parcelas.value,
                'status': self.status_parcelas.text
            }
            
            response = await self.controller.edit_despesa(payload)

            if response:
                message = "Despesa editada com sucesso!"
            else:
                message = "Erro ao editar despesa!"

        except Exception as e:
            print(f"Error edit_despesa: {e}")
            message = "Erro ao editar despesa!"
        finally:
            self.id = 0            
            self.progressring.visible = False            
            self.page.pop_dialog()
            
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(message, weight=ft.FontWeight.BOLD),
                    bgcolor=AppColors.ORANGE_DARK,
                )
            )
            
            await self.list_despesas_mes(self.date)
            await self.listar_despesas_resumo()
            self.page.update()    


    async def delete_despesa(self, id_depesa: int):
        try:
            response = await self.controller.delete_despesa(id_depesa)

            if response:
                message = "Despesa deletada com sucesso!"
            else:
                message = "Erro ao deletar despesa!"

            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(message, weight=ft.FontWeight.BOLD),
                    bgcolor=AppColors.ORANGE_DARK,
                )
            )

        except Exception as e:
            print(f"Error delete_despesa: {e}")
        finally:
            await self.list_despesas_mes(self.date)
            await self.listar_despesas_resumo()
            self.page.update()    


    async def on_chart_event(self, e: flc.BarChartEvent):
        if e.type == flc.ChartEventType.TAP_DOWN and e.rod_index is not None:
            grupo_clicado = self.chart_groups[e.group_index]
            barra_clicada = grupo_clicado.rods[e.rod_index]
            self.date = barra_clicada.date

            for g_index, group in enumerate(self.chart_groups):
                for r_index, rod in enumerate(group.rods):
                    is_selected = (e.group_index == g_index and e.rod_index == r_index)
                    rod.color = AppColors.ORANGE_DARK if is_selected else AppColors.GRAY_LIGHT2
            
            self.grafico.update()
            await self.list_despesas_mes(self.date)


    async def listar_despesas_resumo(self):
        self.progressring.visible = True
        self.page.update()

        message, soma = await self.controller.listar_despesas_resumo()

        novas_labels = []
        valores = [float(iten["total_geral"]) for iten in message]
        maior_valor = max(valores) if valores else 100
        limite_grafico = maior_valor * 1.2 # Dá uma folga de 20% no topo        
        self.chart_groups.clear()
        novas_labels = []

        soma_total = soma["s_total_geral"]
        soma_a_pagar = soma["s_total_a_pagar"]
        soma_pago = soma["s_total_pago"]

        self.label_total_a_pagar.value = f'Total a pagar: R$ {formatar_moeda_brasileira(soma_a_pagar)}'
        self.label_total_pago.value = f'Total pago: R$ {formatar_moeda_brasileira(soma_pago)}'
        self.label_total_geral.value = f'Total geral: R$ {formatar_moeda_brasileira(soma_total)}'

        for i, iten in enumerate(message):
            mes:int             = int(iten["mes"])
            ano:int             = int(iten["ano"])

            total_pago:float    = float(iten["total_pago"   ])
            total_a_pagar:float = float(iten["total_a_pagar"])
            valor_total:float   = float(iten["total_geral"  ])

            nome_mes = self.MESES_ABREV[mes]

            date = f"01/{mes}/{ano}"

            self.chart_groups.append(
                flc.BarChartGroup(
                    x=i,
                    rods=[
                        # Usamos nossa classe customizada aqui
                        BackgroundRod(y=valor_total, max_y=limite_grafico, date=date)
                    ]
                )
            )  

            novas_labels.append(
                flc.ChartAxisLabel(
                    value=i, 
                    label=ft.Text(nome_mes, size=11, color=AppColors.GRAY_LIGHT2, weight=ft.FontWeight.BOLD)
                )
            )

        self.grafico.max_y = limite_grafico    
        self.grafico.bottom_axis.labels = novas_labels
        self.grafico.bottom_axis.show_labels = True
        self.grafico.update()

        self.progressring.visible = False
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
            await self.listar_despesas_resumo()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text('Erro ao salvar despesa'),
                open=True,
            )
            self.page.update()


    async def selected_date_calendar(self, e):
       self.edt_vencimento.value = self.data_vencimento.value.strftime("%d/%m/%Y") 
       self.page.update()              
        
    
