import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField


class CustonModalView(ft.AlertDialog):
    def __init__(
            self, 
            page:ft.Page, 
            callback:None, 
            callback2:None, 
            controls:list=[], 
            height:int=300, 
            width:int=300,
            text_button_1:str = 'Salvar',
            content_padding=ft.Padding.all(3),
            padding=ft.Padding.all(3),
            margin=ft.Margin.all(5)
        ):
        super().__init__()
        self.text_button_1 = text_button_1
        self.content_padding = content_padding
        self.padding = padding
        self.margin = margin
        page = page
        self.width = width
        self.height = height
        self.open = False
        self.bgcolor = AppColors.GRAY_DARK
        self.callback = callback
        self.callback2 = callback2
        self.content = ft.Container(
            height=self.height,
            width=self.width,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=controls,
                            spacing=10,
                        ),
                        padding=10,
                    ),
                    ft.Container(height=10),
                    ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                expand=True,
                                controls=[
                                    ft.Button(
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            side=ft.BorderSide(1, AppColors.GRAY_DARK),
                                        ),
                                        expand=True,
                                        height=45,
                                        elevation=5,
                                        content=self.text_button_1,
                                        bgcolor=AppColors.ORANGE_BURNT,
                                        color=AppColors.GRAY_LIGHT,

                                        on_click=self.save
                                    )
                                ],
                            ),
                            ft.Row(
                                expand=True,
                                controls=[
                                    ft.OutlinedButton(
                                        expand=True,
                                        height=45,
                                        content="Fechar",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            color=AppColors.GRAY_LIGHT,
                                        ),
                                        on_click=self.close
                                    )
                                ],
                            ),                        
                        ],
                    ),                
                ]
            )
        )


    async def save(self, e):
        await self.callback(e)

    def close(self, e):
        self.callback2(e)