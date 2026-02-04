import flet as ft
from flet.auth.providers import GoogleOAuthProvider
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from controller.call_api import ProtectedApiCall
from urllib.parse import  urlparse
import json
import os
from datetime import datetime
import requests

class LoginController:
    def __init__(self, page: ft.Page):
        self.client_id = '184100860737-52caf580q16d4ht8hgkl7ak8p7dr92js.apps.googleusercontent.com'
        self.id_secreto = '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'
        #self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        #self.id_secreto = os.getenv('GOOGLE_CLIENT_SECRET')
        self.page = page
        self.LoginModel = LoginModel()
        self.token_obj:str=None

        self.parsed_url = urlparse(self.page.url)
        self.base_domain = f"https://{self.parsed_url.netloc}/oauth_callback"

        self.provider = GoogleOAuthProvider(
            self.client_id,
            self.id_secreto,
            self.base_domain
        )

        self.provider.scopes.extend(
            [
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/calendar"                
            ]
        )

        self.provider.authorization_endpoint += "?access_type=offline&prompt=consent"

        self.page.on_login = self.on_login


    async def handle_login_google(self):
        await self.page.login(
            provider=self.provider
        )


    async def on_login(self, e):

        if e.error:
            self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Houve um erro: {e.error}")))
            self.page.update()
            print(e.error)
            return

        token_obj = await self.page.auth.get_token()  

        await ft.SharedPreferences().set("google_access_token", token_obj.access_token)
        await ft.SharedPreferences().set("google_refresh_token", token_obj.refresh_token)

        refresh = token_obj.refresh_token

        g_user = self.page.auth.user
        
        g_mail = g_user["email"]
        g_id   = g_user["sub"  ]
        g_name = g_user["name"]
        
        g_token = token_obj.access_token

        try:
          response = await self.LoginModel.login_google(g_mail, g_id, g_token, g_name)

          if response.status_code == 200:
            data = json.loads(response.content)
            await ft.SharedPreferences().set("r_token", data["r_token"])
            await ft.SharedPreferences().set("token",   data["token"  ])
            await ft.SharedPreferences().set("id",      data["message"]["id"])

            self.page.update()
            self.page.go("/main")
          else:
            dialog = CustonDialog(
                self.page,
                title="Erro de Autenticação",
                content=f"Falha ao autenticar com Google no servidor. Status: {response.status_code}",
                actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
            )
            self.page.show_dialog(dialog)
            self.page.update()       
                     
        except Exception as ex:
                    print(f"Erro na requisição ao backend: {ex}")        

#        await self.fetch_google_calendar_events()


    async def fetch_google_calendar_events(self):

        token_obj = await self.page.auth.get_token()

        token = token_obj.access_token    
        
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.utcnow().isoformat() + 'Z'   

        try:
            # Chamada direta à API do Google usando requests
            response = requests.get(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                headers=headers,
                params={
                    'timeMin': now,
                    'maxResults': 10,
                    'singleEvents': True,
                    'orderBy': 'startTime'
                }
            )
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                if not events:
                    print("Nenhum evento encontrado.")
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(f"Evento: {start} - {event['summary']}")
            else:
                print(f"Erro na API do Google: {response.status_code} - {response.text}")
                
        except Exception as ex:
            print(f"Erro ao conectar com Google Calendar: {ex}")



    async def refresh_token(self, view_instance):

        r_token:str = await ft.SharedPreferences().get("r_token")
        id:str      = await ft.SharedPreferences().get("id")

        if r_token:
            view_instance.progress_ring.visible = True
            self.page.update()

            response = await self.LoginModel.refresh_token(
                r_token,
                id
            )

            if response.status_code == 200:
                await ft.SharedPreferences().set("token", json.loads(response.content)["token"]) 
                await ft.SharedPreferences().set("r_token", json.loads(response.content)["r_token"]) 
               
                self.page.update()
                await self.page.push_route("/main")

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
                    ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())
                ]
            )
            self.page.show_dialog(dialog)          
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
                    ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())
                ]
            )
            self.page.show_dialog(dialog)          
            self.page.update()
            return
            
        elif response.status_code != 401:
            view_instance.progress_ring.visible = False
            await ft.SharedPreferences().set("token", json.loads(response.content)["token"]) 
            await ft.SharedPreferences().set("r_token", json.loads(response.content)["r_token"]) 

            message = json.loads(response.content)["message"]

            await ft.SharedPreferences().set("id", message["id"])

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
                    ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())
                ]
            )
            self.page.show_dialog(dialog)          
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
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())]
                )
                self.page.show_dialog(dialog)
                self.page.update()

            elif response.status_code == 404:
                dialog = CustonDialog(
                    self.page,
                    title="Erro",
                    content=message["message"],
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())]                    
                )
                self.page.show_dialog(dialog)
                self.page.update()