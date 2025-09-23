import flet as ft
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
from model.loginmodel import LoginModel
from model.professionalmodel import ProfessionlModel
from model.clientmodel import ClientModel
from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
from model.mainmodel import mainModel
from view.controls.formatcurr import formatar_moeda_brasileira
import json
from view.controls.colors import AppColors
from view.controls.custoncardsimples import CustonCardSimples

class MainController:
    def __init__(self, page:ft.Page, instance):
        
        self.instance = instance
        self.page = page
        self.model = mainModel()
        self.model_professional = ProfessionlModel()
        self.model_clientes = ClientModel()


    async def listItens(self):

        response = await self.model.GetItensData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model.GetItensData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list_itens.controls.clear()

            for item in array:
                id_prod      = item["id"                ]
                name         = item["nome"              ]
                ident        = item["ident_serv"        ]
                estoque      = item["quantidade_estoque"]
                valor        = item["valor_venda"       ]
                inf_valor    = item["inf_valor"         ]
                comissionado = item["comissionado"      ]
                comissao     = item["comissao"          ]

                if ident == 0:
                    icon = ft.Icons.CATEGORY
                elif ident == 1:
                    icon = ft.Icons.MISCELLANEOUS_SERVICES

                card = CustonCardItensVenda(
                    ident_serv=ident,
                    page=self.page,
                    width=self.instance.page.width,
                    instance=self.instance,
                    icon=icon,
                    name=name,
                    id=id_prod,
                    estoque=estoque,
                    valor=valor,
                    inf_valor=inf_valor,
                    comissionado=comissionado,
                    comissao=comissao,
                    tap=self.instance.list_itens.on_card_selected,
                    on_change=self.instance.list_itens.recalculate_total
                )

                self.instance.list_itens.controls.append(card) 
            
            self.page.update()  


    async def listPorfissionais(self):

        response = await self.model_professional.getProfessionalData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model_professional.getProfessionalData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list_profissionais.controls.clear()

            for item in array:
                name      = item["name"]
                id_prof   = item["id"  ]

                card = CustonCardProfessional(
                    instance=self.instance,
                    name=name,
                    id=id_prof,
                    tap=self.instance.list_profissionais.on_card_selected
                )

                self.instance.list_profissionais.controls.append(card) 
            
            self.page.update()
       

    async def listClientes(self):
        response = await self.model.GetClientsData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model.GetClientsData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list_clients.controls.clear()

            for item in array:
                name      = item["nome"]
                id_client = item["id"  ]

                card = CustonCardSimples(
                    page=self.page,
                    title=name,
                    id=id_client,
                    tap=self.instance.list_clients.on_card_selected,
                    instance=self.instance
                )

                self.instance.list_clients.controls.append(card) 
            
            self.page.update()

