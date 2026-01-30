import flet as ft
from view.controls.custoncard import CustonCard
from model.professionalmodel import ProfessionlModel
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from utils.formatcurr import formatar_moeda_brasileira
import json
import asyncio

class ProfessionalController:
    def __init__(self, page: ft.Page, instance):
        self.id_prof:int 
        self.instance = instance
        self.page    = page
        self.model   = ProfessionlModel()

        self.dialog  = None    
        
        self.id_loja = self.instance.id_loja
        self.token   = self.instance.token
        self.r_token = self.instance.r_token
  


    async def createProfessional(self, e):

        self.page.pop_dialog()
        
        self.instance.progressRing.visible = True
        self.page.update()          

        response = await self.model.createProfessionalData(
            self.instance.id_loja,
            self.instance.edtName.value,
            self.instance.edtTelefone.value,
            self.instance.edtComissao.value,
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")
            if response.status_code != 200:
                await self.page.push_route("/")

            else:
                await self.model.createProfessionalData(
                    self.instance.id_loja,
                    self.instance.edtName.value,
                    self.instance.edtTelefone.value,
                    self.instance.edtComissao.value,
                    self.instance.token
                )         

        self.instance.progressRing.visible = False
        self.page.update()   
        await self.listProfessionalData()  


    async def editProfessional(self, e):

        self.page.pop_dialog()
        
        self.instance.progressRing.visible = True
        self.page.update()  

        response = await self.model.editProfessionalData(
            self.instance.id_prof,
            self.instance.edtName.value,
            self.instance.edtTelefone.value,
            self.instance.edtComissao.value,
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")

            if response.status_code != 200:
                await self.page.push_route("/")

            else:
                response = await self.model.editProfessionalData(
                    self.instance.id_prof,
                    self.instance.edtName.value,
                    self.instance.edtTelefone.value,
                    self.instance.edtComissao.value,
                    self.instance.token
                )    

        self.id_prof = 0

        self.instance.progressRing.visible = False
        self.page.update()  

        await self.listProfessionalData()        



    async def deleteProfessional(self, id_prof):

        self.instance.progressRing.visible = True
        self.page.update()        

        response = await self.model.deleteProfessionalData(id_prof, self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:
                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                await self.model.deleteProfessionalData(id_prof, self.instance.token)
            else:
                self.page.push_route("/")    

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listProfessionalData()



    async def listProfessionalData(self):

        if not self.instance.token or not self.instance.id_loja:    
            self.page.push_route("/")
            self.page.update()
            return

        self.instance.progressRing.visible = True
        self.page.update()

        response = await self.model.getProfessionalData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.getProfessionalData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.push_route("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list.controls.clear()

            for item in array:
                name      = item["name"     ]
                telefone  = item["telefone" ]
                comissao  = item["comissao" ]
                v_vendido = item["v_vendido"]
                id_prof   = item["id"       ]

                card = CustonCard(
                    page=self.page,
                    width=self.instance.width,
                    icon=ft.Icons.PERSON,
                    title=name,
                    desc=f'Tel.: {telefone}',
                    detail=f'Vendas: R$ '+formatar_moeda_brasileira(v_vendido),
                    id=id_prof,
                    callback=lambda id_prof: self.deleteProfessional(id_prof),
                    tap=self.instance.list.on_card_selected,
                    callback2=lambda id_prof:self.open_modal_view_detail(id_prof)
                )

                self.instance.list.controls.append(card) 
            
            self.page.update()

        self.instance.progressRing.visible = False
        self.page.update()    




    async def open_modal_view_detail(self, id):
        self.instance.id_prof = id        
        response = await self.model.DetailProfessionalData(id=id, token=self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.DetailProfessionalData(id=id, token=self.instance.token)
            else:    
                self.page.push_route("/login")                

        elif response.status_code == 200:
            self.instance.edtName.value     = json.loads(response.content)["nome"    ]
            self.instance.edtTelefone.value = json.loads(response.content)["telefone"]
            self.instance.edtComissao.value = json.loads(response.content)["comissao"]

            self.page.show_dialog(self.instance.modalview)

        self.page.update()    
