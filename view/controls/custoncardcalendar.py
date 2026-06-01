import flet as ft
import datetime
from view.controls.colors import AppColors
        

class CustoncardMonth(ft.Card):
    def __init__(
            self, 
            page: ft.Page, 
            month:str='', 
            is_month:bool=False, 
            tap=None,
            data_do_mes: datetime.date = None    
        ):
        super().__init__()
        page = page
        self.month = month
        self.data_do_mes = data_do_mes
        self.tap = tap
        self.height = 50
        self.is_month = is_month
        self.month_name = ft.Text(
            value=self.month,
            color=AppColors.GRAY_LIGHT4,
            size=14
        )
        self.content = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.BACKGROUND_DARK,    # Cor inicial
                    AppColors.GRAY_DARK,   # Cor final
                ],                
            ),
            content=ft.GestureDetector(
                content=self.month_name,
                on_tap=self.on_tap_callback,
            )           
        )


    def did_mount(self):
        if self.is_month:
            self.month_name.color = AppColors.ORANGE_DARK
        else:
            self.month_name.color = AppColors.GRAY_LIGHT3


    def select(self):
        self.month_name.color = AppColors.ORANGE_DARK
        self.selected = True
        #self.update()            


    def deselect(self):
        self.month_name.color = AppColors.GRAY_LIGHT3
        self.selected = False
        #self.update()         


    async def on_tap_callback(self, e):
        if self.tap:
            await self.tap(self)        



class CustonCardDay(ft.Card):
    def __init__(self, page:ft.Page, card_date: datetime.date, is_hoje:bool=False, day_name:str='', tap:callable=None):
        super().__init__()

        page = page

        self.day:int = card_date.day
        self.card_date = card_date
        self.is_hoje:bool = is_hoje
        self.tap = tap
        self.day_name = day_name
        self.height = 70
        self.width = 50
        self.border_radius=ft.border_radius.all(10)
        self.elevation=10
        self.padding = ft.padding.all(10)

        self.indicator = ft.Container(
            bgcolor=AppColors.ORANGE_BURNT,
            top=22,
            left=15,
            height=9,
            width=9,
            border_radius=ft.border_radius.all(5),
            visible=False
        )

        self.bg_color = AppColors.ORANGE_DARK
        self.text_color = AppColors.WHITE

        self.day_number = ft.Text(
            value=str(self.day),
            color=AppColors.GRAY_LIGHT4,
            size=20,
            weight=ft.FontWeight.BOLD,
            top=30,
            left=10

        )

        self.day_of_week = ft.Text(
            value=str(self.day_name),
            color=AppColors.GRAY_LIGHT4,
            size=10,
            weight=ft.FontWeight.BOLD, 
            top=2, 
            left=8          
        )

        self.content = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.BACKGROUND_DARK,    # Cor inicial
                    AppColors.GRAY_DARK,   # Cor final
                ],                
            ),            
            #bgcolor=AppColors.GRAY_DARK2,
            border_radius=ft.border_radius.all(5),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[
                    ft.GestureDetector(
                        content=ft.Stack(
                            controls=[
                                self.day_of_week,
                                self.day_number,
                                self.indicator
                            ]
                        ),
                        on_tap=self.on_tap_callback
                    ),
                ]
            )
        )


    def did_mount(self):
        if self.is_hoje:
            self.day_number.color = AppColors.ORANGE_DARK
        else:
            self.day_number.color = AppColors.GRAY_LIGHT3 

        #page.update()    


    def select(self):
        self.day_number.color = AppColors.ORANGE_DARK
        self.selected = True
        #self.update()            


    def deselect(self):
        self.day_number.color = AppColors.GRAY_LIGHT3
        self.selected = False
        #self.update()         


    async def on_tap_callback(self, e):
        if self.tap:
            await self.tap(self)          



class CustonRowCalendar(ft.Row):
    def __init__(self, page:ft.Page, instance=None):
        super().__init__()

        self.instance = instance
#        page = page

        self.scroll=ft.ScrollMode.AUTO
        self.spacing=10  


    def on_card_selected(self, card_instance: CustoncardMonth):
        for card in self.controls:
            if isinstance(card, CustoncardMonth): 
                if card is card_instance:
                    card.select()
                    self.selected_card = card
                else:
                    card.deselect()



class CustonRowDays(ft.Row):                    
    def __init__(self, page:ft.Page, instance=None):
        super().__init__()

        self.instance = instance
        #page = page

        self.scroll=ft.ScrollMode.AUTO
        self.spacing=10  


    def on_card_selected(self, card_instance: CustonCardDay):
        for card in self.controls:
            if isinstance(card, CustonCardDay): 
                if card is card_instance:
                    card.select()
                    self.selected_card = card
                else:
                    card.deselect()    