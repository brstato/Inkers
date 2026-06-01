import flet as ft
from view.controls.colors import AppColors

class CustonButton(ft.Button):
    def __init__(self, page:ft.Page, text:str = '', route:str=''):
        super().__init__(
            content = text,
            bgcolor=AppColors.GRAY_DARK,
            color=AppColors.WHITE,
            elevation=5,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, AppColors.GRAY_LIGHT4),
                color=AppColors.GRAY_LIGHT,
            ),
            width=250,
            height=45,          
        )

        self.route = route
        self.on_click=self._go_to_route 


    async def _go_to_route(self, e):
        await self.page.push_route(self.route)

