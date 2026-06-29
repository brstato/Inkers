"""
model/loginmodel.py
-------------------
Camada de Model responsável por toda comunicação HTTP com a API backend
relacionada ao fluxo de autenticação.

Retorna DTOs (Data Transfer Objects) tipados em vez de objetos crus do
httpx, eliminando o acoplamento entre Controller e a biblioteca HTTP.

Compatibilidade: Os métodos `refresh_token()` e `login()` originais que
retornam ``httpx.Response`` foram preservados como ``refresh_token_raw()``
e ``login_raw()`` para não quebrar os demais controllers que ainda os
utilizam diretamente (accountcontroller, call_api, etc.). Esses métodos
serão descontinuados em uma futura refatoração geral.
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass
from model.config import Config


# ── Data Transfer Objects (DTOs) ────────────────────────────────────

@dataclass(frozen=True)
class LoginResult:
    """Resultado unificado para login tradicional e login Google."""
    success: bool
    status_code: int
    token: str = ""
    r_token: str = ""
    user_id: str = ""
    error_message: str = ""


@dataclass(frozen=True)
class RefreshResult:
    """Resultado da tentativa de renovação de token."""
    success: bool
    status_code: int
    token: str = ""
    r_token: str = ""


@dataclass(frozen=True)
class RecoveryResult:
    """Resultado do fluxo de recuperação de senha."""
    success: bool
    status_code: int
    message: str = ""


# ── Model ───────────────────────────────────────────────────────────

class LoginModel:
    """
    Camada de Model responsável por toda comunicação HTTP com a API backend
    relacionada ao fluxo de autenticação.

    Utiliza a biblioteca `httpx` para requisições assíncronas.
    Os endpoints são centralizados em `model.config.Config`.

    Os métodos principais retornam DTOs tipados (`LoginResult`,
    `RefreshResult`, `RecoveryResult`) em vez de `httpx.Response`,
    encapsulando parsing de JSON e interpretação de status codes.
    """

    _recovery_password_url: str = Config.RECOVERY_PASSWORD_URL
    _login_url: str             = Config.LOGIN_URL
    _refresh_token_url: str     = Config.REFRESH_TOKEN_URL
    _login_google_url: str      = Config.LOGIN_GOOGLE_URL

    _DEFAULT_HEADERS = {"Content-Type": "application/json"}

    # ── Métodos com DTO (usados pelo LoginController) ───────────────

    async def login_google(
        self,
        g_email: str,
        g_id: str,
        g_token: str,
        g_name: str,
        ads_id: str,
        r_token: str,
    ) -> LoginResult:
        """
        Autentica um usuário no backend da aplicação usando as credenciais
        provenientes do provedor Google OAuth2.

        Args:
            g_email: Endereço de e-mail da conta Google do usuário.
            g_id: Identificador único do usuário no Google (``sub`` do JWT).
            g_token: Access token emitido pelo Google OAuth2.
            g_name: Nome completo do usuário na conta Google.
            ads_id: ID da conta Google Ads do usuário (pode ser None).
            r_token: Refresh token do Google OAuth2.

        Returns:
            LoginResult: DTO com ``success``, ``token``, ``r_token`` e
                ``user_id`` em caso de sucesso; ou ``error_message``
                em caso de falha.
        """
        payload = {
            "g_email": g_email,
            "g_id":    g_id,
            "g_token": g_token,
            "g_name":  g_name,
            "ads_id":  ads_id,
            "r_token": r_token,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url=self._login_google_url,
                json=payload,
                headers=self._DEFAULT_HEADERS,
            )

        return self._parse_login_response(response)

    async def login(self, username: str, password: str) -> LoginResult:
        """
        Autentica um usuário no backend usando credenciais tradicionais
        de e-mail e senha.

        Args:
            username: Endereço de e-mail do usuário.
            password: Senha do usuário em texto simples.

        Returns:
            LoginResult: DTO com ``success``, ``token``, ``r_token`` e
                ``user_id`` em caso de sucesso; ou ``status_code`` e
                ``error_message`` em caso de falha.

        Note:
            Esta feature está implementada e funcional no backend, mas a sua
            interface visual (campos e botão) está atualmente comentada
            na ``LoginView``, pois o método principal de acesso é o Google OAuth2.
        """
        payload = {
            "email": username,
            "senha": password,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self._login_url,
                json=payload,
                headers=self._DEFAULT_HEADERS,
            )

        return self._parse_login_response(response)

    async def refresh_token(self, r_token: str, user_id: str) -> RefreshResult:
        """
        Renova a sessão do usuário usando um refresh token previamente
        persistido, sem exigir que o usuário realize um novo login.

        Args:
            r_token: Refresh token armazenado no dispositivo.
            user_id: ID do usuário armazenado localmente.

        Returns:
            RefreshResult: DTO com ``success``, ``token`` e ``r_token``
                em caso de renovação bem-sucedida.
        """
        response = await self._do_refresh_request(r_token, user_id)

        if response.status_code == 200:
            data = response.json()
            return RefreshResult(
                success=True,
                status_code=200,
                token=data["token"],
                r_token=data["r_token"],
            )

        return RefreshResult(success=False, status_code=response.status_code)

    async def recovery_password(self, email: str) -> RecoveryResult:
        """
        Dispara o fluxo de recuperação de senha no backend.

        Args:
            email: Endereço de e-mail do usuário.

        Returns:
            RecoveryResult: DTO com ``success``, ``status_code`` e
                ``message`` (texto personalizado do backend).

        Note:
            Timeout de 30s pois o envio de e-mail pode ser lento.
        """
        payload = {"email": email}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url=self._recovery_password_url,
                json=payload,
                headers=self._DEFAULT_HEADERS,
            )

        data = response.json()
        message = data.get("message", "")

        return RecoveryResult(
            success=(response.status_code == 200),
            status_code=response.status_code,
            message=message,
        )

    # ── Métodos legacy (backward compat para outros controllers) ────
    #    Serão removidos quando os demais controllers forem refatorados.

    async def refresh_token_raw(self, r_token: str, user_id: str) -> httpx.Response:
        """
        Versão legacy de ``refresh_token()`` que retorna ``httpx.Response``
        diretamente, para compatibilidade com controllers que ainda leem
        ``response.status_code`` e ``response.json()`` manualmente.

        .. deprecated::
            Use ``refresh_token()`` que retorna ``RefreshResult``.
        """
        return await self._do_refresh_request(r_token, user_id)

    # ── Helpers privados ────────────────────────────────────────────

    async def _do_refresh_request(
        self, r_token: str, user_id: str
    ) -> httpx.Response:
        """Executa a requisição HTTP de refresh de token (uso interno)."""
        payload = {
            "uuid":    user_id,
            "r_token": r_token,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self._refresh_token_url,
                json=payload,
                headers=self._DEFAULT_HEADERS,
            )
        return response

    @staticmethod
    def _parse_login_response(response: httpx.Response) -> LoginResult:
        """Converte um httpx.Response de login em um LoginResult tipado."""
        if response.status_code == 200:
            data = response.json()
            return LoginResult(
                success=True,
                status_code=200,
                token=data["token"],
                r_token=data["r_token"],
                user_id=str(data["message"]["id"]),
            )

        # Mensagens de erro mapeadas por status code
        _error_messages = {
            401: "E-mail ou senha incorretos.",
            404: "Não encontramos uma conta com esse e-mail. Verifique o e-mail informado.",
            422: "Verifique os dados informados e tente novamente.",
        }

        return LoginResult(
            success=False,
            status_code=response.status_code,
            error_message=_error_messages.get(
                response.status_code,
                "Não foi possível realizar o login no momento. Tente novamente mais tarde.",
            ),
        )