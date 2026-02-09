import flet as ft
from view.controls.colors import AppColors
from utils.formatcurr import formatar_moeda_brasileira
from view.controls.custonmodalview import CustonModalView
from view.controls.custondialog import CustonDialog
from view.controls.custontextfield import CustomTextField

class CustonCardItensVenda(ft.Card):
    def __init__(
            self, 
            width,
            page: ft.Page,
            instance, 
            icon:None, 
            valor:float=0.00,
            name:str='', 
            id=None, 
            estoque:int=0, 
            ident_serv:int=0,
            inf_valor:bool=False,
            comissionado:bool=False,
            comissao:int=0,
            valor_visible:bool=True,
            tap:callable=None,
            on_change:callable=None
        ):
        super().__init__()

        self.ident_serv = ident_serv
        self.on_change = on_change
        self.width = width
#        self.page = page
        self.valor = valor
        self.valor_original = valor
        self.estoque = estoque
        self.name:str = name
        self.id:int = id
        self.selected:bool = False
        self.tap = tap
        self.instance = instance
        self.icon = icon
        self.quantidade:int=0
        self.total:float=0
        self.height = 135
        self.inf_valor = inf_valor
        self.comissionado = comissionado
        self.comissao = comissao
        self.valor_visible = valor_visible
        
        self.border_radius=ft.BorderRadius.all(10)
        self.elevation=10
        self.padding = ft.Padding.all(10)

        self.edtValVenda = CustomTextField(
            label="Valor de venda:", 
            chars=r"^[0-9,]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.moda_view = CustonModalView(
            height=150,
            callback=self.handler_inf_valor,
            callback2=lambda e: self.Cancel_inf_valor(e),
            page=page, 
            controls=[
                self.edtValVenda
            ]
        )

        self.text_total = ft.TextSpan(
            text=f'R$ {formatar_moeda_brasileira(self.total)}',
            style=ft.TextStyle(size=16, color=AppColors.GRAY_LIGHT3, weight=ft.FontWeight.BOLD),                                                                                                                       
        )

        self.text_valor = ft.TextSpan(
            text=f'R$ {formatar_moeda_brasileira(self.valor)}',
            style=ft.TextStyle(size=16, color=AppColors.GRAY_LIGHT3,),                                                                                                                       
        )
        
        self.text_quant = ft.TextSpan(
            text=f'{self.quantidade}',
            style=ft.TextStyle(size=16, color=AppColors.GRAY_LIGHT3,),                                                                                                                       
        )

        self.btn_add = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=AppColors.ORANGE_BURNT,    
            on_click=lambda e: self.add_quant(e)                                                          
        )    

        self.btn_remove = ft.IconButton(
            icon=ft.Icons.REMOVE,
            icon_color=AppColors.ORANGE_BURNT,    
            on_click=lambda e: self.remove_quant(e)                                                          
        )             

        self.btn_cancel = ft.Button(
            content='Cancelar',
            color=AppColors.GRAY_LIGHT,
            bgcolor=AppColors.BACKGROUND_DARK,
            on_click=lambda e: self.cancel_valor(e)
        )

        self.btn_confirm = ft.Button(
            content='Confirmar',
            color=AppColors.GRAY_LIGHT,
            bgcolor=AppColors.BACKGROUND_DARK,
            on_click=lambda e: self.confirm_valor(e)
        )        

        self.dialog = CustonDialog(
            page, 
            'Atenção', 
            'O valor informado é menor que o valor original, deseja continuar?',
            actions=[
                self.btn_cancel,
                self.btn_confirm
            ]
        )

        self.text_estoque = ft.Text(
            value=f'Estoque: {self.estoque}', 
            color=AppColors.GRAY_LIGHT, size=14
        )

        self.text_valor = ft.Text( 
            visible=self.valor_visible,
            size=18, 
            offset=ft.Offset(x=0, y=-0.4),                                   
            spans=[
                self.text_valor, 
                ft.TextSpan(
                    text=f' X ',
                    style=ft.TextStyle(size=12, color=AppColors.GRAY_LIGHT3,),                                                                                                                       
                ),    
                self.text_quant,  
                ft.TextSpan(
                    text=f' = ',
                    style=ft.TextStyle(size=12, color=AppColors.GRAY_LIGHT3,),                                                                                                                       
                ),       
                self.text_total,                                                                                                                                     
            ],                                
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
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(10),
            content=ft.Row(
                controls=[
                    #ft.Icon(name=self.icon, color=AppColors.ORANGE_DARK),
                    #ft.VerticalDivider(color=AppColors.ORANGE_DARK),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(value=self.name, color=AppColors.ORANGE_DARK, size=16, weight=ft.FontWeight.BOLD,),
                                self.text_valor,
                                self.text_estoque,
                            ],
                            width=page.width / 2,
                        ),
                    ), 
                    ft.Container(                            
                        content=ft.Column(                                                
                            controls=[
                                self.btn_add,
                                self.btn_remove,                                                        
                            ],
                        ), 
                        border=ft.Border.all(1, AppColors.GRAY_MED2),
                        border_radius=ft.BorderRadius.all(5),
                        bgcolor=AppColors.GRAY_DARK,
                        shadow=ft.BoxShadow(color=AppColors.BLACK, blur_radius=5),
                        padding=ft.Padding.all(5),
                    ),                     

                ],
            )
        )

        self.content=ft.GestureDetector(                
            content=self.container,
            on_tap=self.on_tap_callback,
        )     


    async def handler_inf_valor(self, e):
        await self.Confirm_inf_valor(e)


    def on_tap_callback(self, e):
        if self.tap:
            self.tap(self)


    def select(self):
        self.container.border = ft.Border.all(1, AppColors.ORANGE_BURNT)
        self.selected = True
        self.update()


    def deselect(self):
        self.container.border = None
        self.selected = False
        self.update()         


    def did_mount(self):
        if self.ident_serv == 1:
            self.text_estoque.visible = False

        self.total = self.valor * self.quantidade
        self.text_total.text = f'R$ {self.total}'
        self.page.update()


    def add_quant(self, e):
        if self.instance.status_caixa == 'F':
            self.dialog_alert = CustonDialog(
                page=self.page,
                title="Atenção",
                content="O caixa esta fechado, por favor abra o caixa para continuar!",
                actions=[
                    ft.TextButton(
                        text="OK",
                        on_click=lambda e:[
                            self.page.pop_dialog(),
                            self.page.update()
                        ]
                    )
                ]
            )
            self.page.show_dialog(self.dialog_alert)
            self.page.update()
            return

        if self.inf_valor == 'True' and self.quantidade == 0:
            self.page.show_dialog(self.moda_view)

        self.container.border = ft.Border.all(1, AppColors.ORANGE_BURNT)
        self.quantidade = self.quantidade + 1 
        self.text_quant.text = self.quantidade
        self.total = self.valor * self.quantidade
        self.text_total.text = f'R$ {formatar_moeda_brasileira(self.total)}'

        self.instance.btn_total.visible = True
        self.instance.btn_cancelar.visible = True
        self.instance.btn_fechar_caixa.visible = False
            
        self.on_change()    

        self.page.update()


    def remove_quant(self, e):  
        if self.quantidade > 0:
            self.quantidade = self.quantidade - 1 
            self.text_quant.text = self.quantidade
            self.total = self.valor * self.quantidade
            self.text_total.text = f'R$ {formatar_moeda_brasileira(self.total)}'

        if self.quantidade == 0:
            self.container.border = None  
            self.text_quant.text = self.quantidade
            self.valor = self.valor_original        
            self.text_valor.text=f'R$ {formatar_moeda_brasileira(self.valor)}'
            self.instance.btn_total.visible = False
            self.instance.btn_cancelar.visible = False
            self.instance.btn_fechar_caixa.visible = True

        self.on_change()          

        self.page.update()      


    def Cancel_inf_valor(self, e):
        self.page.pop_dialog()        
        self.page.update()  


    async def Confirm_inf_valor(self, e):
        if not self.edtValVenda.value == '':
            self.valor = float(self.edtValVenda.value.replace(',', '.'))

            # 1. FECHE O DIÁLOGO ATUAL PRIMEIRO
            self.page.pop_dialog()
            self.page.update()

            # 2. AGORA VERIFIQUE SE PRECISA ABRIR O PRÓXIMO
            if self.valor < self.valor_original:
                self.page.show_dialog(self.dialog)
                # self.page.update() # O show_dialog geralmente já trigga a abertura, mas se precisar forçar, use aqui

            self.total = self.valor * self.quantidade
            self.text_valor.text = f'R$ {formatar_moeda_brasileira(self.valor)}'        
            self.text_total.text = f'R$ {formatar_moeda_brasileira(self.total)}'        
            
            # self.page.pop_dialog()  <-- REMOVA ESTA LINHA (já fechamos lá em cima)
            
            self.on_change()     
            self.page.update()       


    def confirm_valor(self, e):
        self.edtValVenda.value = ''
        self.page.pop_dialog()
        self.page.update()


    def cancel_valor(self, e):
        self.edtValVenda.value = ''
        self.valor = self.valor_original              
        self.total = self.valor * self.quantidade
        self.text_valor.text = f'R$ {formatar_moeda_brasileira(self.valor)}'        
        self.text_total.text = f'R$ {formatar_moeda_brasileira(self.total)}'        
        self.page.pop_dialog()   
        self.on_change()     
        self.page.update()            