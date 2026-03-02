import flet as ft
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from controller.studiocontroller import StudioController

class EstudioView(ft.View):
    def __init__(self, page: ft.Page, name: str = ""):
        super().__init__(
            route=f"/estudio",
            bgcolor=AppColors.BLACK,
            scroll=ft.ScrollMode.AUTO,
            padding=0,
        )
        self.name = name
        self.progress_ring = CustonProgressRing()
        self.controller = StudioController(page, self)

        self.txt_name_studio = ft.Text("Estúdio", size=20, weight=ft.FontWeight.BOLD, color=AppColors.WHITE)

        top_bar = ft.Container(
            content=ft.Row(
                controls=[
                    self.txt_name_studio,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=20, horizontal=20),
            bgcolor=AppColors.GRAY_DARK,
        )
        # --- Hero Section ---
        hero_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Transforme sua ideia em arte.",
                        size=48,
                        weight=ft.FontWeight.W_900,
                        color=AppColors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Tatuagens exclusivas e autorais feitas sob medida para você.\nEstúdio focado em biossegurança e resultados premium.",
                        size=18,
                        color=AppColors.GRAY_LIGHT2,
                        text_align=ft.TextAlign.CENTER,
                        #spacing=10,
                    ),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        content="AGENDAR MEU ORÇAMENTO",
                        bgcolor=AppColors.ORANGE_BURNT,
                        color=AppColors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.all(20),
                        ),
                        on_click=self.go_to_home, # Redireciona pro app ou chama ação
                    ),
                    ft.Container(height=10),
                    ft.TextButton(
                        content="Conhecer mais do estúdio",
                        style=ft.ButtonStyle(color=AppColors.GRAY_LIGHT2),
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=page.width,
            padding=ft.padding.symmetric(vertical=80, horizontal=20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[AppColors.BACKGROUND_DARK, AppColors.GRAY_DARK],
            ),
            alignment=ft.Alignment.CENTER,
        )

        # --- Styles / Services Section ---
        style_cards = [
            self._create_style_card("Realismo", "Arte hiper-realista em preto e sombra ou colorida.", ft.Icons.BRUSH),
            self._create_style_card("Fineline", "Traços finos, delicados e elegantes.", ft.Icons.CREATE),
            self._create_style_card("Blackwork", "Estilo marcante focado em tinta preta intensa.", ft.Icons.FORMAT_PAINT),
            self._create_style_card("Old School", "Tradicional, cores sólidas e traços definidos.", ft.Icons.ANCHOR),
        ]

        styles_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Nossas Especialidades", size=32, weight=ft.FontWeight.BOLD, color=AppColors.ORANGE_BURNT),
                    ft.Text("Três artistas residentes especializados em estilos variados.", size=16, color=AppColors.GRAY_LIGHT3),
                    ft.Container(height=30),
                    ft.ResponsiveRow(
                        controls=style_cards,
                        alignment=ft.MainAxisAlignment.CENTER,
                        run_spacing=20,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=60, horizontal=20),
            bgcolor=AppColors.BACKGROUND_DARK,
        )

        # --- How It Works Section ---
        steps_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Como funciona?", size=32, weight=ft.FontWeight.BOLD, color=AppColors.ORANGE_BURNT),
                    ft.Container(height=30),
                    ft.ResponsiveRow(
                        controls=[
                            self._create_step_card("1. A Ideia", "Conte sua história e suas referências. Faremos o orçamento.", "1", ft.Icons.CHAT_BUBBLE_OUTLINE),
                            self._create_step_card("2. O Design", "Preparamos um desenho autoral e exclusivo para você.", "2", ft.Icons.DESIGN_SERVICES),
                            self._create_step_card("3. A Tatuagem", "Marcamos a sessão no nosso estúdio com todo o conforto.", "3", ft.Icons.CHECK_CIRCLE_OUTLINE),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=60, horizontal=20),
            bgcolor=AppColors.GRAY_DARK,
        )

        # --- Social Proof / Guarantee ---
        guarantee_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=AppColors.ORANGE_DARK),
                    ft.Container(height=20),
                    ft.Text("Qualidade e Biossegurança", size=28, weight=ft.FontWeight.BOLD, color=AppColors.WHITE),
                    ft.Text(
                        "Utilizamos apenas materiais descartáveis, agulhas premium e tintas regulamentadas.\nSeu conforto e segurança são nossa prioridade máxima.",
                        size=16,
                        color=AppColors.GRAY_LIGHT2,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=60, horizontal=20),
            bgcolor=AppColors.BACKGROUND_DARK,
        )

        # --- Footer / Final CTA ---
        footer_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Pronto para começar?", size=36, weight=ft.FontWeight.BOLD, color=AppColors.WHITE),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        content="FALAR NO WHATSAPP",
                        icon=ft.Icons.CHAT,
                        bgcolor=ft.Colors.GREEN_700,
                        color=AppColors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.all(20),
                        ),
                    ),
                    ft.Container(height=40),
                    ft.Text("© 2026 Inkers App - Studio System. Todos os direitos reservados.", size=12, color=AppColors.GRAY_MED)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=60, horizontal=20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[AppColors.GRAY_DARK, AppColors.BLACK],
            ),
        )

        self.controls = [
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            top_bar,
                            hero_content,
                            styles_content,
                            steps_content,
                            guarantee_content,
                            footer_content,
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    self.progress_ring,
                ]
            ),
        ]

    def _create_style_card(self, title, description, icon):
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=40, color=AppColors.ORANGE_DARK),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=AppColors.WHITE),
                    ft.Text(description, size=14, color=AppColors.GRAY_LIGHT3, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            bgcolor=AppColors.GRAY_MED3,
            border_radius=12,
            border=ft.border.all(1, AppColors.GRAY_MED2),
        )

    def _create_step_card(self, title, description, step_num, icon):
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(step_num, size=24, weight=ft.FontWeight.BOLD, color=AppColors.BACKGROUND_DARK),
                        bgcolor=AppColors.ORANGE_BURNT,
                        width=50,
                        height=50,
                        border_radius=25,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=AppColors.WHITE),
                    ft.Text(description, size=14, color=AppColors.GRAY_LIGHT3, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
        )

    def go_to_home(self, e):
        self.page.go("/main")


    def did_mount(self):
        self.page.run_task(self.aux)    
        

    async def aux(self):
        await self.controller.get_info_studio(self.name)    
        