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
            text_button_1:str = 'Salvar'
        ):
        super().__init__()
        self.text_button_1 = text_button_1
        self.page = page
        self.width = width
        self.height = height
        self.open = False
        self.bgcolor = AppColors.GRAY_DARK
        self.callback = callback
        self.callback2 = callback2
        self.content = ft.Container(
            height=self.height,
            width=self.width,
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=controls,
                        ),
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(
                                expand=True,
                                controls=[
                                    ft.ElevatedButton(
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            side=ft.BorderSide(1, AppColors.GRAY_DARK),
                                        ),
                                        expand=True,
                                        height=45,
                                        elevation=5,
                                        text=self.text_button_1,
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
                                        text="Voltar",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            #side=ft.BorderSide(1, AppColors.GRAY_DARK),
                                            color=AppColors.GRAY_LIGHT,
                                        ),
                                        #on_click=lambda e:self.callback2(e)
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