import flet as ft
from view.controls.custoncardsimples import CustonCardSimples


class CustonList(ft.ListView):
    def __init__(self, page:ft.Page):
        super().__init__(
            controls=[],
            expand=True,
            
        )

#        self.page = page
        self.selected_card = None
        self.height = 500

    def on_card_selected(self, card_instance: CustonCardSimples):
        # Percorre todos os cards na lista de controles
        for card in self.controls:
            if isinstance(card, CustonCardSimples): # Garante que estamos lidando com um CustonCard
                if card is card_instance:
                    # Se for o card que foi clicado, seleciona ele
                    card.select()
                    self.selected_card = card
                else:
                    # Se não for, garante que ele não está selecionado
                    card.deselect()
                