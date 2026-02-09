import flet as ft
from controller.call_api import ProtectedApiCall
from model.despesasmodel import despesas_model
import json
from datetime import datetime
import flet_charts as flc
from view.controls.custongraphics import BackgroundRod
from view.controls.colors import AppColors
from view.controls.custoncard import CustonCard
from utils.formatcurr import formatar_moeda_brasileira



class DespesasController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.instance = instance
        self.model = despesas_model()

        self.MESES_ABREV = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


    async def delete_despesa(self, id_despesa:int):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.delete_despesas,
            id_despesa = id_despesa,
            token = self.instance.token
        ).call_api_refresh_token()

        if response.status_code == 200:
            message = "Despesa deletada com sucesso!"
            await self.list_despesas_mes(self.instance.date)
            await self.listar_despesas_resumo()
            
        else:
            message = "Erro ao deletar despesa!"

        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.ORANGE_DARK,
            )
        )
        self.page.update()


    async def list_despesas_mes(self, date:str):
        response  = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.list_despesas_mes,
            id_loja=self.instance.id_loja,
            date=date,
            token=self.instance.token
        ).call_api_refresh_token()

        message = json.loads(response.content)["message"]
        total = json.loads(response.content)["total_periodo"]

        self.instance.list.controls.clear()

        self.instance.text_total.value = f'Total: R$ {formatar_moeda_brasileira(total)}'

        for item in message:

            date = item["data_vencimento"]
            
            card = CustonCard(
                page=self.page,
                width=self.page.width,
                icon=ft.Icons.MONETIZATION_ON,
                title=item["descricao"],
                desc=f'Valor: R$ {formatar_moeda_brasileira(item["valor"])}',
                sub_desc=f'Vencimento: {date}',
                detail=f'{item["status"]}',
                sub_detail=f'Parcela: {item["parcela"]}',
                categoria=item["tipo_registro"],
                id=item["id"],
                callback=lambda id_depesa:self.delete_despesa(id_depesa),
                callback2=None,
                tap=self.instance.list.on_card_selected
            )
            self.instance.list.controls.append(card)

        self.page.update()
        self.instance.id = 0


    async def on_chart_event(self, e: flc.BarChartEvent):
        if e.type == flc.ChartEventType.TAP_DOWN and e.rod_index is not None:
            grupo_clicado = self.instance.chart_groups[e.group_index]
            barra_clicada = grupo_clicado.rods[e.rod_index]
            self.instance.date = barra_clicada.date

            for g_index, group in enumerate(self.instance.chart_groups):
                for r_index, rod in enumerate(group.rods):
                    is_selected = (e.group_index == g_index and e.rod_index == r_index)
                    rod.color = AppColors.ORANGE_DARK if is_selected else AppColors.GRAY_LIGHT2
            
            #print(f"{data_selecionada}")
            self.instance.grafico.update()
            await self.list_despesas_mes(self.instance.date)


    async def get_data(self):
        self.instance.id_loja = await ft.SharedPreferences().get("id"   )
        self.instance.token   = await ft.SharedPreferences().get("token")


    async def listar_despesas_resumo(self):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.resume_despesas,
            id_loja=self.instance.id_loja,
            token=self.instance.token
        ).call_api_refresh_token()

        message = json.loads(response.content)["message"]
        novas_labels = []
        valores = [float(iten["total_geral"]) for iten in message]
        maior_valor = max(valores) if valores else 100
        limite_grafico = maior_valor * 1.2 # Dá uma folga de 20% no topo        
        self.instance.chart_groups.clear()
        novas_labels = []

        for i, iten in enumerate(message):
            mes:int             = int(iten["mes"])
            ano:int             = int(iten["ano"])

            total_pago:float    = float(iten["total_pago"   ])
            total_a_pagar:float = float(iten["total_a_pagar"])
            valor_total:float   = float(iten["total_geral"  ])

            nome_mes = self.MESES_ABREV[mes]

            date = f"01/{mes}/{ano}"

            self.instance.chart_groups.append(
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

        self.instance.grafico.max_y = limite_grafico    
        self.instance.grafico.bottom_axis.labels = novas_labels
        self.instance.grafico.bottom_axis.show_labels = True
        self.instance.grafico.update()