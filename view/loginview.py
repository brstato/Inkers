import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.logincontroller import LoginController
from view.controls.custonprogressring import CustonProgressRing


class LoginView(ft.View):
    """
    Tela inicial da aplicação, responsável pela interface de autenticação do usuário.

    Atende pela rota raiz ("/") e é exibida sempre que o usuário não possui
    uma sessão ativa. Delega toda a lógica de negócio ao `LoginController`.

    Fluxo de inicialização:
        1. O construtor monta todos os componentes visuais.
        2. `did_mount()` é chamado automaticamente pelo Flet após a montagem,
           disparando a tentativa de auto login via refresh token em background.

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
        Inicializa a LoginView, instancia o controller e constrói todos
        os componentes visuais da interface de login.

        Args:
            page (ft.Page): Objeto principal do Flet que representa a janela/aba
                            atual da aplicação. Passado ao controller para
                            permitir navegação, dialogs e acesso à sessão.
        """
        super().__init__(
            route="/",
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=0,
        )

        self.controller = LoginController(page)

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


    def did_mount(self):
        """
        Método de ciclo de vida do Flet, chamado automaticamente pelo framework
        logo após a view ser montada e exibida na tela.

        Responsabilidade:
            Dispara a tentativa de "Auto Login" em background usando o
            `refresh_token` persistido no dispositivo da sessão anterior.
            Utiliza `page.run_task()` para não bloquear a thread principal
            da UI durante a requisição assíncrona.

        Comportamento:
            - Se um `r_token` válido existir em `SharedPreferences`:
              o usuário é autenticado silenciosamente e redirecionado para `/main`.
            - Se não existir ou for inválido:
              a tela de login permanece exibida aguardando interação do usuário.
        """
        self.page.run_task(self._refresh_token_task)


    async def _refresh_token_task(self):
        """
        Tarefa assíncrona de auto login, executada em background pelo `did_mount`.

        Wrapper que delega ao controller a lógica de tentativa de renovação
        de sessão via refresh token, passando a própria instância da view
        para que o controller possa manipular o `progress_ring`.
        """
        await self.controller.refresh_token(self)


    async def _go_to_account(self, e):
        """
        Navega para a tela de criação de conta (`/account`).

        Acionado pelo `btn_create_account` (atualmente comentado na UI).

        Args:
            e: Evento de clique do Flet (não utilizado diretamente).
        """
        await self.page.push_route("/account")


    async def _on_click_forgot(self, e):
        """
        Manipulador do clique em "Esqueci minha senha".

        Delega ao controller o fluxo de recuperação de senha, passando
        a instância da view para leitura do campo `txt_username` (e-mail).

        Args:
            e: Evento de clique do Flet, repassado ao controller.
        """
        await self.controller.handler_forgot_password(e, self)


    async def _on_click_login_google(self, e):
        """
        Manipulador do clique no botão principal de login via Google OAuth2.

        Delega ao controller o início do fluxo de autorização OAuth2,
        que abre o popup/redirecionamento do Google para o usuário.

        Args:
            e: Evento de clique do Flet (não utilizado diretamente pelo controller).
        """
        await self.controller.handle_login_google()


    async def _on_click_login(self, e):
        """
        Manipulador do clique no botão de login tradicional (e-mail e senha).

        Delega ao controller o fluxo de autenticação convencional, passando
        a instância da view para leitura dos campos `txt_username` e
        `txt_password` e para controle do `progress_ring`.

        Args:
            e: Evento de clique do Flet, repassado ao controller para
               verificação de campos e tratamento de feedback visual.

        Note:
            O botão que aciona este método (`btn_login`) está atualmente
            comentado no layout da view. O método permanece implementado
            para futura reativação da feature.
        """
        await self.controller.handle_login(e, self)