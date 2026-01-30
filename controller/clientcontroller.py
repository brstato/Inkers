import flet as ft
from view.controls.custoncard import CustonCard
from model.loginmodel import LoginModel
from controller.call_api import ProtectedApiCall
from utils.formatcurr import formatar_moeda_brasileira
from model.clientmodel import ClientModel
from controller.call_api import ProtectedApiCall
import json



class ClientController:
    def __init__(self, page: ft.Page, instance):
        self.id_prof:int 
        self.instance = instance
        self.page    = page
        self.model   = ClientModel()

        self.dialog  = None    
        
        self.id_loja = self.instance.id_loja
        self.token   = self.instance.token
        self.r_token = self.instance.r_token
  


    async def createClient(self, e):

        self.page.close(self.instance.modalviewCreateClient)
        
        self.instance.progressRing.visible = True
        self.page.update()          

        await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.createclientData,
            nome=self.instance.edtNome.value,
            telefone=self.instance.edtTelefone.value,
            id_loja=self.instance.id_loja,
            aniversario=self.instance.edtDtNascimento.value,
            token=self.instance.token 
        ).call_api_refresh_token()   

        self.instance.progressRing.visible = False
        self.page.update()   
        await self.listClientData()  


    async def editClient(self, e):

        self.page.close(self.instance.modalview)
        
        self.instance.progressRing.visible = True
        self.page.update()  

        await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.editclientData,
            id_client=self.instance.id_client,
            nome=self.instance.edtNome.value,     
            telefone=self.instance.edtTelefone.value,
            aniversario=self.instance.edtDtNascimento.value,
            token=self.instance.token
        ).call_api_refresh_token() 

        self.id_client = 0

        self.instance.progressRing.visible = False
        self.page.update()  

        await self.listClientData()        



    async def deleteClient(self, id_client):

        self.instance.progressRing.visible = True
        self.page.update()        

        await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.deleteclientData,
            id_client=id_client,
            token=self.instance.token
        ).call_api_refresh_token()

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listClientData(e=None)



    async def listClientData(self, e, param:str = ''):

        if not self.instance.token or not self.instance.id_loja:    
            self.page.go("/")
            self.page.update()
            return

        self.instance.progressRing.visible = True
        self.page.update()

        if param == '':
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientData,
                id_loja=self.instance.id_loja,
                token=self.instance.token
            ).call_api_refresh_token()

        elif param == 'a': 
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientDataA,
                id_loja=self.instance.id_loja,
                token=self.instance.token                
            ).call_api_refresh_token()

        elif param == 'b': 
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientDataB,
                id_loja=self.instance.id_loja,
                token=self.instance.token                
            ).call_api_refresh_token()

        elif param == 'c': 
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientDataC,
                id_loja=self.instance.id_loja,
                token=self.instance.token                
            ).call_api_refresh_token()

        elif param == 'maior': 
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientDataMaior,
                id_loja=self.instance.id_loja,
                token=self.instance.token                
            ).call_api_refresh_token()

        elif param == 'menor': 
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.model.getclientDataMenor,
                id_loja=self.instance.id_loja,
                token=self.instance.token                
            ).call_api_refresh_token()                        

        
        array = json.loads(response.content)["message"]
        self.instance.count = json.loads(response.content)["count"]

        self.instance.list.controls.clear()

        for item in array:
            nome          = item["nome"              ]
            telefone      = item["telefone"          ]
            aniversario   = item["data_nascimento"   ]
            ultima_compra = item["data_ultima_compra"]
            id_client     = item["id"                ]
            valor_gasto   = item["v_gasto"           ]
            categoria     = item["categoria"         ]

            card = CustonCard(
                page=self.page,
                width=self.instance.width,
                icon=ft.Icons.PERSON,
                title=nome,
                desc=f'Telefone: {telefone}',
                sub_desc=f'Aniversario: {aniversario}',
                detail=f'Valor gasto: R$ {formatar_moeda_brasileira(valor_gasto)}',
                sub_detail=f'Ultima compra: {ultima_compra}',
                categoria=categoria,
                id=id_client,
                visible_menu=True,
                telefone=telefone,
                callback=lambda id_client: self.deleteClient(id_client),
                tap=self.instance.list.on_card_selected,
                callback2=lambda id_client:self.open_modal_view_detail(id_client)
            )

            self.instance.list.controls.append(card)
        
        self.page.update()

        self.instance.progressRing.visible = False
        self.page.update()  


    async def selected_date_calendar(self, e):
       self.instance.edtDtNascimento.value = self.instance.calendario.value.strftime("%d/%m") 
       self.page.update()


    async def open_modal_view_detail(self, id):
        self.instance.id_client = id        

        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.DetailclientData,
            id_client=id,
            token=self.instance.token
        ).call_api_refresh_token()

        self.instance.edtNome.value         = json.loads(response.content)["nome"           ]
        self.instance.edtDtNascimento.value = json.loads(response.content)["data_nascimento"]
        self.instance.edtTelefone.value     = json.loads(response.content)["telefone"       ] 
        

        self.page.open(self.instance.modalview)

        self.page.update()    
