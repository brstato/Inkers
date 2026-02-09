import flet_charts as flc
from view.controls.colors import AppColors
import flet as ft

class BackgroundRod(flc.BarChartRod):
    def __init__(self, y: float, max_y:float, date:str=''):
        super().__init__()
        # Configurações dinâmicas baseadas no estado
        self.from_y = 0
        self.to_y = y
        self.width = 12
        self.color = AppColors.GRAY_LIGHT2
        self.border_radius = ft.border_radius.vertical(top=6, bottom=6)
        
        # Propriedades de fundo (o "trilho" da barra)
        self.bg_to_y = max_y # Altura total do trilho
        self.bg_color = ft.Colors.with_opacity(0.1, AppColors.GRAY_LIGHT2)
        self.date = date


class CustombarChart(flc.BarChart):
    def __init__(self, groups: list[flc.BarChartGroup], on_event=None,  **kwargs):
            super().__init__(
                groups=groups,
                border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                left_axis=flc.ChartAxis(show_labels=False),
                top_axis=flc.ChartAxis(show_labels=False),
                right_axis=flc.ChartAxis(show_labels=False),
                bottom_axis=flc.ChartAxis(
                    show_labels=True,
                    labels=[],
                    label_size=30,
                ),
                horizontal_grid_lines=flc.ChartGridLines(
                    color=ft.Colors.GREY_300, width=1, dash_pattern=[3, 3]
                ),
                interactive=True,
                expand=True,
                tooltip=flc.BarChartTooltip(
                    bgcolor=AppColors.GRAY_DARK,
                    border_radius=4,
                ),   
                on_event=on_event                          
            )

            

            
            

                