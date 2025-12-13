import flet as ft
from view.controls.colors import AppColors

class CustonCardProfessional(ft.Card):
    def __init__(self, instance, name:str='', comission:int=0, id:int=0, tap:callable=None):
        super().__init__()

        self.name:str = name
        self.comission = comission
        self.id:int = id
        self.selected:bool = False
        self.tap = tap
        self.instance = instance

        self.height = 70
        self.width = 200
        
        self.border_radius=ft.border_radius.all(10)
        self.elevation=10
        self.padding = ft.padding.all(10)

        self.container=ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,  # Ponto inicial do gradiente
                end=ft.alignment.bottom_center, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK2,    # Cor inicial
                    AppColors.GRAY_DARK,   # Cor final
                ],                
            ),
            bgcolor = AppColors.GRAY_DARK,
            border=None,
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.all(10),
            content=ft.Row(
                controls=[
                    ft.Icon(name=ft.Icons.PERSON, color=AppColors.ORANGE_DARK),
                    ft.VerticalDivider(color=AppColors.ORANGE_DARK),
                    ft.Text(value=self.name, color=AppColors.GRAY_LIGHT, size=16)
                ],
            )
        )

        self.content=ft.GestureDetector(                
            content=self.container,
            on_tap=self.on_tap_callback,
        )     


    async def on_tap_callback(self, e):
        if self.tap:
            await self.tap(self)


    def select(self):
        self.container.border = ft.border.all(1, AppColors.ORANGE_BURNT)
        self.selected = True
        self.instance.id_prof = self.id
        self.instance.comission = self.comission
        self.update()


    def deselect(self):
        self.container.border = None
        self.selected = False
        self.update()         