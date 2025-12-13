import flet as ft
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional

class CustonListProfessional(ft.Row):

    def __init__(self, page:ft.Page):
        super().__init__(
            controls=[], 
            expand=True
        )
        self.scroll = ft.ScrollMode.AUTO
        self.page = page
        self.selected_card = None
  

    def on_card_selected(self, card_instance: CustonCardProfessional):
        # Percorre todos os cards na lista de controles
        for card in self.controls:
            if isinstance(card, CustonCardProfessional): # Garante que estamos lidando com um CustonCard
                if card is card_instance:
                    # Se for o card que foi clicado, seleciona ele
                    card.select()
                    self.selected_card = card
                else:
                    # Se não for, garante que ele não está selecionado
                    card.deselect()


    def cancelar(self):
        for card in self.controls:
            if isinstance(card, CustonCardProfessional):
                card.deselect()
        self.page.update()                        
        
        