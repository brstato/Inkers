import flet as ft
from controller.call_api import ProtectedApiCall
from model.relatoriovendasmodel import RelatorioVendasModel
import json
from datetime import datetime
import flet_charts as flc
from view.controls.custongraphics import BackgroundRod
from view.controls.colors import AppColors
from view.controls.custoncard import CustonCard
from utils.formatcurr import formatar_moeda_brasileira
from view.controls.custondialog import CustonDialog



class RelatorioEntradasController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.instance = instance
        self.model = RelatorioVendasModel()

        self.MESES_ABREV = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


    async def venda_detalhes(self, id_venda: int):      
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.entrada_detalhes,
            id_venda=id_venda,
            token=self.instance.r_token
        ).call_api_refresh_token()

        if response.status_code == 200:
            message = json.loads(response.content)["response"]
            return message        


    async def list_vendas_mes(self, month_number:int, year:int):
        self.instance.progress_ring.visible = True
        self.page.update()
        try:
            response  = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.list_vendas_mes,
                month_number=month_number,
                year=year,
                token=self.instance.r_token
            ).call_api_refresh_token()

            message = json.loads(response.content)["response"]

            total       = float(message[0]["total"])
            comissoes   = float(message[0]["comissoes"])
            liquido     = float(message[0]["liquido"])

            self.instance.list.controls.clear()

            self.instance.text_total.value = f'Total: R$ {formatar_moeda_brasileira(total)}, Comisões: R$ {formatar_moeda_brasileira(comissoes)},\n Líquido: R$ {formatar_moeda_brasileira(liquido)}'

            for item in message:

                date = item["data_venda"]
                
                card = CustonCard(
                    page=self.page,
                    width=self.page.width,
                    height=100,
                    icon=ft.Icons.MONETIZATION_ON,
                    title="Venda Realizada",
                    desc=f'Valor: R$ {formatar_moeda_brasileira(item["valor"])}',
                    sub_desc=f'Data: {date.replace("-", "/")}',
                    id=item["id_venda"],
                    callback=None,
                    callback2=None,
                    tap=self.instance.list.on_card_selected,
                    visible_btn=False
                )
                self.instance.list.controls.append(card)

            self.instance.id = 0
            self.instance.progress_ring.visible = False
            self.page.update()            
        except Exception as e:
            self.page.show_dialog(
                CustonDialog(
                    self.page,
                    'Atenção',
                    content=ft.Text(f'ERRO ao buscar vendas do mês: {e}'),
                    actions=[
                        ft.TextButton(
                            'OK',
                            on_click=lambda e: [self.page.pop_dialog(), self.page.update()]
                        )
                    ]
                )
            )    
            self.instance.progress_ring.visible = False
            self.page.update()    
            return
            

    async def on_chart_event(self, e: flc.BarChartEvent):
        if e.type == flc.ChartEventType.TAP_DOWN and e.rod_index is not None:
            grupo_clicado = self.instance.chart_groups[e.group_index]
            barra_clicada = grupo_clicado.rods[e.rod_index]
            self.instance.date = barra_clicada.date

            for g_index, group in enumerate(self.instance.chart_groups):
                for r_index, rod in enumerate(group.rods):
                    is_selected = (e.group_index == g_index and e.rod_index == r_index)
                    rod.color = AppColors.ORANGE_DARK if is_selected else AppColors.GRAY_LIGHT2
            
            self.instance.grafico.update()
            await self.list_vendas_mes(barra_clicada.month_number, barra_clicada.year)


    async def get_data(self):
        self.instance.id_loja = self.page.session.store.get("id"   )
        self.instance.token   = self.page.session.store.get("token")
        self.instance.r_token = self.page.session.store.get("r_token")


    async def listar_vendas_resumo(self):
        self.instance.progress_ring.visible = True
        self.page.update()
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.resume_vendas,
            token=self.instance.token
        ).call_api_refresh_token()

        res = json.loads(response.content)["response"]
        novas_labels = []
        valores = [float(iten["total"]) for iten in res]
        maior_valor = max(valores) if valores else 100
        limite_grafico = maior_valor * 1.2 # Dá uma folga de 20% no topo        
        self.instance.chart_groups.clear()
        novas_labels = []

        for i, iten in enumerate(res):
            mes:int             = int(iten["mes"])
            ano:int             = int(iten["ano"])

            valor_total:float   = float(iten["total"   ])

            nome_mes = self.MESES_ABREV[mes]

            date = f"01/{mes}/{ano}"

            self.instance.chart_groups.append(
                flc.BarChartGroup(
                    x=i,
                    rods=[
                        # Usamos nossa classe customizada aqui
                        BackgroundRod(y=valor_total, max_y=limite_grafico, date=date, month_number=mes, year=ano)
                    ]
                )
            )  

            novas_labels.append(
                flc.ChartAxisLabel(
                    value=i, 
                    label=ft.Text(nome_mes, size=11, color=AppColors.GRAY_LIGHT2, weight=ft.FontWeight.BOLD)
                )
            )

        self.instance.grafico.max_y = limite_grafico    
        self.instance.grafico.bottom_axis.labels = novas_labels
        self.instance.grafico.bottom_axis.show_labels = True
        self.instance.grafico.update()
        self.instance.progress_ring.visible = False
        self.page.update()