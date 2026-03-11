import flet as ft
from view.controls.colors import AppColors
from utils.formatcurr import formatar_moeda_brasileira
from view.controls.custonmodalview import CustonModalView
from view.controls.custondialog import CustonDialog
from view.controls.custontextfield import CustomTextField
from datetime import datetime

class CustonCardItensAgenda(ft.Card):
    def __init__(
            self, 
            page: ft.Page,
            instance,  
            atendimento:str='',
            hora_inicio:str='',
            hora_fim   :str='',
            name       :str='', 
            event_id   :str='',
            data_atend :str='',
            telefone   :int=0,                        
            id_agenda  :int=0, 
            id_client  :int=0,
            valor      :float=0.00,            
            is_pendente:bool=False,
            delete     :callable=None,
            tap        :callable=None,
            edit       :callable=None,            
        ):
        super().__init__()

        self.edit = edit
        page = page
        self.valor = valor
        self.name:str = name
        self.atendimento=atendimento
        self.hora_inicio=hora_inicio
        self.hora_fim=hora_fim
        # Formata data para dd/mm/yyyy
        try:
            
            if data_atend and 'T' in str(data_atend):
                self.data_atend = datetime.fromisoformat(str(data_atend)).strftime("%d/%m/%Y")
            elif data_atend and '-' in str(data_atend):
                self.data_atend = datetime.strptime(str(data_atend), "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                self.data_atend = data_atend
        except Exception:
            self.data_atend = data_atend
            
        self.id_agenda:int = id_agenda
        self.id = id_agenda
        self.id_client:int = id_client
        self.selected:bool = False
        self.tap = tap
        self.instance = instance
        self.height = 145
        self.telefone = telefone
        self.delete = delete
        self.event_id = event_id
        self.is_pendente = is_pendente
        
        self.border_radius=ft.border_radius.all(10)
        self.elevation=10
        self.padding = ft.padding.all(10)

        self.edtValor = CustomTextField(
            label="Valor de venda:", 
            regex=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )


        
        self.text_quant = ft.Text(
            #text=f'{self.quantidade}',
            style=ft.TextStyle(size=16, color=AppColors.GRAY_LIGHT3,),                                                                                                                       
        )

        self.btn_edit = ft.IconButton(
            icon=ft.Icons.CHECK if is_pendente else ft.Icons.EDIT,
            icon_color=AppColors.ORANGE_BURNT,
            on_click=self.detail_agendamento                                                        
        )    

        self.btn_remove = ft.IconButton(
            icon=ft.Icons.CLOSE if is_pendente else ft.Icons.DELETE,
            icon_color=AppColors.ORANGE_BURNT,    
            on_click=self.delete_agendamento                                                          
        )          

        self.cor_borda = AppColors.ORANGE_DARK if is_pendente else AppColors.GRAY_MED2   

        self.text_name = ft.Text( 
            size=18, 
            offset=ft.Offset(x=0, y=-0.4),                                   
            spans=[
                self.name,                                                                                                                                               
            ],                                
        )
        
        self.telefone_area = ft.Row(
            controls=[
                ft.Text(value=f'tel.: {self.telefone}', color=AppColors.GRAY_LIGHT2, size=14),
                ft.IconButton(icon_color=AppColors.GRAY_LIGHT2, icon=ft.Icons.PHONE, url=f"https://wa.me/{self.telefone}")
            ]
        )

        self.container=ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),
            bgcolor = AppColors.GRAY_DARK,
            border=None,
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.all(10),
            content=ft.Row(
                controls=[
                    # ft.Icon(
                    #     icon=ft.Icons.ACCESS_TIME if is_pendente else ft.Icons.DATE_RANGE, 
                    #     color=AppColors.ORANGE_DARK
                    # ),
                    # ft.VerticalDivider(color=AppColors.ORANGE_DARK),
                    ft.Container(
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text(value=self.name, color=AppColors.ORANGE_DARK, size=16, weight=ft.FontWeight.BOLD,),
                                self.telefone_area,
                                #ft.Text(value=self.atendimento, color=AppColors.GRAY_LIGHT2, size=14),
                                ft.Text(value=f'Data: {self.data_atend}\nInicio: {self.hora_inicio} - Fim: {self.hora_fim}', color=AppColors.GRAY_LIGHT2, size=14),
                            ],
                            #width=self.width / 2,
                        ),
                    ), 
                    ft.Container(expand=True),
                    ft.Container(                            
                        content=ft.Column(                                                
                            controls=[
                                self.btn_edit,
                                self.btn_remove,                                                        
                            ],
                        ), 
                        border=ft.border.all(1, AppColors.GRAY_MED2),
                        border_radius=ft.border_radius.all(5),
                        bgcolor=AppColors.GRAY_DARK,
                        shadow=ft.BoxShadow(color=AppColors.BLACK, blur_radius=5),
                        padding=ft.padding.all(5),
                    ),                     

                ],
            )
        )


        self.content=ft.GestureDetector(                
            content=self.container,
            on_tap=self.on_tap_callback,
        )     


    def on_tap_callback(self, e):
        if self.tap:
            self.tap(self)


    def select(self):
        self.container.border = ft.border.all(1, AppColors.ORANGE_BURNT)
        self.selected = True
        #self.instance.id_prof = self.id
        self.update()


    def deselect(self):
        self.container.border = None
        self.selected = False
        self.update()         


    async def delete_agendamento(self, e):
        self.instance.id = self.id
        self.page.run_task(self.delete, e)


    async def detail_agendamento(self, e):
        self.instance.id = self.id
        self.instance.client_id = self.id_client
        self.page.run_task(self.edit, e)


