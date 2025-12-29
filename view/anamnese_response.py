import flet as ft
from view.controls.colors import AppColors

class AnamneseResponse(ft.View):
    def __init__(self):
        super().__init__(
            route="/anamneseresponse", 
            scroll="auto",
            bgcolor=AppColors.BACKGROUND_DARK                  
        )

        self.agradecimento = ft.Row(
            controls=[
                ft.Container(expand=True),
                ft.Text(
                    value="Obrigado por preencher sua anamnese!",
                    color=AppColors.GRAY_LIGHT,
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),    
                ft.Container(expand=True),
            ],
        )

        self.controls = [
            self.agradecimento,
        ]
