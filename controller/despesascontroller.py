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
from datetime import datetime, timedelta


class DespesasController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.instance = instance
        self.model = despesas_model()

    async def converter_data_serial(self, serial_date) -> str:
        try:
            # Se vier como string do banco, converte para inteiro
            num_dias = int(serial_date)
            # Data base do Delphi/Excel
            data_base = datetime(1899, 12, 30)
            data_final = data_base + timedelta(days=num_dias)
            return data_final.strftime("%d/%m/%Y")
        except Exception:
            return "" # Retorna vazio caso ocorra erro na conversão



    async def edit_despesa(self, payload: dict) -> bool:
        try:
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.edit_despesa,
                payload=payload,
                token=self.instance.token
            ).call_api_refresh_token()

            if response.status_code != 200:
                print(f"Error edit_despesa: {response.status_code} - {response.content}")
                return False
            else:                
                return True
        except Exception as e:
            raise 
    

    async def detalhes_despesa(self, id_despesa: int):
        try:
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.detalhes_despesa,
                id_despesa=id_despesa,
                token=self.instance.token
            ).call_api_refresh_token()

            if response.status_code != 200:
                print(f"Error detalhes_despesa: {response.status_code} - {response.content}")
                return None
            else:
                data = json.loads(response.content)
                
                id_despesa = data['id'             ]
                descricao  = data['descricao'      ]
                valor      = data['valor'          ]
                date       = data['data_vencimento']
                parcela    = data['parcela'        ]
                status     = data['status'         ]

                date = await self.converter_data_serial(date)

                return id_despesa, descricao, valor, date, parcela, status
                
        except Exception as e:
            raise 


    async def create_despesa(self, payload:dict, token:str) -> bool:
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.create_despesa,
            payload=payload,
            token=token
        ).call_api_refresh_token()

        if response.status_code != 200:
            print(f"Error create_despesa: {response.status_code} - {response.content}")
            return False
        else:
            
            return True 

    
    async def list_categorias(self):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.list_categorias,
            token=self.instance.token
        ).call_api_refresh_token()

        return json.loads(response.content)


    async def baixa_despesa(self):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.baixa_despesa,
            id=self.instance.id,
            token=self.instance.token
        ).call_api_refresh_token()  

        if response.status_code == 200:
            message = "Despesa baixada com sucesso!"
            await self.list_despesas_mes(self.instance.date)
            await self.listar_despesas_resumo()
            self.instance.btn_dar_baixa.visible = False
            
        else:
            message = "Erro ao baixar despesa!"

        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.ORANGE_DARK,
            )
        )
        self.page.update()


    async def delete_despesa(self, id_despesa:int) -> bool:
        try:
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.delete_despesas,
                id_despesa = id_despesa,
                token = self.instance.token
            ).call_api_refresh_token()
                
            if response.status_code == 200:
                return True
            else:
                return False                    

        except Exception as e:
            print(f"Error delete_despesa: {e}")
            return False    


    async def list_despesas_mes(self, date:str):
        response  = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.list_despesas_mes,
            id_loja=self.instance.id_loja,
            date=date,
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code != 200:
            print(f"Error list_despesas_mes: {response.status_code} - {response.content}")
            return None

        try:
            data          = json.loads(response.content)
            message       = data.get("message", [])
            total_periodo = data.get("total_periodo", 0)
            total_pago    = data.get("total_pago", 0)
            total_a_pagar = data.get("total_a_pagar", 0)
            
            return message, total_periodo, total_pago, total_a_pagar
        except json.JSONDecodeError:
            print(f"JSONDecodeError in list_despesas_mes: {response.content}")
            return


    async def get_data(self):
        self.instance.id_loja = self.page.session.store.get("id"   )
        self.instance.token   = self.page.session.store.get("token")
        self.instance.r_token = self.page.session.store.get("r_token")


    async def listar_despesas_resumo(self):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.resume_despesas,
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code != 200:
            print(f"Error listar_despesas_resumo: {response.status_code} - {response.content}")
            return

        try:
            data = json.loads(response.content)
            message = data.get("message", [])
            soma = data.get("soma", 0)
            return message, soma
        except json.JSONDecodeError:
            print(f"JSONDecodeError in listar_despesas_resumo: {response.content}")
            return None

