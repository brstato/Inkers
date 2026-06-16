"""
view/loginview.py
-----------------
Tela inicial da aplicação, responsável pela interface de autenticação.

A comunicação com o ``LoginController`` acontece exclusivamente via:
    - **Callbacks** injetados no construtor do Controller, que ele
      invoca para feedback visual (loading, dialogs, navegação).
    - **Parâmetros** passados aos métodos do Controller — a View extrai
      os valores dos campos e os envia como argumentos simples (strings),
      em vez de enviar a si mesma (``self``).

Isso garante que:
    - O Controller não conhece nenhum controle da View
      (``txt_username``, ``progress_ring``, etc.).
    - A View pode ser redesenhada livremente sem alterar o Controller.
"""

import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custondialog import CustonDialog
from controller.logincontroller import LoginController


class LoginView(ft.View):
    """
    Tela inicial da aplicação, responsável pela interface de autenticação do usuário.

    Atende pela rota raiz (``"/"``) e é exibida sempre que o usuário não possui
    uma sessão ativa. Delega toda a lógica de negócio ao ``LoginController``,
    comunicando-se com ele via callbacks e parâmetros.

    Attributes:
        controller (LoginController): Instância do controller que gerencia
            toda a lógica de autenticação.
        progress_ring (CustonProgressRing): Indicador de carregamento exibido
            durante operações assíncronas (login, refresh token etc.).
        logo (ft.Image): Logotipo da aplicação exibido no centro da tela.
        txt_username (CustomTextField): Campo de entrada para e-mail
            (atualmente oculto na UI — login Google é o método ativo).
        txt_password (CustomTextField): Campo de entrada para senha com
            toggle de visibilidade (atualmente oculto na UI).
        btn_login_google (ft.Row): Botão principal "Entrar" via Google OAuth2.
        btn_login (ft.Row): Botão "Entrar" via e-mail/senha (oculto na UI).
        btn_create_account (ft.Row): Botão "Criar Conta" (oculto na UI).
        btn_forgot_password (ft.Row): Botão "Esqueci minha senha" (oculto na UI).
        btn_support (ft.Row): Botão de redirecionamento para suporte via WhatsApp.
        infor (ft.Row): Link clicável para o site inkers.com.br.
    """

    def __init__(self, page: ft.Page):
        """
        Inicializa a LoginView, instancia o controller (injetando callbacks
        de UI) e constrói todos os componentes visuais da interface de login.

        Args:
            page: Objeto principal do Flet que representa a janela/aba atual
                  da aplicação. Passado ao controller para permitir acesso
                  ao OAuth2 e session store.
        """
        super().__init__(
            route="/",
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=0,
        )

        # Controller recebe callbacks para comunicação com a View
        self.controller = LoginController(
            page,
            on_show_loading=self._set_loading,
            on_show_error=self._show_error_dialog,
            on_show_message=self._show_message_dialog,
            on_navigate=self._navigate,
        )

        self.progress_ring = CustonProgressRing(page.height)

        self.logo = ft.Image(
            width=300,
            src=f"inkers_logo.png",
        )

        self.txt_username = CustomTextField("Email", keyboard_type=ft.KeyboardType.EMAIL)
        self.txt_password = CustomTextField("Senha", password=True, can_reveal_password=True)


        self.btn_login_google = ft.Row(
            expand=True,
            controls=[
                ft.Button(
                    content=ft.Text("Entrar"),
                    bgcolor=AppColors.ORANGE_DARK,
                    color=AppColors.WHITE,
                    elevation=5,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    on_click=self._on_click_login_google,
                )
            ],
        )

        self.btn_login = ft.Row(
            expand=True,
            controls=[
                ft.Button(
                    content=ft.Text("Entrar"),
                    bgcolor=AppColors.ORANGE_BURNT,
                    color=AppColors.WHITE,
                    elevation=5,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    on_click=self._on_click_login,
                )
            ],
        )


        self.btn_create_account = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Criar Conta",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    on_click=self._go_to_account
                )
            ],
        )


        self.btn_forgot_password = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Esqueci minha senha",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    on_click=self._on_click_forgot,
                )
            ]
        )


        self.btn_support = ft.Row(
            expand=True,
            controls=[
                ft.OutlinedButton(
                    expand=True,
                    height=45,
                    content="Suporte",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    url="https://wa.me/5524998564421"
                )
            ],
        )

        self.infor = ft.Row(
            expand=True,
            controls=[
                ft.TextButton(content='inkers.com.br', expand=True, url='inkers.com.br')
            ]
        )


        main_container = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    self.logo,
                    #self.txt_username,
                    #self.txt_password,
                    #ft.Container(height=20), # Espaçamento
                    #self.btn_login,
                    self.btn_login_google,
                    #self.btn_create_account,
                    #self.btn_forgot_password,
                    self.btn_support,
                    self.infor
                ],
            ),

            padding=40,
        )

        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        content=main_container,
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    self.progress_ring,
                ],
            ),
        ]

    # ── Callbacks injetados no Controller ──────────────────────────

    def _set_loading(self, visible: bool) -> None:
        """Controla a visibilidade do progress ring (callback do Controller)."""
        self.progress_ring.visible = visible

    def _show_error_dialog(self, title: str, message: str) -> None:
        """Exibe um dialog de erro ao usuário (callback do Controller)."""
        dialog = CustonDialog(
            self.page,
            title=title,
            content=message,
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dialog)
        self.page.update()

    def _show_message_dialog(self, title: str, message: str) -> None:
        """Exibe um dialog informativo ao usuário (callback do Controller)."""
        dialog = CustonDialog(
            self.page,
            title=title,
            content=message,
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dialog)
        self.page.update()

    async def _navigate(self, route: str) -> None:
        """Navega para a rota especificada (callback do Controller)."""
        if route == "/main":
            await self.page.push_route(route)
        else:
            self.page.go(route)

    # ── Ciclo de vida ──────────────────────────────────────────────

    def did_mount(self):
        """
        Método de ciclo de vida do Flet, chamado automaticamente pelo framework
        logo após a view ser montada e exibida na tela.

        Responsabilidade:
            Dispara a tentativa de "Auto Login" em background usando o
            refresh_token persistido no dispositivo da sessão anterior.
            Utiliza ``page.run_task()`` para não bloquear a thread principal
            da UI durante a requisição assíncrona.

        Comportamento:
            - Se um ``r_token`` válido existir em SharedPreferences:
              o usuário é autenticado silenciosamente e redirecionado.
            - Se não existir ou for inválido:
              a tela de login permanece exibida aguardando interação.
        """
        self.page.run_task(self._auto_login_task)


    async def _auto_login_task(self):
        """
        Tarefa assíncrona de auto login, executada em background pelo ``did_mount``.

        Delega ao controller a lógica de tentativa de renovação de sessão
        via refresh token. O controller usa os callbacks injetados para
        controlar o progress_ring e navegar.
        """
        await self.controller.try_auto_login()

    # ── Handlers de eventos ────────────────────────────────────────

    async def _go_to_account(self, e):
        """
        Navega para a tela de criação de conta (``/account``).

        Acionado pelo ``btn_create_account`` (atualmente comentado na UI).

        Args:
            e: Evento de clique do Flet (não utilizado diretamente).
        """
        await self.page.push_route("/account")


    async def _on_click_forgot(self, e):
        """
        Manipulador do clique em "Esqueci minha senha".

        Extrai o e-mail do campo ``txt_username`` e passa como parâmetro
        ao controller — o controller nunca acessa o campo diretamente.

        Args:
            e: Evento de clique do Flet.
        """
        email = self.txt_username.value
        await self.controller.handle_forgot_password(email)


    async def _on_click_login_google(self, e):
        """
        Manipulador do clique no botão principal de login via Google OAuth2.

        Delega ao controller o início do fluxo de autorização OAuth2,
        que abre o popup/redirecionamento do Google para o usuário.

        Args:
            e: Evento de clique do Flet (não utilizado diretamente).
        """
        await self.controller.handle_login_google()


    async def _on_click_login(self, e):
        """
        Manipulador do clique no botão de login tradicional (e-mail e senha).

        Extrai e-mail e senha dos campos da View e passa como parâmetros
        ao controller — o controller nunca acessa os campos diretamente.

        Args:
            e: Evento de clique do Flet.

        Note:
            O botão que aciona este método (``btn_login``) está atualmente
            comentado no layout da view. O método permanece implementado
            para futura reativação da feature.
        """
        email = self.txt_username.value
        password = self.txt_password.value
        await self.controller.handle_login(email, password)