import flet as ft
from flet.auth import OAuthProvider
from urllib.parse import urlparse
import os
import httpx
from utils.secure_storage import SecureStorage
from controller.call_api import ProtectedApiCall
from model.accountmodel import AccountModel
from model.integracaomodel import IntegracaoModel
from controller.call_api import ProtectedApiCall
from view.controls.colors import AppColors


class IntegracaoController:
    """
    Controller dedicado para gerenciar integrações de terceiros (SaaS Inkers).
    Isola o fluxo OAuth2 da Meta para não conflitar com o login principal do Google.
    """
    def __init__(self, page: ft.Page, instance:None):
        self.page = page
        self.secure_storage = SecureStorage()
        self.model = AccountModel()
        self.instance = instance
        
        # Credenciais lidas do .env
        self.meta_client_id = os.getenv('META_CLIENT_ID')
        self.meta_secret_id = os.getenv('META_SECRET_ID')
        
        self.integracao_model = IntegracaoModel()

        if not self.meta_client_id or not self.meta_secret_id:
            print("Aviso: Chaves da Meta não configuradas no .env")


    async def on_switch_ads(self, status_campanha_meta:bool):
        try:
            response = await ProtectedApiCall(
                page=self.page,
                instance=self.instance,
                function=self.integracao_model.atualizar_status_campanha_meta,
                status_campanha_meta=status_campanha_meta,
                token=self.instance.token
            ).call_api_refresh_token()

            if response.status_code == 200:
                self.page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text(
                            "Campanha Meta Ads atualizada com sucesso!"
                        ),
                    )
                )
            else:
                self.page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text(
                            "Erro ao atualizar campanha Meta Ads!"
                        ),
                    )
                )
                self.instance.meta_ads_campaign_activate.value = False
            self.page.update()    
        except Exception as e:
            print(f"Erro ao ativar/desativar campanha Meta Ads: {e}")        


    async def salvar_google_analytics(self):
        """Envia o ID do Google Analytics para o backend usando o JWT armazenado."""

        google_analytics_id = self.page.session.store.get("google_analytics_id")
        
        if not google_analytics_id:
            print("[GA ERRO] ID do Analytics não informado.")
            return

        try:
            # O ProtectedApiCall encapsula o token JWT (self.instance.token) automaticamente
            response = await ProtectedApiCall(
                page=self.page,
                instance=self.instance,
                function=self.integracao_model.atualizar_google_analytics_id,
                google_analytics_id=google_analytics_id,
                token=self.instance.token
            ).call_api_refresh_token()

            if response.status_code == 200:
                print("[GA SUCESSO] Google Analytics ID atualizado com sucesso!")
                # Aqui você pode atualizar a UI ou mostrar um SnackBar de sucesso
            else:
                print(f"[GA ERRO BACKEND] {response.status_code} - {response.json()}")

        except Exception as ex:
            print(f"[GA EXCEPTION] {ex}")               


    async def get_meta_pixel_id(self, meta_ads_id: str, long_token: str):
            """Busca o Pixel ID atrelado à Conta de Anúncios selecionada."""
            url = f"https://graph.facebook.com/v25.0/{meta_ads_id}/adspixels"
            params = {"fields": "id,name", "access_token": long_token}

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        pixels = data.get("data", [])
                        if pixels:
                            pixel_id = pixels[0].get("id")
                            print(f"Pixel encontrado: {pixel_id}")

                            response = await ProtectedApiCall(
                                page=self.page,
                                instance=self.instance,
                                function=self.integracao_model.atualizar_meta_pixel_id,
                                meta_pixel_id=pixel_id,
                                token=self.instance.token
                            ).call_api_refresh_token()

                            if response.status_code != 200:
                                print(f"[META PIXEL ERRO] {response.json()}")
                                return

            except Exception as ex:
                print(f"[META PIXEL ERRO] {ex}")
            return None            


    async def atualizar_ui_meta(self):
        if not self.instance.meta_long_token:
            self.instance.status_meta.value = 'Desconectado'
            self.instance.status_meta.color = AppColors.ORANGE_DARK
            self.instance.botao_meta.content = 'Conectar'
            self.instance.botao_alterar_meta.visible = False
            self.instance.area_meta.height = 120
            self.instance.meta_ads_campaign_activate.value = False
        else:
            self.instance.status_meta.value = 'Conectado'
            self.instance.status_meta.color = AppColors.GREEN if hasattr(AppColors, 'GREEN') else 'green'
            self.instance.botao_meta.content = 'Desconectar'
            self.instance.botao_alterar_meta.visible = True
            self.instance.area_meta.height = 200
            if self.instance.status_campanha == 'TRUE':
                self.instance.meta_ads_campaign_activate.value = True
            else:
                self.instance.meta_ads_campaign_activate.value = False

        self.page.update()


    async def desconectar_meta_ads(self, e=None):
        """
        Remove a integração com a Meta Ads (limpa o token local e no backend).
        """
        self.page.session.store.set("meta_long_token", "")
        await self.secure_storage.remove("meta_long_token")
        self.instance.meta_long_token = ""

        # Envia token vazio para o backend limpar na tabela LOJA
        response = await ProtectedApiCall(
            self.page,
            instance=self.instance,
            function=self.model.update_meta_long_token,
            meta_long_token="",
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code == 200:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Meta Ads desconectado com sucesso!")))
        else:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Meta Ads desconectado localmente, mas erro ao atualizar backend.")))
        
        await self.atualizar_ui_meta()


    async def vincular_meta_ads(self, e=None):
        """
        Inicia o fluxo OAuth2 com a Meta. Deve ser chamado pelo evento on_click 
        do botão 'Vincular Facebook/Meta Ads' na View de configurações.
        """
        # 1. Constrói a URL de retorno dinamicamente (mesmo padrão do seu LoginController)
        parsed_url = urlparse(self.page.url)
        base_domain = f"https://{parsed_url.netloc}/oauth_callback"

        # 2. Instancia o Provedor Genérico configurado para a Meta
        meta_provider = OAuthProvider(
            client_id=self.meta_client_id,
            client_secret=self.meta_secret_id,
            authorization_endpoint="https://www.facebook.com/v25.0/dialog/oauth",
            token_endpoint="https://graph.facebook.com/v25.0/oauth/access_token",
            redirect_url=base_domain,
        )
        meta_provider.scopes.extend(
            [
                "public_profile",
                "ads_read", 
                "ads_management", 
                "business_management"
            ]
        )

        # 3. Guarda o callback original do Google e aplica o da Meta
        self.original_on_login = self.page.on_login 
        self.page.on_login = self.on_login_meta
        
        # 4. Dispara o popup/redirecionamento
        await self.page.login(provider=meta_provider)


    async def get_meta_ads_id(self, long_token:str, silencioso: bool = False):
        """
        Busca a conta de anúncios vinculada à Meta.
        """
        url = f"https://graph.facebook.com/v25.0/me/adaccounts"
        params = {
            "fields": "id,name,account_id",
            "access_token": long_token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get("data", [])
                    if not accounts:
                        if not silencioso:
                            self.page.show_dialog(ft.SnackBar(content=ft.Text("Você não tem contas de anúncios vinculadas à Meta.")))
                            self.page.update()
                        return
                    
                    if len(accounts) > 1:
                        if not silencioso:
                            options:list = []
                            for account in accounts:
                                options.append(
                                    ft.DropdownOption(
                                        style=ft.ButtonStyle(
                                            color=AppColors.GRAY_LIGHT2,                    
                                        ),
                                        text=account.get("name"),
                                        key=account.get("id")
                                    )
                                )
                            
                            self.instance.meta_ads_list_dropdown.options = options
                            self.page.show_dialog(self.instance.meta_ads_dialog)
                            self.page.update()
                        
                    elif len(accounts) == 1:
                        # Se só tem 1 conta, salva automaticamente no backend
                        meta_ads_id = accounts[0].get("id")
                        response_save = await ProtectedApiCall(
                            page=self.page,
                            instance=self.instance,
                            function=self.integracao_model.atualizar_meta_ads_id,
                            meta_ads_id=meta_ads_id,
                            token=self.instance.token
                        ).call_api_refresh_token()

                        if not silencioso:
                            if response_save and response_save.status_code == 200:
                                self.page.show_dialog(ft.SnackBar(content=ft.Text("Conta de anúncios vinculada com sucesso!")))
                                await self.atualizar_ui_meta()
                                # Busca e salva o Pixel atrelado a esta conta
                                await self.get_meta_pixel_id(meta_ads_id, long_token)
                            else:
                                self.page.show_dialog(ft.SnackBar(content=ft.Text("Erro ao vincular conta de anúncios no backend.")))
                            self.page.update() 
                        return meta_ads_id        

                else:
                    erro = response.json().get('error', {}).get('message', 'Erro desconhecido')
                    if not silencioso:
                        self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Falha na Graph API: {erro}")))
                    print(f"[META ERRO] {response.text}")
                    
        except Exception as ex:
            if not silencioso:
                self.page.show_dialog(ft.SnackBar(content=ft.Text("Erro de conexão com a Meta.")))
            print(f"[META EXCEPTION] {ex}")

        if not silencioso:
            self.page.update()


    async def salvar_meta_ads_id_selecionado(self, e=None):
        """
        Salva a conta de anúncios selecionada no dropdown da Meta.
        Após salvar, busca e persiste o Pixel ID atrelado à conta escolhida.
        """
        meta_ads_id = self.instance.meta_ads_list_dropdown.value
        if not meta_ads_id:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Por favor, selecione uma conta de anúncios.")))
            self.page.update()
            return

        # Fecha o diálogo
        self.page.pop_dialog()
        self.page.update()
        
        # Envia ID da conta para o backend
        response = await ProtectedApiCall(
            page=self.page,
            instance=self.instance,
            function=self.integracao_model.atualizar_meta_ads_id,
            meta_ads_id=meta_ads_id,
            token=self.instance.token
        ).call_api_refresh_token()

        if response and response.status_code == 200:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Conta de anúncios vinculada com sucesso!")))
            await self.atualizar_ui_meta()

            # Busca e salva o Pixel atrelado à conta selecionada no dropdown
            long_token = self.page.session.store.get("meta_long_token") or self.instance.meta_long_token
            if long_token:
                await self.get_meta_pixel_id(meta_ads_id, long_token)
        else:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Erro ao salvar conta de anúncios no backend.")))
        
        self.page.session.store.set("meta_ads_id", meta_ads_id)
        self.page.update()
         

    async def on_login_meta(self, e: ft.LoginEvent):
        """
        Callback exclusivo para processar o retorno do provedor Meta.
        """
        # 1. DEVOLVE o controle do app para o callback original (Google)
        # Isso garante que se o usuário deslogar e tentar entrar com Google, vai funcionar.
        self.page.on_login = self.original_on_login

        if e.error:
            self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Erro ao vincular Meta: {e.error}")))
            self.page.update()
            return

        # 2. Captura o Token de Curta Duração (Short-Lived: ~1h)
        token_obj = await self.page.auth.get_token()
        short_token = token_obj.access_token

        # 3. Inicia a troca para o Token de Longa Duração (Long-Lived: 60 dias)
        await self.gerar_token_longa_duracao(short_token)


    async def gerar_token_longa_duracao(self, short_token: str):
        """
        Comunica-se com a Graph API para trocar o token de 1h pelo de 60 dias.
        """
        url = "https://graph.facebook.com/v25.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.meta_client_id,
            "client_secret": self.meta_secret_id,
            "fb_exchange_token": short_token
        }

        self.page.session.store.set("meta_short_token", short_token)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    long_token = data.get("access_token")

                    # Salva o token ANTES de buscar as contas para que
                    # instance.meta_long_token já esteja definido quando
                    # atualizar_ui_meta() for chamada internamente
                    await self.salvar_integracao_backend(long_token)

                    # Busca e vincula a conta de anúncios.
                    # - Se 1 conta: salva ads_id e pixel automaticamente (dentro de get_meta_ads_id)
                    # - Se >1 conta: abre dialog; pixel é salvo em salvar_meta_ads_id_selecionado após o Ok
                    await self.get_meta_ads_id(long_token)
                    
                else:
                    erro = response.json().get('error', {}).get('message', 'Erro desconhecido')
                    self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Falha na Graph API: {erro}")))
                    print(f"[META ERRO] {response.text}")
                    
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Erro de conexão com a Meta.")))
            print(f"[META EXCEPTION] {ex}")
            
        self.page.update()


    async def salvar_integracao_backend(self, long_token: str, silencioso: bool = False):
        """
        Aqui chamo o AccountModel para enviar o meta_long_token criptografado e salvar na tabela LOJA.
        """
        self.page.session.store.set("meta_long_token", long_token)
        
        encrypted_value = await self.secure_storage.set("meta_long_token", long_token)

        response = await ProtectedApiCall(
            self.page,
            instance=self.instance,
            function=self.model.update_meta_long_token,
            meta_long_token=encrypted_value,
            token=self.instance.token
        ).call_api_refresh_token()

        if not silencioso:
            # Feedback visual para o usuário
            if response.status_code == 200:
                # Atualiza o token na instância para que atualizar_ui_meta funcione
                self.instance.meta_long_token = long_token
                self.page.show_dialog(ft.SnackBar(content=ft.Text("Token Meta salvo com sucesso!")))
                await self.atualizar_ui_meta()
                self.page.update()
            else:
                self.page.show_dialog(ft.SnackBar(content=ft.Text("Erro ao vincular conta de anúncios.")))
                self.page.update() 
                print(f"[META ERROR] {response.content}")   
        else:
            if response.status_code == 200:
                # Atualiza o token na instância mesmo no modo silencioso
                self.instance.meta_long_token = long_token
            else:
                print(f"[META ERROR SILENCIOSO] {response.content}")


    async def renovar_meta_long_token(self, current_long_token_criptografado: str):
        """
        Descriptografa o token salvo e comunica-se com a Graph API para renová-lo 
        por mais 60 dias.
        """
        # 1. Descriptografa o token que veio do banco de dados
        try:
            current_long_token = await self.secure_storage.decrypt_value(current_long_token_criptografado)
        except Exception as e:
            print(f"[META RENOVAÇÃO ERRO] Falha ao descriptografar token: {e}")
            return False

        # 2. Prepara a requisição para a Meta
        url = "https://graph.facebook.com/v25.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.meta_client_id,
            "client_secret": self.meta_secret_id,
            "fb_exchange_token": current_long_token # Passa o token antigo limpo
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    new_long_token = data.get("access_token")
                    
                    # 3. Reaproveita sua função para criptografar o NOVO token e salvar no banco
                    await self.salvar_integracao_backend(new_long_token, silencioso=True)
                    print("[META] Token renovado com sucesso e atualizado no banco!")

                    await self.get_meta_ads_id(new_long_token, silencioso=True)
                    return True
                    
                else:
                    # Se caiu aqui, o usuário trocou a senha ou removeu o app do Facebook.
                    # A integração quebrou e ele precisa fazer o login manual novamente.
                    erro = response.json().get('error', {}).get('message', 'Erro desconhecido')
                    print(f"[META FALHA RENOVAÇÃO] Integração expirada/revogada: {erro}")
                    
                    self.page.show_dialog(ft.SnackBar(
                        content=ft.Text("A integração com o Facebook expirou. Por favor, vincule novamente.")
                    ))
                    # Opcional: Aqui você pode chamar uma rota da sua API para limpar o token do banco
                    self.instance.area_meta.visible = True 
                    self.page.update()
                    return False
                    
        except Exception as ex:
            print(f"[META EXCEPTION RENOVAÇÃO] {ex}")
            return False            