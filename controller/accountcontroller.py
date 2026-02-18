import flet as ft
from model.accountmodel import AccountModel
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
import json


class AccountController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.model = AccountModel()

        self.dialog = None

        self.instance = instance


    async def get_schedule_json_data(self, view_instance):
        import json
        data = {}
        for item in view_instance.schedule_controls:
            data[item.day_id] = item.get_data()    
        return data     


    async def getAccountData(self, view_instance):
        id: str = self.page.session.store.get("id")
        token: str = self.page.session.store.get("token")
        r_token: str = self.page.session.store.get("r_token")

        if id and r_token:

            view_instance.progressRing.visible = True
            self.page.update()
            
            response = await self.model.getAccountData(id, token)

            if response.status_code == 401:
                response = await LoginModel().refresh_token(r_token, id)
                if response.status_code == 200:
                    self.page.session.store.set("token", json.loads(response.content)["token"])
                    self.page.session.store.set("r_token", json.load(response.content)["r_token"])

                    token: str = self.page.session.store.get("token")
                    r_token: str = self.page.session.store.get("r_token")

                    response = await self.model.getAccountData(id, token)

                    view_instance.txt_username.value = json.loads(response.content)["nome"]
                    view_instance.txt_telefone.value = json.loads(response.content)["telefone"]                
                    view_instance.txt_email.value = json.loads(response.content)["email"]

                    self.page.update()
                else:    
                    self.page.go("/")

            elif response.status_code == 200:
                data = json.loads(response.content)
                view_instance.txt_username.value = data.get("nome", "")
                view_instance.txt_telefone.value = data.get("telefone", "")
                view_instance.txt_email.value    = data.get("email", "")

                horario_data = data.get("horario", {})

                view_instance.load_schedule_data(horario_data)

            if not view_instance.txt_telefone.value:
                dialog = CustonDialog(
                    self.page,
                    'Atenção!',
                    'Complete seus dados.',
                    [
                        ft.TextButton('Ok', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )    
                self.page.show_dialog(dialog)

            view_instance.progressRing.visible = False
            self.page.update()
        else:
            return    


    async def navigation(self, e):
        if self.dialog is not None:
            self.page.pop_dialog()
            self.dialog = None
            self.page.update() 
            
        if self.instance.r_token:
            await self.page.push_route("/main")
        else:
            await self.page.push_route("/")    


    async def handle_save(self, e, view_instance):

        horario_funcionamento = await self.get_schedule_json_data(view_instance)    

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
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update()
                return
        
            if self.password != self.conf_pass:
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="As senhas não coincidem!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
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
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update(), self.page.go("/")])
                    ]
                )
                self.page.show_dialog(self.dialog)  
                return

            if response.status_code == 409:
                self.dialog = CustonDialog(
                    self.page,
                    title="Erro!",
                    content=f"Atenção o nome {self.username} ja esta em uso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog) 
                return                  
                    
        else:
            if not all([self.username, self.telefone, self.email]):
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor preencha todos os campos.",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update()
                return

            if self.password != self.conf_pass:
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="As senhas não coincidem!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
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
                self.token, 
                horario_funcionamento   
            )    

            view_instance.progressRing.visible = False     
            self.page.update()     
            
            if response.status_code == 200:
                self.dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content="Dados atualizados com sucesso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update() 

            elif response.status_code == 401:
                

                response = await LoginModel().refresh_token(r_token, id)
                
                if response.status_code == 200:
                    self.page.session.store.set("token", json.loads(response.content)["token"])
                    self.page.session.store.set("r_token", json.load(response.content)["r_token"])

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
                        token,
                        horario_funcionamento   
                    )    

                    if response.status_code == 200:
                        self.dialog = CustonDialog(
                            self.page,
                            title="Sucesso",
                            content="Dados atualizados com sucesso!",
                            actions=[
                                ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                            ]
                        )
        self.page.update()