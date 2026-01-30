import flet as ft
from view.controls.colors import AppColors

class CustonDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, title: str = '', content: str = '', actions: list = None):
        
        super().__init__()

        #self.page = page
        self.bgcolor = AppColors.BACKGROUND_DARK
        self.title = ft.Text(title, color=AppColors.GRAY_LIGHT) 
        self.content = ft.Text(content, color=AppColors.GRAY_LIGHT) 
        self.modal = True
        self.actions = actions
        self.elevation = 10

        #dialog = ft.AlertDialog()

  