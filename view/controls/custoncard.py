import flet as ft
from view.controls.colors import AppColors
from view.controls.custondialog import CustonDialog


class CustonCard(ft.Card):
    def __init__(self, page:ft.Page, width, id:int, icon:None, callback:None, callback2:None, tap:callable=None,  
        title:str = '', desc:str = '', detail:str = '', sub_desc = '', sub_detail = '', categoria = '',
        telefone:str='', visible_menu:bool=False, visible_btn: bool = True, height:int=140):

        super().__init__()
        self.telefone = telefone
        self.visible_menu = visible_menu
        self.title = title
        self.categoria = categoria
        self.sub_desc = sub_desc
        self.sub_detail = sub_detail
        self.tap = tap
        self.callback = callback
        self.callback2 = callback2
        self.shadow_color=AppColors.BLACK
        self.elevation=5
#        self.page = page
        self.id = id
        self.selected = False
        self.visible_btn = visible_btn
        self.height = height
        
        
        
        self.menu = ft.MenuBar(
            visible=False,
            controls=[
                ft.SubmenuButton(
                    content=ft.TextButton(
                        icon=ft.Icons.SMS,
                        content='Chamar',
                        url=f'https://wa.me/55{self.telefone}'
                    ),
                ),
            ],
        )        
        
        
        self.btn_delete = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=AppColors.ORANGE_BURNT,    
            on_click=lambda e: self.on_delete_click(e)                                                          
        )


        self.btn_edit = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color=AppColors.ORANGE_BURNT,
            on_click=lambda e: page.run_task(self.open_modal_view_detail)
        )

        area_botoes = ft.Container(       
            visible=self.visible_btn,                     
            content=ft.Column(                                                
                controls=[
                    self.btn_delete,
                    self.btn_edit,                                                        
                ],
            ), 
            border=ft.border.all(1, AppColors.GRAY_MED2),
            border_radius=ft.border_radius.all(5),
            bgcolor=AppColors.GRAY_DARK,
            shadow=ft.BoxShadow(color=AppColors.BLACK, blur_radius=5),
            padding=ft.padding.all(5),
        )        
        
        
        self.container = ft.Container(     
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),                   
            border=None,
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(10),
            bgcolor=AppColors.GRAY_DARK,
            height=130,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon=icon,
                        color=AppColors.ORANGE_BURNT,
                        size=20,
                    ),
                    ft.VerticalDivider(
                        color=AppColors.ORANGE_BURNT,
                        width=1,
                        visible=True,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                        spans=[
                                            ft.TextSpan(
                                                text=self.categoria, 
                                                style=ft.TextStyle(color=AppColors.ORANGE_DARK)),
                                            ft.TextSpan(
                                                text=' | ', 
                                                style=ft.TextStyle(color=AppColors.GRAY_MED)),
                                            ft.TextSpan(
                                                text=self.title, 
                                                style=ft.TextStyle(color=AppColors.ORANGE_DARK)),
                                        ],

                                    size=20,
                                    offset=ft.Offset(x=0, y=-0.2),
                                    col=4,
                                    max_lines=1,
                                ),
                                ft.Text(                                                    
                                    value=desc,
                                    color=AppColors.GRAY_LIGHT,
                                    size=15,
                                    offset=ft.Offset(x=0, y=-0.5),
                                    col=4,
                                    max_lines=1,
                                ),       
                                ft.Text(                                                    
                                    value=self.sub_desc,
                                    color=AppColors.GRAY_LIGHT,
                                    size=15,
                                    offset=ft.Offset(x=0, y=-1),
                                    col=4,
                                    max_lines=1,
                                ),                                    
                                ft.Text(                                                    
                                    value=detail,
                                    color=AppColors.GRAY_LIGHT,
                                    size=15,
                                    offset=ft.Offset(x=0, y=-1.5),
                                    max_lines=1,
                                ),    
                                ft.Text(                                                    
                                    value=self.sub_detail,
                                    color=AppColors.GRAY_LIGHT,
                                    size=15,
                                    offset=ft.Offset(x=0, y=-2),
                                    max_lines=1,
                                ),                                                                                                                                                                 
                            ],                            
                        ),
                        
                        width=width / 1.7,
                        height=self.height,
                    ),
                    ft.Container(expand=True),
                    area_botoes,                          
                ]
            ),
        )  

        
        self.content = ft.GestureDetector(
            content=ft.Stack(
                controls=[
                    self.container,
                    self.menu
                ],
            ),
            on_tap=self.on_tap_callback,
            on_double_tap=lambda e:self.open_menu(e)
        )


    def open_menu(self, e):
        self.menu.visible=self.visible_menu
        self.update()        

           
    def on_tap_callback(self, e):
        if self.tap:
            self.tap(self)


    def select(self):
        self.container.border = ft.border.all(2, AppColors.ORANGE_BURNT)
        self.selected = True
        self.update()


    def deselect(self):
        self.container.border = None
        self.selected = False
        self.menu.visible=False
        self.update()        


    def on_delete_click(self, e):
        dialog = CustonDialog(
            self.page,
            title="Confirmação",
            content="Deseja realmente excluir este registro?",
            actions=[
                ft.TextButton(
                    "Cancelar", 
                    on_click=lambda e: [
                        self.page.pop_dialog(), 
                        self.page.update()
                        ]
                    ),
                ft.TextButton(
                    "Excluir",
                    on_click=lambda e: self.page.run_task(self.confirm_delete, dialog)                    
                )
            ]
        ) 
        self.page.show_dialog(dialog)
        self.page.update()   


    async def open_modal_view_detail(self):
        await self.callback2(self.id)


    async def confirm_delete(self, dialog):
        self.page.pop_dialog()
        self.page.update()
        await self.callback(self.id)
   
        