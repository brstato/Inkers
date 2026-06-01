import flet as ft
from view.controls.colors import AppColors

class GaleriaItem(ft.Container):
    def __init__(self, image:str = '', id:int = 0, delete_click: callable = None):
        super().__init__(
            width=100,
            height=100,
            border_radius=ft.border_radius.all(10),
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[
                    ft.Image(
                        src=image,
                        fit=ft.BoxFit.COVER,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        height=100,
                        width=100,
                    ),
                     ft.IconButton(
                         icon=ft.Icons.DELETE,
                         icon_color=AppColors.GRAY_LIGHT,
                         bottom=2,
                         right=2,
                         on_click=self.handle_delete
                     ),
                ]
            )
        )

        self.id = id
        self.delete_click_callback = delete_click

    async def handle_delete(self, e):
        import inspect
        if self.delete_click_callback:
            if inspect.iscoroutinefunction(self.delete_click_callback) or inspect.iscoroutine(self.delete_click_callback):
                await self.delete_click_callback(self.id)
            else:
                self.delete_click_callback(self.id)