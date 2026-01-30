import flet as ft
from view.controls.controls_mainview.custoncarditensvenda import CustonCardItensVenda
from utils.formatcurr import formatar_moeda_brasileira
from view.controls.colors import AppColors

class CustonList(ft.ListView):
    def __init__(self, page:ft.Page, instance=None):
        super().__init__(
            controls=[],
            expand=True,
            
        )

        self.instance = instance
        #self.page = page
        self.selected_card = None


    def on_card_selected(self, card_instance: CustonCardItensVenda):
        self.instance.total = 0

        for card in self.controls:
            if isinstance(card, CustonCardItensVenda):
                if card is card_instance:
                    card.select()
                    self.selected_card = card
                else:
                    if not card.quantidade > 0:
                        card.deselect()

        self.page.update()      


    def recalculate_total(self):
        """Recalcula o total de todos os cards e atualiza a MainView."""
        self.instance.total = 0
        for card in self.controls:
            if isinstance(card, CustonCardItensVenda):
                self.instance.total += card.total
        
        # Atualiza o texto do total na MainView
        self.instance.btn_total.content = f'R$ {formatar_moeda_brasileira(self.instance.total)}'

        if self.instance.total > 0:
            self.instance.btn_agenda.visible = False
            self.instance.btn_total.bgcolor = AppColors.ORANGE_BURNT
            self.instance.btn_total.color   = AppColors.GRAY_LIGHT
            self.instance.btn_cancelar.visible = True
        else:
            self.instance.btn_total.bgcolor = AppColors.GRAY_DARK
            self.instance.btn_total.color   = AppColors.GRAY_LIGHT3
            self.instance.btn_cancelar.visible = False

        self.page.update()    


    def cancelar(self):
        self.instance.total = 0  
        for card in self.controls:
            if isinstance(card, CustonCardItensVenda): 
                card.total = 0
                card.valor = card.valor_original  
                card.quantidade = 0
                card.text_valor.text = f'R$ {card.valor_original}'
                card.text_quant.text = 0
                card.text_total.text = 'R$ 0,00'
        
        self.page.update()
        self.recalculate_total()
        self.on_card_selected(CustonCardItensVenda)