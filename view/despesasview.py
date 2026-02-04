import flet as ft


class DespesasView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/despesas",
            bgcolor="#1E1E1E",
            scroll = ft.ScrollMode.AUTO
        )