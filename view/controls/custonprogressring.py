import flet as ft
from view.controls.colors import AppColors

class CustonProgressRing(ft.Container):
    def __init__(self, 
                 height:int = 0, 
                 visible: bool = False
                 ):
        super().__init__(
            height=height,
            expand=True,
            blur=10,
            alignment=ft.alignment.center,
            visible=visible,
            bgcolor=AppColors.BLACK,
            opacity=0.5,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Container(
                        expand=True,
                    ),
                    ft.ProgressRing(
                        color=AppColors.ORANGE_BURNT,
                        stroke_width=7,
                        width=50, 
                        height=50, 
                        visible=True
                    ),                     
                    ft.Container(
                        expand=True,
                    ),                  

                ],
            ),            
        )

