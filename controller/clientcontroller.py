import flet as ft
from view.controls.custoncard import CustonCard
from model.loginmodel import LoginModel
from view.controls.formatcurr import formatar_moeda_brasileira
from model.clientmodel import ClientModel
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

        response = await self.model.createclientData(
            self.instance.edtNome.value,  
            self.instance.edtTelefone.value, 
            self.instance.id_loja,         
            self.instance.edtDtNascimento.value,     
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
            await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await self.page.client_storage.get_async("token")
            self.instance.r_token = await self.page.client_storage.get_async("r_token")          

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.createclientData(
                    self.instance.edtNome.value,  
                    self.instance.edtTelefone.value, 
                    self.instance.id_loja,         
                    self.instance.edtDtNascimento.value,     
                    self.instance.token
                )          

        self.instance.progressRing.visible = False
        self.page.update()   
        await self.listClientData()  



    async def editClient(self, e):

        self.page.close(self.instance.modalview)
        
        self.instance.progressRing.visible = True
        self.page.update()  

        response = await self.model.editclientData(
            self.instance.id_client,
            self.instance.edtNome.value,       
            self.instance.edtTelefone.value, 
            self.instance.edtDtNascimento.value,     
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
            await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await self.page.client_storage.get_async("token")
            self.instance.r_token = await self.page.client_storage.get_async("r_token")

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.editclientData(
                    self.instance.id_client,
                    self.instance.edtNome.value,       
                    self.instance.edtTelefone.value, 
                    self.instance.edtDtNascimento.value,     
                    self.instance.token
                )

        self.id_client = 0

        self.instance.progressRing.visible = False
        self.page.update()  

        await self.listClientData()        



    async def deleteClient(self, id_client):

        self.instance.progressRing.visible = True
        self.page.update()        

        response = await self.model.deleteclientData(id_client, self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:
                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                await self.model.deleteclientData(id_client, self.instance.token)
            else:
                self.page.go("/")    

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listClientData()



    async def listClientData(self, _categoria:str = '', 
                             _row:int=1, _row_to:int=20,
                             _order_maior:bool=False, 
                             _order_menor:bool=False, 
                             _data_ultima_compra:bool=False):

        self.instance.progressRing.visible = True
        self.page.update()

        response = await self.model.getclientData(
            self.instance.id_loja, 
            self.instance.token, 
            _categoria, 
            _row,
            _row_to,
            _order_maior,
            _order_menor,
            _data_ultima_compra
        )

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model.getclientData(
                    self.instance.id_loja, 
                    self.instance.token, 
                    _categoria, 
                    _row,
                    _row_to,                    
                    _order_maior,
                    _order_menor,
                    _data_ultima_compra
                )

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
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
            
            self.instance.list.controls.append(self.instance.navigation)

            self.page.update()

        self.instance.progressRing.visible = False
        self.page.update()  



    async def open_modal_view_detail(self, id):
        self.instance.id_client = id        
        response = await self.model.DetailclientData(id=id, token=self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model.DetailclientData(id=id, token=self.instance.token)
            else:    
                self.page.go("/login")                

        elif response.status_code == 200:
            self.instance.edtNome.value         = json.loads(response.content)["nome"           ]
            self.instance.edtDtNascimento.value = json.loads(response.content)["data_nascimento"]
            self.instance.edtTelefone.value     = json.loads(response.content)["telefone"       ] 
        

            self.page.open(self.instance.modalview)

        self.page.update()    
