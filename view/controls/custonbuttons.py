import flet as ft
from view.controls.colors import AppColors

class CustonButton(ft.ElevatedButton):
    def __init__(self, page:ft.Page, text:str = '', route:str=''):
        super().__init__(
            text = text,
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
        self.page = page
        self.on_click=lambda e: self.page.go(self.route)  

