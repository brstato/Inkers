import httpx
from model.config import Config

class LoginModel:
    """
    Camada de Model responsável por toda comunicação HTTP com a API backend
    relacionada ao fluxo de autenticação.

    Utiliza a biblioteca `httpx` para requisições assíncronas.
    Os endpoints são centralizados em `model.config.Config`.
    """

    recovery_passwordURL: str = Config.RECOVERY_PASSWORD_URL
    loginURL: str             = Config.LOGIN_URL
    refreshTokenURL: str      = Config.REFRESH_TOKEN_URL
    logingoogleURL: str       = Config.LOGIN_GOOGLE_URL


    async def login_google(self, g_email: str, g_id: str, g_token: str, g_name: str) -> httpx.Response:
        """
        Autentica um usuário no backend da aplicação usando as credenciais
        provenientes do provedor Google OAuth2.

        Após o usuário autorizar o acesso no popup do Google, os dados de
        identificação são enviados ao backend para que ele valide o token,
        crie ou localize o usuário e retorne tokens próprios da API.

        Args:
            g_email (str): Endereço de e-mail da conta Google do usuário.
            g_id (str): Identificador único do usuário no Google (`sub` do JWT).
            g_token (str): Access token emitido pelo Google OAuth2.
            g_name (str): Nome completo do usuário na conta Google.

        Returns:
            httpx.Response: Resposta HTTP do backend.
                - Status 200: Autenticação bem-sucedida.
                  Corpo JSON contém `token`, `r_token` e `message.id`.
                - Outros status: Indicam falha na autenticação.
        """
        payload = {
            "g_email": g_email,
            "g_id":    g_id,
            "g_token": g_token,
            "g_name":  g_name
        }
        header = {
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.logingoogleURL,
                json=payload,
                headers=header
            )

        return response


    async def refresh_token(self, r_token: str, id: str) -> httpx.Response:
        """
        Renova a sessão do usuário usando um refresh token previamente persistido,
        sem exigir que o usuário realize um novo login.

        Chamado automaticamente no `did_mount` da LoginView para implementar
        o fluxo de "Auto Login" entre sessões da aplicação.

        Args:
            r_token (str): Refresh token armazenado no `SharedPreferences`
                           do dispositivo na última autenticação bem-sucedida.
            id (str): ID do usuário armazenado localmente, enviado como `uuid`.

        Returns:
            httpx.Response: Resposta HTTP do backend.
                - Status 200: Token renovado com sucesso.
                  Corpo JSON contém `token` (novo access token) e
                  `r_token` (novo refresh token para substituir o anterior).
                - Outros status: Refresh token inválido ou expirado;
                  tokens locais devem ser limpos e o usuário redirecionado
                  para o login.
        """
        payload = {
            "uuid":    id,
            "r_token": r_token
        }
        header = {
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.refreshTokenURL,
                json=payload,
                headers=header
            )

        return response


    async def recovery_password(self, username: str) -> httpx.Response:
        """
        Dispara o fluxo de recuperação de senha no backend para o e-mail informado.

        O backend é responsável por enviar um e-mail com as instruções de
        redefinição de senha ao usuário. Esta função apenas aciona o endpoint
        e retorna a resposta para que o Controller exiba o feedback adequado.

        Args:
            username (str): Endereço de e-mail do usuário que solicitou
                            a recuperação de senha.

        Returns:
            httpx.Response: Resposta HTTP do backend.
                - Status 200: E-mail de recuperação enviado com sucesso.
                  Corpo JSON contém `message` com texto para exibir ao usuário.
                - Status 404: E-mail não encontrado no sistema.
                  Corpo JSON contém `message` com texto de erro amigável.

        Note:
            Este método define timeout explícito de 30 segundos no cliente HTTP,
            pois o envio de e-mail pelo backend pode ser uma operação mais lenta.
        """
        payload = {
            "email": username
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url=self.recovery_passwordURL,
                json=payload,
                headers=header
            )

        return response


    async def login(self, username: str, password: str) -> httpx.Response:
        """
        Autentica um usuário no backend usando credenciais tradicionais
        de e-mail e senha.

        A criptografia/validação da senha é de responsabilidade exclusiva
        do backend. O campo de senha é enviado em texto simples via HTTPS.

        Args:
            username (str): Endereço de e-mail do usuário.
            password (str): Senha do usuário em texto simples.

        Returns:
            httpx.Response: Resposta HTTP do backend.
                - Status 200: Autenticação bem-sucedida.
                  Corpo JSON contém `token`, `r_token` e `message.id`.
                - Status 401: Credenciais inválidas (e-mail ou senha incorretos).
                - Status 404: Usuário não encontrado com o e-mail informado.
                - Status 422: Dados de entrada inválidos ou malformados.
                - Outros status: Erros inesperados do servidor.

        Note:
            Esta feature está implementada e funcional no backend, mas a sua
            interface visual (campos e botão) está atualmente comentada
            na `LoginView`, pois o método principal de acesso é o Google OAuth2.
        """
        payload = {
            "email": username,
            "senha": password
        }
        header = {
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.loginURL,
                json=payload,
                headers=header
            )

        return response