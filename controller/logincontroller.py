import flet as ft
from flet.auth.providers import GoogleOAuthProvider
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from controller.call_api import ProtectedApiCall
from urllib.parse import  urlparse
import json

class LoginController:
    def __init__(self, page: ft.Page):
        self.client_id = '184100860737-52caf580q16d4ht8hgkl7ak8p7dr92js.apps.googleusercontent.com'
        self.id_secreto = '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'
        self.page = page
        self.LoginModel = LoginModel()

        self.parsed_url = urlparse(self.page.url)
        self.base_domain = f"https://{self.parsed_url.netloc}/oauth_callback"

        self.provider = GoogleOAuthProvider(
            self.client_id,
            self.id_secreto,
            self.base_domain
        )

        # self.provider.scopes.extend(
        #     [
        #         "https://www.googleapis.com/auth/userinfo.email",
        #         "https://www.googleapis.com/auth/userinfo.profile",
        #         "https://www.googleapis.com/auth/calendar"                
        #     ]
        # )

        self.page.on_login = self.on_login


    def handle_login_google(self, e):
        self.page.login(
            provider=self.provider
            # authorization={
            #     "access_type": "offline", 
            #     "prompt": "consent"                
            # }
        )


    async def on_login(self, e):
        if e.error:
            self.page.open(ft.SnackBar(content=ft.Text(f"Houve um erro: {e.error}")))
            self.page.update()
            print(e.error)
            return
        
        if not self.page.auth.user:
            return
        
        g_user = self.page.auth.user
        
        g_mail = g_user["email"]
        g_id   = g_user["sub"  ]
        g_name = g_user["name"]
        
        g_token = self.page.auth.token.access_token

        try:
          response = await self.LoginModel.login_google(g_mail, g_id, g_token, g_name)

          if response.status_code == 200:
            data = json.loads(response.content)
            await self.page.client_storage.set_async("r_token", data["r_token"])
            await self.page.client_storage.set_async("token",   data["token"  ])
            await self.page.client_storage.set_async("id",      data["message"]["id"])

            self.page.update()
            self.page.go("/main")
          else:
            dialog = CustonDialog(
                self.page,
                title="Erro de Autenticação",
                content=f"Falha ao autenticar com Google no servidor. Status: {response.status_code}",
                actions=[ft.TextButton('OK', on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)
            self.page.update()       
                     
        except Exception as ex:
                    print(f"Erro na requisição ao backend: {ex}")



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
            await self.page.client_storage.set_async("token", json.loads(response.content)["token"]) 
            await self.page.client_storage.set_async("r_token", json.loads(response.content)["r_token"]) 

            message = json.loads(response.content)["message"]

            await self.page.client_storage.set_async("id", message["id"])

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