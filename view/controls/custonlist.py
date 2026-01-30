import flet as ft
from view.controls.custoncard import CustonCard
from view.controls.custoncarditensagenda import CustonCardItensAgenda


class CustonList(ft.ListView):
    def __init__(self, page:ft.Page, height=None):
        super().__init__(
            controls=[],
            expand=True,
            
        )

        #self.page = page
        self.selected_card = None
        self._heigt = height


    def did_mount(self):
        if self._heigt != None:
            self.height    

    def on_card_selected(self, card_instance: CustonCard):
        # Percorre todos os cards na lista de controles
        for card in self.controls:
            if isinstance(card, CustonCard) or isinstance(card, CustonCardItensAgenda): # Garante que estamos lidando com um CustonCard
                if card is card_instance:
                    # Se for o card que foi clicado, seleciona ele
                    card.select()
                    self.selected_card = card
                else:
                    # Se não for, garante que ele não está selecionado
                    card.deselect()
                