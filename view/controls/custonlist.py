import flet as ft
from view.controls.custoncard import CustonCard
from view.controls.custoncarditensagenda import CustonCardItensAgenda


class CustonList(ft.ListView):
    def __init__(self, page:ft.Page, height=None, instance=None):
        super().__init__(
            controls=[],
            expand=True,
            
        )

        #self.page = page
        self.selected_card = None
        self._heigt = height
        self.instance = instance


    def did_mount(self):
        if self._heigt != None:
            self.height    

    def on_card_selected(self, card_instance: CustonCard):
        if self.selected_card == card_instance:
            self.selected_card.deselect()
            self.selected_card = None
            if self.instance:
                self.instance.id = 0
                if hasattr(self.instance, 'update_actions_visibility'):
                    self.instance.update_actions_visibility()
            return

        if self.selected_card:
            self.selected_card.deselect()

        card_instance.select()
        self.selected_card = card_instance
        if self.instance:
            self.instance.id = card_instance.id
            if hasattr(self.instance, 'update_actions_visibility'):
                self.instance.update_actions_visibility()
                