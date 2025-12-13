import flet as ft
from view.controls.colors import AppColors

class CustomTextField(ft.TextField):
    def __init__(
            self, 
            label:str='', 
            password:bool=False, 
            can_reveal_password:bool=False,
            chars: str = '',  
            visible:bool=True,       
            on_change=None     
        ):

        super().__init__(
            label=label,
            password=password,
            can_reveal_password=can_reveal_password,
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            bgcolor=AppColors.TRANSPARENT,
            color=AppColors.WHITE,
            label_style=ft.TextStyle(color=AppColors.WHITE),
            input_filter=ft.InputFilter(allow=True, regex_string=chars, replacement_string=""),  
            visible=visible
            )     
        
        self.on_change = on_change

