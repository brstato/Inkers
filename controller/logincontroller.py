import flet as ft
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
import json

class LoginController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.LoginModel = LoginModel()


    async def refresh_token(self, view_instance):

        r_token:str = await self.page.client_storage.get_async("r_token")
        id:str      = await self.page.client_storage.get_async("id")

        if r_token:
            view_instance.progress_ring.visible = True
            self.page.update()

            response = await self.LoginModel.refresh_token(
                r_token,
                id
            )

            if response.status_code == 200:
                await self.page.client_storage.set_async("token", json.loads(response.content)["token"]) 
                await self.page.client_storage.set_async("r_token", json.loads(response.content)["r_token"]) 
                self.page.update()
                self.page.go("/main")

            view_instance.progress_ring.visible = False
            self.page.update()


    async def handle_login(self, e, view_instance):
        self.email = view_instance.txt_username.value
        self.password = view_instance.txt_password.value

        if not self.email or not self.password:
            view_instance.progress_ring.visible = False
            dialog = CustonDialog(
                self.page,
                title="Atenção",
                content="Por favor preencha todos os campos.",
                actions=[
                    ft.TextButton('OK', on_click=lambda e: self.page.close(dialog))
                ]
            )
            self.page.open(dialog)          
            self.page.update()
            return

        view_instance.progress_ring.visible = True
        self.page.update()

        response = await self.LoginModel.login(self.email, self.password) 

        if response.status_code == 401:
            view_instance.progress_ring.visible = False
            dialog = CustonDialog(
                self.page,
                title="Erro",
                content="Usuario e ou senha inválida!",
                actions=[
                    ft.TextButton('OK', on_click=lambda e: self.page.close(dialog))
                ]
            )
            self.page.open(dialog)          
            self.page.update()
            return
            
        elif response.status_code != 401:
            view_instance.progress_ring.visible = False
            self.page.client_storage.set("token", json.loads(response.content)["token"]) 
            self.page.client_storage.set("r_token", json.loads(response.content)["r_token"]) 

            message = json.loads(response.content)["message"]

            self.page.client_storage.set("id", message["id"])

            self.page.update()
            self.page.go("/main")


    async def handler_forgot_password(self, e, view_instance):    
        self.email = view_instance.txt_username.value

        if not self.email:
            dialog = CustonDialog(
                self.page,
                title="Atenção",
                content="Por favor informe o email.",
                actions=[
                    ft.TextButton('OK', on_click=lambda e: self.page.close(dialog))
                ]
            )
            self.page.open(dialog)          
            self.page.update()
            return
        
        else:
            view_instance.progress_ring.visible = True
            self.page.update()            

            response = await self.LoginModel.recovery_password(self.email)

            message = json.loads(response.content)

            view_instance.progress_ring.visible = False
            self.page.update()              

            if response.status_code == 200:
                dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content=message["message"],
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(dialog))]
                )
                self.page.open(dialog)
                self.page.update()

            elif response.status_code == 404:
                dialog = CustonDialog(
                    self.page,
                    title="Erro",
                    content=message["message"],
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(dialog))]                    
                )
                self.page.open(dialog)
                self.page.update()