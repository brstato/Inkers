import flet as ft
from view.controls.colors import AppColors

class CustomTextField(ft.TextField):
    def __init__( 
            self,
            label:str='', 
            value:str='',
            password:bool=False, 
            can_reveal_password:bool=False, 
            visible:bool=True,       
            on_change=None,
            on_blur=None,
            readOnly:bool=False,  
            keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT,
            regex: str = '.*',
            **kwargs            
        ):

        super().__init__(
            label=label,
            value=value,
            password=password,
            can_reveal_password=can_reveal_password,
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            bgcolor=AppColors.TRANSPARENT,
            color=AppColors.WHITE,
            label_style=ft.TextStyle(color=AppColors.WHITE),
            visible=visible,
            read_only=readOnly,
            on_change = on_change,
            on_blur = on_blur,
            keyboard_type=keyboard_type,
            input_filter = ft.InputFilter(regex_string=regex, replacement_string="", allow=True),
            expand=True,
            **kwargs
        )     



    
        

