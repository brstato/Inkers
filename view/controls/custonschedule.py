import flet as ft
from view.controls.colors import AppColors
    
class ScheduleItem(ft.Container):
    def __init__(self, day_id: str, day_name: str):
        super().__init__()
        self.day_id = day_id # ID que o backend espera (1=Dom, 2=Seg...)
        
        # Checkbox para definir se abre ou não
        self.cb_active = ft.Switch(value=True, on_change=self.toggle_inputs, active_color=AppColors.ORANGE_DARK,)
        
        # Label do dia
        self.lbl_day = ft.Text(day_name, width=50, color=AppColors.GRAY_LIGHT)
        
        # Campos de Hora (Usando TextField simples para facilitar)
        # Dica: Você pode usar máscaras ou validação depois
        # self.txt_start = ft.TextField(
            # value="09:00", 
            # width=80, 
            # height=40, 
            # text_size=14,
            # content_padding=10,
            # bgcolor=AppColors.BACKGROUND_DARK, # Ajuste conforme seu tema
            # color=AppColors.GRAY_LIGHT,
            # border_color=AppColors.GRAY_DARK,
            # disabled=False
        # )
        self.hour_options = [
            ft.dropdown.Option(
                text=f"{i:02d}:00",
                content=ft.Text(f"{i:02d}:00", color=AppColors.GRAY_LIGHT)
            ) for i in range(24)
        ]
        self.txt_start = ft.Dropdown(
            options=self.hour_options,
            value="09:00", # Valor padrão
            width=100,      # Largura compacta
            height=40,     # Altura compacta
            text_size=13,
            content_padding=0,
            bgcolor=AppColors.BACKGROUND_DARK,
            color=AppColors.GRAY_LIGHT,
            border_color=AppColors.GRAY_DARK,
            border_radius=8,
            dense=True,    # Faz o dropdown ser mais compacto internamente
            disabled=False
        )
        
        self.txt_end = ft.Dropdown(
            options=self.hour_options,
            value="09:00", # Valor padrão
            width=100,      # Largura compacta
            height=40,     # Altura compacta
            text_size=13,
            content_padding=0,
            bgcolor=AppColors.BACKGROUND_DARK,
            color=AppColors.GRAY_LIGHT,
            border_color=AppColors.GRAY_DARK,
            border_radius=8,
            dense=True,    # Faz o dropdown ser mais compacto internamente
            disabled=False
        )

        self.content = ft.Row(
            controls=[
                self.cb_active,
                self.lbl_day,
                self.txt_start,
                #ft.Text("-", color=AppColors.GRAY_LIGHT),
                self.txt_end
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def toggle_inputs(self, e):
        # Desabilita os campos de hora se o dia estiver "fechado"
        self.txt_start.disabled = not self.cb_active.value
        self.txt_end.disabled = not self.cb_active.value
        self.txt_start.update()
        self.txt_end.update()

    def get_data(self):
        # Retorna o dicionário no formato que o backend Pascal espera
        return {
            "aberto": self.cb_active.value,
            "inicio": self.txt_start.value,
            "fim": self.txt_end.value
        }

    def set_data(self, data):
        # Preenche os dados vindos do banco
        if data:
            self.cb_active.value = data.get("aberto",   False)
            self.txt_start.value = data.get("inicio", "09:00")
            self.txt_end.value   = data.get("fim",    "18:00")
            self.toggle_inputs(None) # Atualiza visualmente