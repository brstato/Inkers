import flet as ft
from flet.auth.providers import GoogleOAuthProvider
from model.loginmodel import LoginModel
from controller.integracaocontroller import IntegracaoController
from utils.secure_storage import SecureStorage
from urllib.parse import urlparse
import os
import json
from datetime import datetime
from typing import Callable, Awaitable, Optional
import httpx


# ── Type aliases para callbacks da View ─────────────────────────────

ShowLoadingFn = Callable[[bool], None]
"""Callback para mostrar/ocultar o indicador de carregamento."""

ShowErrorFn = Callable[[str, str], None]
"""Callback para exibir um dialog de erro (title, message)."""

ShowMessageFn = Callable[[str, str], None]
"""Callback para exibir um dialog informativo (title, message)."""

NavigateFn = Callable[[str], Awaitable[None]]
"""Callback assíncrono para navegar para uma rota."""


class LoginController:
    """
    Controller responsável por toda a lógica de negócio do fluxo de autenticação.

    Gerencia a integração com o provedor OAuth2 do Google via Flet,
    coordena as chamadas ao ``LoginModel`` (camada de dados), controla
    o armazenamento de tokens (volátil e persistente) e comunica
    feedback visual à View via callbacks injetados.

    Attributes:
        _page (ft.Page): Referência ao objeto principal da aplicação Flet.
        _model (LoginModel): Instância do model para comunicação com a API.
        _provider (GoogleOAuthProvider): Provedor OAuth2 configurado.
        _on_show_loading (ShowLoadingFn): Callback para controlar progress ring.
        _on_show_error (ShowErrorFn): Callback para exibir dialog de erro.
        _on_show_message (ShowMessageFn): Callback para exibir dialog informativo.
        _on_navigate (NavigateFn): Callback para navegação de rotas.
    """

    def __init__(
        self,
        page: ft.Page,
        model: LoginModel | None = None,
        *,
        on_show_loading: ShowLoadingFn | None = None,
        on_show_error: ShowErrorFn | None = None,
        on_show_message: ShowMessageFn | None = None,
        on_navigate: NavigateFn | None = None,
    ):
        """
        Inicializa o LoginController, configura o provedor Google OAuth2
        e registra o callback de retorno da autenticação.

        O redirect URI é construído dinamicamente a partir da URL atual da
        página, tornando o controller compatível com diferentes ambientes
        (desenvolvimento, staging, produção) sem necessidade de configuração
        adicional.

        Args:
            page: Objeto principal do Flet. Utilizado para OAuth2, sessão
                e acesso ao session store.
            model: Instância de LoginModel (injeção de dependência).
                Se ``None``, cria uma instância padrão.
            on_show_loading: Callback invocado com ``True``/``False``
                para mostrar/ocultar indicador de carregamento.
            on_show_error: Callback invocado com ``(title, message)``
                para exibir um dialog de erro ao usuário.
            on_show_message: Callback invocado com ``(title, message)``
                para exibir um dialog informativo ao usuário.
            on_navigate: Callback assíncrono invocado com a rota destino
                (ex.: ``"/main"``) para navegar.

        Side Effects:
            - Define ``page.on_login`` apontando para ``self._on_login``,
              registrando o callback de retorno do fluxo OAuth2.
            - Adiciona ao provider os seguintes escopos Google:
                * ``userinfo.email`` — endereço de e-mail do usuário.
                * ``userinfo.profile`` — nome e foto de perfil.
                * ``calendar.events`` — leitura/escrita de eventos.
                * ``adwords`` — acesso à API Google Ads.
                * ``analytics.readonly`` — leitura de dados do GA4.
            - Adiciona ``?access_type=offline&prompt=consent`` ao endpoint
              de autorização para garantir entrega do ``refresh_token``.
        """
        self._page = page
        self._model = model or LoginModel()

        # Callbacks da View (no-ops como fallback seguro)
        self._on_show_loading: ShowLoadingFn = on_show_loading or (lambda visible: None)
        self._on_show_error: ShowErrorFn = on_show_error or (lambda t, m: None)
        self._on_show_message: ShowMessageFn = on_show_message or (lambda t, m: None)
        self._on_navigate: NavigateFn = on_navigate or self._default_navigate

        # OAuth2 config
        self._client_id = os.getenv("CLIENT_ID")
        self._client_secret = os.getenv("SECRET_ID")

        parsed_url = urlparse(self._page.url)
        redirect_uri = f"https://{parsed_url.netloc}/oauth_callback"

        self._provider = GoogleOAuthProvider(
            self._client_id,
            self._client_secret,
            redirect_uri,
        )

        self._provider.scopes.extend([
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/adwords",
            "https://www.googleapis.com/auth/analytics.readonly",
        ])

        self._provider.authorization_endpoint += "?access_type=offline&prompt=consent"

        self._page.on_login = self._on_login


    async def _default_navigate(self, route: str) -> None:
        """Navegação padrão caso a View não injete um callback."""
        self._page.go(route)


    async def fetch_google_ads_id(self, access_token: str) -> list[str]:
        """
        Busca todas as contas do Google Ads vinculadas ao usuário autenticado.
        Retorna uma lista de IDs de clientes (Customer IDs) limpos.
        """
        dev_token = os.getenv("DEVELOPER_TOKEN")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": dev_token,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers",
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    
                    # A API retorna no formato: "resourceNames": ["customers/1234567890", "customers/0987654321"]
                    resource_names = data.get("resourceNames", [])
                    
                    # Extrai apenas os números
                    ads_ids = [name.replace("customers/", "") for name in resource_names]
                    
                    print(f"[GOOGLE ADS IDs ENCONTRADOS] {ads_ids}")
                    return ads_ids
                else:
                    print(f"[GOOGLE ADS ERRO] Status: {response.status_code} - {response.text}")

        except Exception as ex:
            print(f"[GOOGLE ADS EXCEÇÃO] {ex}")

            return []


    async def fetch_google_ads_accounts_details(self, access_token: str, customer_ids: list[str]) -> list[dict]:
        """Busca o ID da conta do Google Ads do usuário."""
        dev_token = os.getenv("DEVELOPER_TOKEN")
        contas_detalhes = []

        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": dev_token,
            "Content-Type": "application/json"
        }

        query = """
            SELECT 
                customer.id,
                customer.descriptive_name
            FROM customer
        """

        try:
            async with httpx.AsyncClient() as client:
                for customer_id in customer_ids:
                    headers["login-customer-id"] = customer_id
                    payload = {
                        "query": query
                    }
                    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:search"
                    response = await client.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        if results:
                            customer_info = results[0].get("customer", {})
                            nome_conta = customer_info.get("descriptiveName", "Conta sem nome")
                            id_conta = str(customer_info.get("id"))
                            contas_detalhes.append(
                                {
                                    "id": id_conta,
                                    "nome": nome_conta
                                }
                            )
                            print(f"[GOOGLE ADS CONTA] ID: {id_conta} | Nome: {nome_conta}")
        except Exception as ex:
            print(f"[GOOGLE ADS ERRO] {ex}")

        return contas_detalhes
        

    async def fetch_google_analytics_id(self, access_token: str) -> Optional[str]:
        """
        Busca o Measurement ID (ex.: ``G-XXXXXXXXXX``) do Google Analytics 4
        associado à primeira propriedade web encontrada na conta do usuário.

        Realiza duas chamadas sequenciais à Google Analytics Admin API:
            1. ``accountSummaries`` — lista as contas e suas propriedades GA4.
            2. ``dataStreams`` — lista os data streams da primeira propriedade,
               extraindo o ``measurementId`` do primeiro stream web encontrado.

        Args:
            access_token: Access token do Google OAuth2 com o escopo
                ``analytics.readonly`` ativo na sessão atual.

        Returns:
            O Measurement ID (``G-XXXXXXXXXX``) se encontrado; ``None`` caso
            contrário.

        Side Effects:
            - Imprime o ID encontrado no console via ``print``.
            - Em caso de exceção, imprime a mensagem de erro com
              o prefixo ``[GOOGLE ANALYTICS ERRO]``.

        Note:
            Após o retorno, o chamador (``_on_login``) persiste o valor
            em ``session.store`` sob a chave ``google_analytics_id``.
        """
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                # 1. Busca as contas e propriedades do usuário
                res_summaries = await client.get(
                    "https://analyticsadmin.googleapis.com/v1beta/accountSummaries",
                    headers=headers,
                )

                if res_summaries.status_code == 200:
                    data = res_summaries.json()
                    accounts = data.get("accountSummaries", [])

                if not accounts:
                    return None

                    # Pega a primeira propriedade da primeira conta
                first_property = accounts[0].get("propertySummaries", [])[0].get("property")

                # 2. Busca o Data Stream (para extrair o Measurement ID: G-XXXX)
                res_streams = await client.get(
                    f"https://analyticsadmin.googleapis.com/v1beta/{first_property}/dataStreams",
                    headers=headers,
                )

                if res_streams.status_code == 200:
                    streams = res_streams.json().get("dataStreams", [])
                    for stream in streams:
                        if "webStreamData" in stream:
                            ga_id = stream["webStreamData"].get("measurementId")
                            print(f"Google Analytics ID encontrado: {ga_id}")
                            return ga_id
        except Exception as ex:
            print(f"[GOOGLE ANALYTICS ERRO] {ex}")

        return None


    async def handle_login_google(self) -> None:
        """
        Inicia o fluxo de autenticação OAuth2 com o Google.

        Aciona o mecanismo interno do Flet para abrir o popup ou
        redirecionar o usuário para a página de autorização do Google.
        Após a autorização (ou recusa), o Flet chama automaticamente
        o callback ``_on_login``.
        """
        await self._page.login(provider=self._provider)

    async def _on_login(self, e) -> None:
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
                - ``e.error`` (str | None): Mensagem de erro se o login falhou.

        Flow:
            1. Verifica ``e.error`` — se presente, exibe SnackBar e encerra.
            2. Obtém o ``token_obj`` via ``page.auth.get_token()``.
            3. Salva ``access_token`` e ``refresh_token`` do Google na session.store.
            4. Extrai ``email``, ``sub`` (id) e ``name`` de ``page.auth.user``.
            5. Chama ``LoginModel.login_google()`` para autenticar no backend.
            6. Se sucesso: salva tokens da API em session.store e
               SharedPreferences, depois navega para ``/main``.
            7. Se falha: comunica erro à View via ``_on_show_error``.
            8. Em caso de exceção de rede: registra no console via ``print``.

        Side Effects:
            Armazena as seguintes chaves após login bem-sucedido:
            - session.store: ``google_access_token``, ``google_refresh_token``,
              ``r_token``, ``token``, ``id``.
            - SharedPreferences: ``r_token``, ``id``, ``google_refresh_token``,
              ``login_method`` (valor: ``"google"``).
        """
        if e.error:
            self._on_show_error("Erro", f"Houve um erro: {e.error}")
            print(e.error)
            return

        token_obj = await self._page.auth.get_token()

        self._page.session.store.set("google_access_token", token_obj.access_token)
        self._page.session.store.set("google_refresh_token", token_obj.refresh_token)

        g_user = self._page.auth.user

        g_mail  = g_user["email"]
        g_id    = g_user["sub"]
        g_name  = g_user["name"]
        g_token = token_obj.access_token
        r_token = token_obj.refresh_token

        try:
            try:
                ads_id = await self.fetch_google_ads_id(g_token)
                if ads_id:
                    try:
                        contas_detalhes_local = await ft.SharedPreferences().get("contas_detalhes")
                    except Exception:
                        await ft.SharedPreferences().remove("contas_detalhes")
                        contas_detalhes_local = None

                    if not contas_detalhes_local:
                        contas_detalhes = await self.fetch_google_ads_accounts_details(g_token, ads_id)
                        await ft.SharedPreferences().set("contas_detalhes", json.dumps(contas_detalhes))
                        
            except Exception as ex:
                print(f"Erro ao buscar Google Ads ID: {ex}")
                ads_id = None

            result = await self._model.login_google(
                g_mail, g_id, g_token, g_name, ads_id, r_token
            )

            if result.success:
                # Sessão (volátil): autorizar chamadas às APIs protegidas
                self._page.session.store.set("r_token", result.r_token)
                self._page.session.store.set("token",   result.token)
                self._page.session.store.set("id",      result.user_id)

                # Persistente: auto-login na próxima sessão
                _storage = SecureStorage()
                await _storage.set("r_token", result.r_token)
                await _storage.set("google_refresh_token", token_obj.refresh_token or "")
                await ft.SharedPreferences().set("id", str(result.user_id))
                await ft.SharedPreferences().set("login_method", "google")

                # Busca o Analytics ID em background
                ga_id = await self.fetch_google_analytics_id(g_token)
                if ga_id:
                    self._page.session.store.set("google_analytics_id", ga_id)

                self._page.update()
                await self._on_navigate("/main")
            else:
                self._on_show_error(
                    "Erro de Autenticação",
                    f"Falha ao autenticar com Google no servidor. Status: {result.status_code}",
                )

        except Exception as ex:
            print(f"Erro na requisição ao backend: {ex}")


    async def fetch_google_calendar_events(self) -> None:
        """
        Busca os próximos eventos do Google Calendar do usuário autenticado.

        Realiza uma chamada direta à Google Calendar API usando o access token
        do Google armazenado na sessão atual. Exibe os eventos encontrados no
        console (log técnico).

        Note:
            Este método está implementado mas **não está sendo chamado**
            (a linha de invocação em ``_on_login`` está comentada). É uma
            feature planejada para versões futuras da aplicação.
            O escopo ``calendar.events`` já é solicitado no OAuth2, portanto
            não há necessidade de reautenticação para ativá-la.

        API Endpoint:
            GET https://www.googleapis.com/calendar/v3/calendars/primary/events

        Query Params:
            - timeMin (str): Data/hora atual em UTC no formato ISO 8601.
            - maxResults (int): Número máximo de eventos retornados (10).
            - singleEvents (bool): True para expandir eventos recorrentes.
            - orderBy (str): ``startTime`` para ordem cronológica ascendente.
        """
        token_obj = await self._page.auth.get_token()
        token = token_obj.access_token
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.utcnow().isoformat() + "Z"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers=headers,
                    params={
                        "timeMin": now,
                        "maxResults": 10,
                        "singleEvents": True,
                        "orderBy": "startTime",
                    },
                )

            if response.status_code == 200:
                events = response.json().get("items", [])
                if not events:
                    print("Nenhum evento encontrado.")
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(f"Evento: {start} - {event['summary']}")
            else:
                print(f"Erro na API do Google: {response.status_code} - {response.text}")

        except Exception as ex:
            print(f"Erro ao conectar com Google Calendar: {ex}")


    async def try_auto_login(self) -> None:
        """
        Tenta renovar a sessão do usuário automaticamente usando o refresh
        token persistido no dispositivo da sessão anterior (Auto Login).

        Chamado por ``LoginView.did_mount()`` em background. Comunica
        estado de carregamento à View via ``_on_show_loading`` callback.

        Flow:
            1. Lê ``r_token`` e ``id`` do ``SharedPreferences``.
            2. Se ``r_token`` existir, exibe loading e chama
               ``LoginModel.refresh_token()``.
            3. Se sucesso: atualiza tokens em session.store e
               SharedPreferences, restaura google_refresh_token,
               navega para ``/main``.
            4. Se falha: chama ``clear_persistent_tokens()`` para
               invalidar dados locais e forçar novo login.
            5. Oculta loading ao final, independente do resultado.

        Note:
            Se ``r_token`` não existir no SharedPreferences (primeiro
            acesso ou após logout), nenhuma ação é tomada e o usuário
            permanece na tela de login.
        """
        _storage = SecureStorage()
        r_token: str = await _storage.get("r_token")
        user_id: str = await ft.SharedPreferences().get("id")

        if not r_token:
            return

        self._on_show_loading(True)

        try:
            result = await self._model.refresh_token(r_token, user_id)

            if result.success:
                # SharedPreferences: atualiza persistência criptografada
                await _storage.set("r_token", result.r_token)
                await ft.SharedPreferences().set("id", user_id)

                # session.store: necessário para o MainView e demais views
                self._page.session.store.set("token",   result.token)
                self._page.session.store.set("r_token", result.r_token)
                self._page.session.store.set("id",      user_id)

                # Busca o google_refresh_token e coloca na sessão
                g_refresh = await _storage.get("google_refresh_token")
                if g_refresh:
                    self._page.session.store.set("google_refresh_token", g_refresh)

                self._page.update()
                await self._on_navigate("/main")
            else:
                # Token inválido/expirado: limpa persistência
                await self.clear_persistent_tokens()
        finally:
            self._on_show_loading(False)
            self._page.update()


    async def clear_persistent_tokens(self) -> None:
        """
        Remove todos os tokens de autenticação armazenados de forma persistente
        no ``SharedPreferences`` do dispositivo/navegador.

        Deve ser chamado nos seguintes cenários:
            - Logout explícito do usuário.
            - Falha na renovação do token (``r_token`` inválido ou expirado).
            - Detecção de sessão comprometida ou inválida.

        Após esta operação, o próximo acesso à aplicação exigirá que o
        usuário realize um novo login completo.

        Keys removidas:
            - ``r_token``: Refresh token da API backend.
            - ``id``: ID do usuário na API backend.
            - ``google_refresh_token``: Refresh token do Google OAuth2.
            - ``login_method``: Método de login utilizado.
        """
        _storage = SecureStorage()
        for key in ("r_token", "id", "google_refresh_token", "login_method"):
            await _storage.remove(key)


    async def handle_login(self, email: str, password: str) -> None:
        """
        Gerencia o fluxo completo de autenticação tradicional com e-mail e senha.

        Valida os campos de entrada, exibe o indicador de carregamento,
        chama o ``LoginModel`` e trata as diferentes respostas com
        feedback via callbacks.

        Args:
            email: E-mail informado pelo usuário.
            password: Senha informada pelo usuário.

        Flow:
            1. Valida se e-mail e senha foram preenchidos.
            2. Exibe loading.
            3. Chama ``LoginModel.login(email, senha)``.
            4. Processa o ``LoginResult``:
               - Sucesso: Salva tokens em session.store → Navega para ``/main``.
               - Falha: Exibe dialog com mensagem de erro do DTO.
            5. Em caso de exceção de rede: dialog de erro genérico.
            6. Oculta loading em todos os cenários.

        Note:
            O botão que aciona este método está atualmente comentado na
            ``LoginView``. O método principal de autenticação ativo é o
            Google OAuth2.
        """
        if not email or not password:
            self._on_show_error(
                "Atenção",
                "Por favor, preencha o e-mail e a senha.",
            )
            return

        self._on_show_loading(True)

        try:
            result = await self._model.login(email, password)

            if result.success:
                self._page.session.store.set("token",   result.token)
                self._page.session.store.set("r_token", result.r_token)
                self._page.session.store.set("id",      result.user_id)

                self._on_show_loading(False)
                self._page.update()
                await self._on_navigate("/main")
                return

            # Títulos de erro por status code
            _error_titles = {
                401: "Acesso Negado",
                404: "Usuário não encontrado",
                422: "Dados inválidos",
            }

            self._on_show_error(
                _error_titles.get(result.status_code, "Serviço indisponível"),
                result.error_message,
            )

            # Log técnico apenas no console para status inesperados
            if result.status_code not in (401, 404, 422):
                print(f"[LOGIN ERRO] Status: {result.status_code}")

        except Exception as ex:
            print(f"[LOGIN ERRO] Exceção: {ex}")
            self._on_show_error(
                "Erro de conexão",
                "Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.",
            )
        finally:
            self._on_show_loading(False)
            self._page.update()


    async def handle_forgot_password(self, email: str) -> None:
        """
        Gerencia o fluxo de recuperação de senha por e-mail.

        Valida se o e-mail foi informado, exibe o indicador de carregamento,
        chama o ``LoginModel`` e apresenta o feedback retornado pelo backend
        ao usuário via callback.

        Args:
            email: E-mail informado pelo usuário.

        Flow:
            1. Valida se e-mail está preenchido.
            2. Exibe loading.
            3. Chama ``LoginModel.recovery_password(email)``.
            4. Processa o ``RecoveryResult``:
               - 200: Exibe dialog de sucesso com mensagem do backend.
               - 404: Exibe dialog de erro com mensagem do backend.
            5. Oculta loading ao final.

        Note:
            O texto das mensagens de sucesso e erro são definidos
            inteiramente pelo backend.
        """
        if not email:
            self._on_show_error("Atenção", "Por favor informe o email.")
            return

        self._on_show_loading(True)

        try:
            result = await self._model.recovery_password(email)

            if result.success:
                self._on_show_message("Sucesso", result.message)
            else:
                self._on_show_error("Erro", result.message)
        finally:
            self._on_show_loading(False)
            self._page.update()