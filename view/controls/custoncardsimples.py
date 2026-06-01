import flet as ft
from view.controls.colors import AppColors


class CustonCardSimples(ft.Card):
    def __init__(self, page:ft.Page, id:int, tap:callable=None, title:str = '', instance=None):

        super().__init__()
        self.title = title
        self.tap = tap
        self.shadow_color=AppColors.BLACK
        self.elevation=5
#        self.page = page
        self.id = id
        self.selected = False    
        self.instance = instance
        
        
        self.container = ft.Container(     
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),                   
            border=None,
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(10),
            bgcolor=AppColors.GRAY_DARK,
            height=50,
            width=300,
            content=ft.Text(                                                    
                value=self.title,
                color=AppColors.GRAY_LIGHT,
                size=15,
                max_lines=1,
            ), 
        )  

        
        self.content = ft.GestureDetector(
            content=ft.Stack(
                controls=[
                    self.container,
                ],
            ),
            on_tap=self.on_tap_callback,
            on_double_tap=lambda e:self.on_double_tap(e)
        )
     

    def on_double_tap(self, e):
        self.instance.text_client.value = self.title
        self.instance.text_client.visible = True
        self.instance.id_client = self.id
        self.page.pop_dialog()
        self.page.update()       


    def on_tap_callback(self, e):
        if self.tap:
            
            self.instance.text_client.value = self.title
            self.instance.text_client.visible = True
            self.instance.id_client = self.id            
            self.page.update()

            self.tap(self)


    def select(self):
        self.instance.text_client.value = self.title
        self.instance.id_client = self.id       
        self.container.border = ft.border.all(2, AppColors.ORANGE_BURNT)
        self.selected = True
        self.update()


    def deselect(self):
        self.container.border = None
        self.selected = False
        self.update()          


   
        