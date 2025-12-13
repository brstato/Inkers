import flet as ft
from model.accountmodel import AccountModel
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
import json


class AccountController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.model = AccountModel()

        self.dialog = None

        self.r_token:str = ''


    async def getAccountData(self, view_instance):
        id: str = await self.page.client_storage.get_async("id")
        token: str = await self.page.client_storage.get_async("token")
        r_token: str = await self.page.client_storage.get_async("r_token")

        if (id == '') or (r_token == ''):
            return

        view_instance.progressRing.visible = True
        self.page.update()
        
        response = await self.model.getAccountData(id, token)

        if response.status_code == 401:
            response = await LoginModel().refresh_token(r_token, id)
            if response.status_code == 200:
                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                token: str = await self.page.client_storage.get_async("token")
                r_token: str = await self.page.client_storage.get_async("r_token")

                response = await self.model.getAccountData(id, token)

                view_instance.txt_username.value = json.loads(response.content)["nome"]
                view_instance.txt_telefone.value = json.loads(response.content)["telefone"]                
                view_instance.txt_email.value = json.loads(response.content)["email"]

                self.page.update()
            else:    
                self.page.go("/")

        elif response.status_code == 200:
            view_instance.txt_username.value = json.loads(response.content)["nome"]
            view_instance.txt_telefone.value = json.loads(response.content)["telefone"]                
            view_instance.txt_email.value = json.loads(response.content)["email"]

        view_instance.progressRing.visible = False
        self.page.update()


    def navigation(self, e, id:str = None):
        if self.dialog is not None:
            self.page.close(self.dialog)
            self.dialog = None
            self.page.update() 
        if self.r_token != '' or self.r_token is not None:
            self.page.go("/main")
            self.page.update()
        else:
            self.page.go("/")    


    async def handle_save(self, e, view_instance):

        self.username = view_instance.txt_username.value
        self.telefone = view_instance.txt_telefone.value
        self.email    = view_instance.txt_email.value
        self.password = view_instance.txt_password.value
        self.conf_pass= view_instance.txt_conf_password.value

        self.id:str      = view_instance.id
        self.token:str   = view_instance.token
        self.r_token = view_instance.r_token

        if not self.r_token:

            if not all([self.username, self.telefone, self.email, self.password, self.conf_pass]):
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor preencha todos os campos.",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update()
                return
        
            if self.password != self.conf_pass:
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="As senhas não coincidem!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update()
                return    
        
            view_instance.progressRing.visible = True
            self.page.update()

            response = await self.model.register(
                self.username,
                self.telefone,
                self.email,
                self.password
            )    

            view_instance.progressRing.visible = False         
            
            if response.status_code == 200:
                self.dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content="Conta criada com sucesso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update()    
                    
        else:
            if not all([self.username, self.telefone, self.email]):
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor preencha todos os campos.",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update()
                return

            if self.password != self.conf_pass:
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="As senhas não coincidem!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update()
                return                

            view_instance.progressRing.visible = True
            self.page.update()

            response = await self.model.updateAccountData(
                self.id,
                self.username,
                self.telefone,
                self.email,
                self.password,
                self.token
            )    

            view_instance.progressRing.visible = False     
            self.page.update()     
            
            if response.status_code == 200:
                self.dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content="Dados atualizados com sucesso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.close(self.dialog), self.page.update()])
                    ]
                )
                self.page.open(self.dialog)          
                self.page.update() 

            elif response.status_code == 401:
                

                response = await LoginModel().refresh_token(r_token, id)
                
                if response.status_code == 200:
                    await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                    await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                    token: str = json.loads(response.content)["token"]
                    r_token: str = json.load(response.content)["r_token"]

                    view_instance.token  = token
                    view_instance.r_token = r_token

                    response = await self.model.updateAccountData(
                        id,
                        self.username,
                        self.telefone,
                        self.email,
                        self.password,
                        token
                    )    

                    if response.status_code == 200:
                        self.dialog = CustonDialog(
                            self.page,
                            title="Sucesso",
                            content="Dados atualizados com sucesso!",
                            actions=[
                                ft.TextButton('OK', on_click=lambda e:[self.page.close(self.dialog), self.page.update()])
                            ]
                        )
        self.page.update()