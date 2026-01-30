import flet as ft
from view.controls.custoncard import CustonCard
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from utils.formatcurr import formatar_moeda_brasileira
from model.servicemodel import ServiceModel
import json
import asyncio

class ServiceController:
    def __init__(self, page: ft.Page, instance):
        self.id_prof:int 
        self.instance = instance
        self.page    = page
        self.model   = ServiceModel()

        self.dialog  = None    
        
        self.id_loja = self.instance.id_loja
        self.token   = self.instance.token
        self.r_token = self.instance.r_token
  


    async def createService(self, e):

        self.page.pop_dialog(self.instance.modalviewCreateService)
        
        self.instance.progressRing.visible = True
        self.page.update()          

        response = await self.model.createServiceData(
            self.instance.edtNome.value,
            self.instance.infvalor.value,   
            self.instance.id_loja,         
            self.instance.Comissionado.value,
            self.instance.edtValcusto.value,
            self.instance.edtValVenda.value,      
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")          

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.createServiceData(
                    self.instance.edtNome.value,
                    self.instance.infvalor.value,  
                    self.instance.id_loja,         
                    self.instance.Comissionado.value,
                    self.instance.edtValcusto.value,
                    self.instance.edtValVenda.value,      
                    self.instance.token
                )          

        self.instance.progressRing.visible = False
        self.page.update()   
        await self.listServiceData()  


    async def editService(self, e):

        self.page.pop_dialog(self.instance.modalview)
        
        self.instance.progressRing.visible = True
        self.page.update()  

        response = await self.model.editServiceData(
            self.instance.id_prod,
            self.instance.edtNome.value,
            self.instance.infvalor.value,             
            self.instance.Comissionado.value,
            self.instance.edtValcusto.value,
            self.instance.edtValVenda.value,      
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.editServiceData(
                    self.instance.id_prod,
                    self.instance.edtNome.value,
                    self.instance.infvalor.value,            
                    self.instance.Comissionado.value,
                    self.instance.edtValcusto.value,
                    self.instance.edtValVenda.value,      
                    self.instance.token
                )

        self.id_prod = 0

        self.instance.progressRing.visible = False
        self.page.update()  

        await self.listServiceData()        



    async def deleteServicet(self, id_prof):

        self.instance.progressRing.visible = True
        self.page.update()        

        response = await self.model.deleteServiceData(id_prof, self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:
                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                await self.model.deleteServiceData(id_prof, self.instance.token)
            else:
                self.page.go("/")    

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listServiceData()



    async def listServiceData(self):

        if not self.instance.token or not self.instance.id_loja:    
            self.page.go("/")
            self.page.update()
            return

        self.instance.progressRing.visible = True
        self.page.update()

        response = await self.model.getServiceData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.getServiceData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list.controls.clear()

            for item in array:
                name      = item["nome"       ]
                margem    = item["margem"     ]
                v_vendido = item["vendas"     ]
                v_custo   = item["valor_custo"]
                v_venda   = item["valor_venda"]
                id_serv   = item["id"         ]

                card = CustonCard(
                    page=self.page,
                    width=self.instance.width,
                    icon=ft.Icons.MISCELLANEOUS_SERVICES,
                    title=name,
                    desc=f'Custo: {formatar_moeda_brasileira(v_custo)} | Venda: {formatar_moeda_brasileira(v_venda)}',
                    sub_desc=f'Margem: {margem}%',
                    detail=f'Vendido: {formatar_moeda_brasileira(v_vendido)}',
                    id=id_serv,
                    callback=lambda id_serv: self.deleteServicet(id_serv),
                    tap=self.instance.list.on_card_selected,
                    callback2=lambda id_serv:self.open_modal_view_detail(id_serv)
                )

                self.instance.list.controls.append(card) 
            
            self.page.update()

        self.instance.progressRing.visible = False
        self.page.update()    




    async def open_modal_view_detail(self, id):
        self.instance.id_prod = id        
        response = await self.model.DetailServiceData(id=id, token=self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.DetailServiceData(id=id, token=self.instance.token)
            else:    
                self.page.go("/login")                

        elif response.status_code == 200:
            data = json.loads(response.content)

            self.instance.edtValcusto.value  = formatar_moeda_brasileira(data.get("valor_custo", 0))
            self.instance.edtValVenda.value  = formatar_moeda_brasileira(data.get("valor_venda", 0))
            
            self.instance.edtNome.value      = data.get("nome", 0)

            infvalor:bool = bool(data.get("inf_valor",    False))
            Comissionado:bool = bool(data.get("comissionado", False))

            self.instance.infvalor.value     = infvalor
            self.instance.Comissionado.value = Comissionado

            self.page.show_dialog(self.instance.modalview)
        self.page.update()    
