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

        self.page.session.store.set("google_access_token", token_obj.access_token)
        self.page.session.store.set("google_refresh_token", token_obj.refresh_token)

        g_user = self.page.auth.user
        
        g_mail = g_user["email"]
        g_id   = g_user["sub"  ]
        g_name = g_user["name"]
        
        g_token = token_obj.access_token

        try:
          response = await self.LoginModel.login_google(g_mail, g_id, g_token, g_name)

          if response.status_code == 200:
            data = json.loads(response.content)
            r_token = data["r_token"]
            user_id = data["message"]["id"]

            # Sessão (volátil)
            self.page.session.store.set("r_token", r_token)
            self.page.session.store.set("token",   data["token"  ])
            self.page.session.store.set("id",      user_id)

            # Persistente: salva para auto-login na próxima sessão
            await ft.SharedPreferences().set("r_token",              r_token)
            await ft.SharedPreferences().set("id",                   str(user_id))
            await ft.SharedPreferences().set("google_refresh_token", token_obj.refresh_token or "")
            await ft.SharedPreferences().set("login_method",         "google")

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
        # Lê r_token e id do SharedPreferences (persistente entre sessões)
        r_token: str = await ft.SharedPreferences().get("r_token")
        user_id: str = await ft.SharedPreferences().get("id")

        if r_token:
            view_instance.progress_ring.visible = True
            self.page.update()

            response = await self.LoginModel.refresh_token(
                r_token,
                user_id
            )

            if response.status_code == 200:
                data = json.loads(response.content)
                new_token   = data["token"]
                new_r_token = data["r_token"]

                # SharedPreferences: atualiza persistência para a próxima sessão
                await ft.SharedPreferences().set("r_token", new_r_token)
                await ft.SharedPreferences().set("id",      user_id)

                # session.store: necessário para o MainView e demais views lerem nesta sessão
                self.page.session.store.set("token",   new_token)
                self.page.session.store.set("r_token", new_r_token)
                self.page.session.store.set("id",      user_id)

                # Busca o google_refresh_token e coloca na sessão também
                g_refresh = await ft.SharedPreferences().get("google_refresh_token")
                if g_refresh:
                    self.page.session.store.set("google_refresh_token", g_refresh)

                self.page.update()
                await self.page.push_route("/main")
            else:
                # Token inválido/expirado: limpa persistência para forçar novo login
                await self.clear_persistent_tokens()

            view_instance.progress_ring.visible = False
            self.page.update()


    async def clear_persistent_tokens(self):
        """Remove tokens persistidos do client_storage (usado no logout ou token inválido)."""
        for key in ("r_token", "id", "google_refresh_token", "login_method"):
            await ft.SharedPreferences().remove(key)


    async def handle_login(self, e, view_instance):
            self.email = view_instance.txt_username.value
            self.password = view_instance.txt_password.value

            if not self.email or not self.password:
                dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor, preencha o e-mail e a senha.",
                    actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                )
                self.page.show_dialog(dialog)
                self.page.update()
                return

            view_instance.progress_ring.visible = True
            self.page.update()

            try:
                response = await self.LoginModel.login(self.email, self.password) 

                if response.status_code == 200:
                    data = json.loads(response.content)
                    self.page.session.store.set("token",   data["token"]) 
                    self.page.session.store.set("r_token", data["r_token"]) 
                    self.page.session.store.set("id",      data["message"]["id"])
                    
                    view_instance.progress_ring.visible = False
                    self.page.update()
                    self.page.go("/main")

                elif response.status_code == 401:
                    view_instance.progress_ring.visible = False
                    dialog = CustonDialog(
                        self.page,
                        title="Acesso Negado",
                        content="E-mail ou senha incorretos.",
                        actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                    )
                    self.page.show_dialog(dialog)
                    self.page.update()

                elif response.status_code == 404:
                    view_instance.progress_ring.visible = False
                    dialog = CustonDialog(
                        self.page,
                        title="Usuário não encontrado",
                        content="Não encontramos uma conta com esse e-mail. Verifique o e-mail informado.",
                        actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                    )
                    self.page.show_dialog(dialog)
                    self.page.update()

                elif response.status_code == 422:
                    view_instance.progress_ring.visible = False
                    dialog = CustonDialog(
                        self.page,
                        title="Dados inválidos",
                        content="Verifique os dados informados e tente novamente.",
                        actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                    )
                    self.page.show_dialog(dialog)
                    self.page.update()

                else:
                    # Log técnico apenas no console para depuração
                    print(f"[LOGIN ERRO] Status: {response.status_code} | Resposta: {response.content}")

                    view_instance.progress_ring.visible = False
                    dialog = CustonDialog(
                        self.page,
                        title="Serviço indisponível",
                        content="Não foi possível realizar o login no momento. Tente novamente mais tarde.",
                        actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                    )
                    self.page.show_dialog(dialog)
                    self.page.update()

            except Exception as ex:
                # Log técnico apenas no console
                print(f"[LOGIN ERRO] Exceção: {ex}")

                view_instance.progress_ring.visible = False
                dialog = CustonDialog(
                    self.page,
                    title="Erro de conexão",
                    content="Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.",
                    actions=[ft.TextButton('OK', on_click=lambda e: self.page.pop_dialog())]
                )
                self.page.show_dialog(dialog)
                self.page.update()


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