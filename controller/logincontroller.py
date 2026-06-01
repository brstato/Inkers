import flet as ft
from flet.auth.providers import GoogleOAuthProvider
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from controller.integracaocontroller import IntegracaoController
from controller.call_api import ProtectedApiCall
from utils.secure_storage import SecureStorage
from urllib.parse import urlparse
import json
import os
from datetime import datetime
import requests
import httpx


class LoginController:
    """
    Controller responsável por toda a lógica de negócio do fluxo de autenticação.

    Gerencia a integração com o provedor OAuth2 do Google via Flet,
    coordena as chamadas ao `LoginModel` (camada de dados), controla
    o armazenamento de tokens (volátil e persistente) e fornece
    feedback visual à `LoginView` via dialogs e progress ring.

    Attributes:
        client_id (str): Client ID do projeto no Google Cloud Console,
            lido da variável de ambiente `CLIENT_ID`.
        id_secreto (str): Client Secret do projeto no Google Cloud Console,
            lido da variável de ambiente `SECRET_ID`.
        page (ft.Page): Referência ao objeto principal da aplicação Flet.
        LoginModel (LoginModel): Instância do model para comunicação com a API.
        token_obj (str | None): Token object da sessão atual do Google OAuth2.
        parsed_url: URL da página parseada para extração do domínio base.
        base_domain (str): URI de callback OAuth2 construída dinamicamente
            a partir da URL atual (ex: `https://app.inkers.com.br/oauth_callback`).
        provider (GoogleOAuthProvider): Provedor OAuth2 configurado com
            client_id, secret e redirect URI.
    """

    def __init__(self, page: ft.Page):
        """
        Inicializa o LoginController, configura o provedor Google OAuth2
        e registra o callback de retorno da autenticação.

        O redirect URI é construído dinamicamente a partir da URL atual da
        página, tornando o controller compatível com diferentes ambientes
        (desenvolvimento, staging, produção) sem necessidade de configuração
        adicional.

        Args:
            page (ft.Page): Objeto principal do Flet que representa a janela/aba
                            atual. Utilizado para navegação, dialogs, sessão e
                            acesso ao sistema OAuth2 do framework.

        Side Effects:
            - Define `page.on_login` apontando para `self.on_login`,
              registrando o callback de retorno do fluxo OAuth2.
            - Adiciona ao provider os seguintes escopos Google:
                * `userinfo.email` — endereço de e-mail do usuário.
                * `userinfo.profile` — nome e foto de perfil.
                * `calendar.events` — leitura/escrita de eventos no Google Calendar.
                * `adwords` — acesso à API Google Ads (Google AdWords).
                * `analytics.readonly` — leitura de dados do Google Analytics (GA4).
            - Adiciona `?access_type=offline&prompt=consent` ao endpoint de
              autorização para garantir a entrega do `refresh_token` do Google
              mesmo em reautenticações subsequentes.
        """

        self.client_id = os.getenv('CLIENT_ID')
        self.id_secreto = os.getenv('SECRET_ID')
        self.page = page
        self.LoginModel = LoginModel()
        self.token_obj: str = None

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
                "https://www.googleapis.com/auth/calendar.events",
                "https://www.googleapis.com/auth/adwords",
                "https://www.googleapis.com/auth/analytics.readonly"
            ]
        )

        self.provider.authorization_endpoint += "?access_type=offline&prompt=consent"

        self.page.on_login = self.on_login


    async def fetch_google_ads_id(self, access_token: str):
        """Busca o ID da conta do Google Ads do usuário."""
        # Puxando o dev token do seu .env
        dev_token = os.getenv('DEVELOPER_TOKEN') 
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": dev_token
        }
            
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint que lista todas as contas que este usuário tem acesso
                res_ads = await client.get(
                    'https://googleads.googleapis.com/v20/customers:listAccessibleCustomers',
                    headers=headers
                )
                    
                if res_ads.status_code == 200:
                    data = res_ads.json()

                    ads_id:str = data['resourceNames'][0]
                    ads_id = ads_id.replace('customers/', '')

                    print(f"[GOOGLE ADS ID] {ads_id}")

                    return ads_id                        
        except Exception as ex:
            print(f"[GOOGLE ADS ERRO] {ex}")
            
        return None        


    async def fetch_google_analytics_id(self, access_token: str):
        """
        Busca o Measurement ID (ex.: ``G-XXXXXXXXXX``) do Google Analytics 4
        associado à primeira propriedade web encontrada na conta do usuário.

        Realiza duas chamadas sequenciais à Google Analytics Admin API:
            1. ``accountSummaries`` — lista as contas e suas propriedades GA4.
            2. ``dataStreams`` — lista os data streams da primeira propriedade,
               extraindo o ``measurementId`` do primeiro stream web encontrado.

        Args:
            access_token (str): Access token do Google OAuth2 com o escopo
                ``analytics.readonly`` ativo na sessão atual.

        Returns:
            str | None: O Measurement ID (``G-XXXXXXXXXX``) se encontrado;
                ``None`` se a conta não possuir propriedades/streams
                ou se ocorrer qualquer erro de rede ou API.

        Side Effects:
            - Imprime o ID encontrado no console via ``print``.
            - Em caso de exceção, imprime a mensagem de erro com
              o prefixo ``[GOOGLE ANALYTICS ERRO]``.

        Note:
            Após o retorno, o chamador (``on_login``) persiste o valor
            em ``session.store`` sob a chave ``google_analytics_id``.
            A persistência em banco de dados fica a cargo de uma chamada
            à API backend (não implementada neste método).
        """
        headers = {"Authorization": f"Bearer {access_token}"}
            
        try:
            async with httpx.AsyncClient() as client:
                # 1. Busca as contas e propriedades do usuário
                res_summaries = await client.get(
                    'https://analyticsadmin.googleapis.com/v1beta/accountSummaries',
                    headers=headers
                )
                
                if res_summaries.status_code == 200:
                    data = res_summaries.json()
                    accounts = data.get('accountSummaries', [])
                        
                if not accounts:
                    return None
                        
                    # Pega a primeira propriedade da primeira conta
                first_property = accounts[0].get('propertySummaries', [])[0].get('property')
                
                # 2. Busca o Data Stream (para extrair o Measurement ID: G-XXXX)
                res_streams = await client.get(
                    f'https://analyticsadmin.googleapis.com/v1beta/{first_property}/dataStreams',
                    headers=headers
                )
                
                if res_streams.status_code == 200:
                    streams = res_streams.json().get('dataStreams', [])
                    for stream in streams:
                        if 'webStreamData' in stream:
                            ga_id = stream['webStreamData'].get('measurementId')
                            print(f"Google Analytics ID encontrado: {ga_id}")
                            # Envie para a sua API C# atualizar a coluna GOOGLE_ANALYTICS_ID
                            
                    
                            return ga_id
        except Exception as ex:
            print(f"[GOOGLE ANALYTICS ERRO] {ex}")
            
        return None        


    async def handle_login_google(self):
        """
        Inicia o fluxo de autenticação OAuth2 com o Google.

        Aciona o mecanismo interno do Flet para abrir o popup ou
        redirecionar o usuário para a página de autorização do Google.
        Após a autorização (ou recusa), o Flet chama automaticamente
        o callback `on_login`.
        """
        await self.page.login(
            provider=self.provider
        )


    async def on_login(self, e):
        """
        Callback do Flet chamado automaticamente após a conclusão do
        fluxo OAuth2 do Google (com sucesso ou com erro).

        Este é o método central do processo de autenticação Google.
        Coordena a obtenção dos tokens Google, extração dos dados do
        usuário, chamada ao backend da API e armazenamento dos tokens
        resultantes em memória (session.store) e de forma persistente
        (SharedPreferences).

        Args:
            e: Evento de login do Flet. Contém:
                - `e.error` (str | None): Mensagem de erro se o login falhou.

        Flow:
            1. Verifica `e.error` — se presente, exibe SnackBar e encerra.
            2. Obtém o `token_obj` via `page.auth.get_token()`.
            3. Salva `access_token` e `refresh_token` do Google na session.store.
            4. Extrai `email`, `sub` (id) e `name` de `page.auth.user`.
            5. Chama `LoginModel.login_google()` para autenticar no backend.
            6. Se status 200: salva tokens da API em session.store e
               SharedPreferences, depois navega para `/main`.
            7. Se outro status: exibe `CustonDialog` com o código de erro HTTP.
            8. Em caso de exceção de rede: registra no console via `print`.

        Side Effects:
            Armazena as seguintes chaves após login bem-sucedido:
            - session.store: `google_access_token`, `google_refresh_token`,
              `r_token`, `token`, `id`.
            - SharedPreferences: `r_token`, `id`, `google_refresh_token`,
              `login_method` (valor: "google").
        """
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
        g_name = g_user["name" ]

        g_token = token_obj.access_token
        r_token = token_obj.refresh_token

        try:
            try:
               ads_id = await self.fetch_google_ads_id(g_token)
            except Exception as e:
                print(f"Erro ao buscar Google Ads ID: {e}")

            response = await self.LoginModel.login_google(
                g_mail, 
                g_id, 
                g_token, 
                g_name, 
                ads_id, 
                r_token
            )


            if response.status_code == 200:
                data = json.loads(response.content)
                r_token = data["r_token"]
                user_id = data["message"]["id"]

                # Sessão (volátil): utilizada durante a sessão ativa para
                # autorizar chamadas às APIs protegidas da aplicação.
                self.page.session.store.set("r_token", r_token)
                self.page.session.store.set("token",   data["token"  ])
                self.page.session.store.set("id",      user_id)

                # Persistente: salva criptografado para auto-login na próxima sessão
                _storage = SecureStorage()
                await _storage.set("r_token",              r_token)
                await _storage.set("google_refresh_token", token_obj.refresh_token or "")
                await ft.SharedPreferences().set("id",          str(user_id))
                await ft.SharedPreferences().set("login_method", "google")

                # Busca o Analytics ID em background
                ga_id = await self.fetch_google_analytics_id(g_token)
                if ga_id:
                    # Salve na sessão ou chame a API para persistir no banco (GOOGLE_ANALYTICS_ID)
                    self.page.session.store.set("google_analytics_id", ga_id)

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
        """
        Busca os próximos eventos do Google Calendar do usuário autenticado.

        Realiza uma chamada direta à Google Calendar API usando o access token
        do Google armazenado na sessão atual. Exibe os eventos encontrados no
        console (log técnico).

        Note:
            Este método está implementado mas **não está sendo chamado**
            (a linha de invocação em ``on_login`` está comentada). É uma
            feature planejada para versões futuras da aplicação.
            O escopo ``calendar.events`` já é solicitado no OAuth2, portanto
            não há necessidade de reautenticação para ativá-la.

        API Endpoint:
            GET https://www.googleapis.com/calendar/v3/calendars/primary/events

        Query Params:
            - timeMin (str): Data/hora atual em UTC no formato ISO 8601
              (ex.: ``2026-05-29T23:00:00Z``).
            - maxResults (int): Número máximo de eventos retornados (10).
            - singleEvents (bool): ``True`` para expandir eventos recorrentes
              em ocorrências individuais.
            - orderBy (str): ``startTime`` para ordem cronológica ascendente.
        """
        token_obj = await self.page.auth.get_token()

        token = token_obj.access_token

        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.utcnow().isoformat() + 'Z'

        try:
            # Chamada direta à API do Google usando httpx
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
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
        """
        Tenta renovar a sessão do usuário automaticamente usando o refresh
        token persistido no dispositivo da sessão anterior (Auto Login).

        Chamado por `LoginView.did_mount()` em background para verificar
        silenciosamente se o usuário pode ser reautenticado sem interação.

        Args:
            view_instance: Instância da `LoginView`, usada para controlar
                           a visibilidade do `progress_ring` durante
                           a tentativa de renovação.

        Flow:
            1. Lê `r_token` e `id` do `SharedPreferences`.
            2. Se `r_token` existir, exibe o `progress_ring` e chama
               `LoginModel.refresh_token()`.
            3. Se status 200: atualiza tokens em `SharedPreferences` e
               `session.store`, restaura `google_refresh_token` na sessão
               e navega para `/main`.
            4. Se outro status: chama `clear_persistent_tokens()` para
               invalidar os dados locais e forçar novo login completo.
            5. Oculta o `progress_ring` ao final, independente do resultado.

        Note:
            Se `r_token` não existir no `SharedPreferences` (primeiro acesso
            ou após logout), nenhuma ação é tomada e o usuário permanece
            na tela de login.
        """
        # Lê r_token e id do SharedPreferences (persistente entre sessões)
        _storage = SecureStorage()
        r_token: str = await _storage.get("r_token")
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

                # SharedPreferences: atualiza persistência criptografada para a próxima sessão
                await _storage.set("r_token", new_r_token)
                await ft.SharedPreferences().set("id", user_id)

                # session.store: necessário para o MainView e demais views lerem nesta sessão
                self.page.session.store.set("token",   new_token)
                self.page.session.store.set("r_token", new_r_token)
                self.page.session.store.set("id",      user_id)

                # Busca o google_refresh_token descriptografado e coloca na sessão
                g_refresh = await _storage.get("google_refresh_token")
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
        """
        Remove todos os tokens de autenticação armazenados de forma persistente
        no `SharedPreferences` do dispositivo/navegador.

        Deve ser chamado nos seguintes cenários:
            - Logout explícito do usuário.
            - Falha na renovação do token (``r_token`` inválido ou expirado).
            - Detecção de sessão comprometida ou inválida.

        Após esta operação, o próximo acesso à aplicação exigirá que o usuário
        realize um novo login completo (Google OAuth2 ou e-mail/senha).

        Note:
            Os tokens são armazenados de forma **criptografada** via
            ``SecureStorage`` (wrapper sobre ``flet.security``), e não
            diretamente no ``ft.SharedPreferences``. Esta função delega
            a remoção ao método ``SecureStorage.remove()``.

        Keys removidas do SecureStorage:
            - ``r_token``: Refresh token da API backend.
            - ``google_refresh_token``: Refresh token do Google OAuth2.
            - ``login_method``: Método de login utilizado (ex.: ``"google"``).

        Keys removidas do SharedPreferences (via SecureStorage):
            - ``id``: ID do usuário na API backend (não criptografado).
        """
        _storage = SecureStorage()
        for key in ("r_token", "id", "google_refresh_token", "login_method"):
            await _storage.remove(key)


    async def handle_login(self, e, view_instance):
        """
        Gerencia o fluxo completo de autenticação tradicional com e-mail e senha.

        Valida os campos de entrada, exibe o indicador de carregamento,
        chama o `LoginModel` e trata as diferentes respostas HTTP com
        dialogs de feedback amigáveis ao usuário.

        Args:
            e: Evento de clique do Flet (não utilizado diretamente).
            view_instance: Instância da `LoginView`, usada para:
                - Ler os valores de `txt_username` (e-mail) e `txt_password` (senha).
                - Controlar a visibilidade do `progress_ring`.

        Flow:
            1. Valida se e-mail e senha foram preenchidos.
            2. Exibe o `progress_ring`.
            3. Chama `LoginModel.login(email, senha)`.
            4. Processa a resposta HTTP:
               - 200: Salva `token`, `r_token` e `id` na session.store →
                      Navega para `/main`.
               - 401: Dialog "Acesso Negado" — credenciais inválidas.
               - 404: Dialog "Usuário não encontrado".
               - 422: Dialog "Dados inválidos".
               - Outros: Dialog "Serviço indisponível" + log técnico no console.
            5. Em caso de exceção de rede: Dialog "Erro de conexão" + log no console.
            6. Oculta o `progress_ring` em todos os casos de erro.

        Note:
            Esta feature está totalmente implementada, mas o botão que a aciona
            (`btn_login`) está atualmente comentado na UI da `LoginView`.
            O método principal de autenticação ativo é o Google OAuth2.
        """
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
        """
        Gerencia o fluxo de recuperação de senha por e-mail.

        Valida se o e-mail foi informado, exibe o indicador de carregamento,
        chama o `LoginModel` e apresenta o feedback retornado pelo backend
        diretamente ao usuário via `CustonDialog`.

        Args:
            e: Evento de clique do Flet (não utilizado diretamente).
            view_instance: Instância da `LoginView`, usada para:
                - Ler o valor de `txt_username` (e-mail informado).
                - Controlar a visibilidade do `progress_ring`.

        Flow:
            1. Lê o e-mail do campo ``txt_username``.
            2. Se vazio: exibe dialog "Por favor informe o email." e encerra.
            3. Exibe o ``progress_ring``.
            4. Chama ``LoginModel.recovery_password(email)``.
            5. Oculta o ``progress_ring``.
            6. Processa a resposta HTTP:
               - 200: Exibe dialog de sucesso com ``message["message"]``
                      (texto personalizado retornado pelo backend, ex.:
                      "Enviamos um link de redefinição para o seu e-mail.").
               - 404: Exibe dialog de erro com ``message["message"]``
                      (ex.: "E-mail não encontrado").
               - Outros status: nenhum tratamento específico implementado;
                 o ``progress_ring`` é ocultado mas nenhum feedback
                 visual adicional é exibido ao usuário.

        Note:
            O texto das mensagens de sucesso e erro são definidos
            inteiramente pelo backend, permitindo personalização sem
            necessidade de alterações no frontend.
        """
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