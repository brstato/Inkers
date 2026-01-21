import flet as ft
from controller.clientcontroller import ClientController
from view.controls.colors import AppColors
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custontextfield import CustomTextField
from view.controls.custonmodalview import CustonModalView
from view.controls.custonlist import CustonList
from view.controls.custoncard import CustonCard


class ClientView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/clients",
            bgcolor=AppColors.BACKGROUND_DARK,
            scroll = ft.ScrollMode.AUTO
        )
        
        self.page    = page

        self.width = self.page.width

        self.id_loja = None
        self.token   = None
        self.r_token = None
        self.id_serv = None

        self.categoria:str = ''
        self.order_maior:bool=False
        self.order_menor:bool=False
        self.ultima_compra:bool=False

        self.row:int = 1
        self.row_to:int = 20
        self.count:int = 0

        self.controller  = ClientController(self.page, self)

        self.calendario = ft.DatePicker(on_change=self.controller.selected_date_calendar)       

        self.edtNome         = CustomTextField(label="Nome do cliente:")    
        self.edtNoneSocial   = CustomTextField(label="Nome social:")
        
        self.edtDtNascimento = CustomTextField(
            label="Aniversário:", 
            regex=r"[0-9/]",
            keyboard_type=ft.KeyboardType.DATETIME,
        )

        self.edtTelefone     = CustomTextField(
            label="Telefone", 
            regex=r"^[0-9]*$",
            keyboard_type=ft.KeyboardType.NUMBER,
        )      


        self.area_data = ft.Stack(
            controls=[
                self.edtDtNascimento, 
                ft.IconButton(
                    icon=ft.Icons.DATE_RANGE,
                    on_click=lambda e: [self.page.open(self.calendario), self.page.update()],
                    icon_color=AppColors.GRAY_LIGHT2,
                    right=10,
                )
            ]
        ) 

        self.edtPesquisa = ft.TextField(
            visible=False,
            hint_text="Pesquisar por nome...",
            on_change=self.filter_clients, # Função que fará a mágica
            border_color=AppColors.ORANGE_DARK,
            height=40,
            content_padding=10,          
        )

        self.view_title = ft.Text(
            value="Clientes",
            style=ft.TextStyle(
                color=AppColors.ORANGE_DARK,
            ),
        )        

        self.open_search_icon = ft.IconButton(
            icon=ft.Icons.SEARCH,
            on_click=self.open_search_bar
        )

        self.close_search_icon = ft.IconButton(
            icon=ft.Icons.CLOSE,
            visible=False,
            on_click=self.close_search_bar
        )        

        self.modalviewCreateClient = CustonModalView(
            self.page,
            height=300,
            callback=self.controller.createClient,
            callback2=self.close_modal_view_create_client,
            controls=[
                self.edtNome,
                self.area_data,
                self.edtTelefone            
            ],            
        )        
        
        self.modalview = CustonModalView(
            self.page,
            height=300,
            callback=self.controller.editClient,
            callback2=self.close_modal_view,
            controls=[
                self.edtNome,
                self.area_data,
                self.edtTelefone    
            ],
        )

        self.selected_card = None
        self.list = CustonList(self.page)
        self.progressRing = CustonProgressRing(self.page.height)  
        
        self.appbar = ft.AppBar(
            actions=[
                self.open_search_icon,
                self.close_search_icon,
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            icon=ft.Icons.PERSON,
                            text='Cliente A',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e, param='a')
                        ),
                        ft.PopupMenuItem(
                            icon=ft.Icons.PERSON,
                            text='Cliente B',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e, param='b')
                        ),                 
                        ft.PopupMenuItem(
                            icon=ft.Icons.PERSON,
                            text='Cliente C',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e, param='c')
                        ),                       
                        ft.PopupMenuItem(
                            icon=ft.Icons.ARROW_UPWARD,
                            text='Maior valor gasto',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e, param='maior')
                        ),      
                        ft.PopupMenuItem(
                            icon=ft.Icons.ARROW_DOWNWARD,
                            text='Menor valor gasto',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e, param='menor')
                        ),                               
                        ft.PopupMenuItem(
                            text='Remover filtro',
                            on_click=lambda e: self.page.run_task(self.controller.listClientData, e)
                        ),                                                                                       
                    ],                       
                ),
            ],
            adaptive=True,
            automatically_imply_leading=False,
            bgcolor=AppColors.GRAY_DARK,
            title=ft.Stack(
                controls=[
                    self.view_title,
                    self.edtPesquisa
                ]
            )
        )
        
        self.bottom_appbar = ft.BottomAppBar(
            height=60,
            bgcolor=AppColors.GRAY_DARK,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=lambda e:self.page.go("/main")
                    ),
                    ft.Container(
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=AppColors.ORANGE_BURNT,
                        on_click=lambda e: self.open_modal_view(e)
                    ),
                ],
            )
        )


        self.controls = [
            ft.Stack(
                controls=[
                    self.list,
                    self.progressRing
                ],
            ),
        ]


    async def prior_navigation(self, e):
        if self.row > 20:
            self.row -= 20
            self.row_to -= 20
            
            await self.__get_client_data_categorizado( 
                                e=e,
                                categoria=self.categoria,
                                row=self.row,
                                row_to=self.row_to,
                                order_maior=self.order_maior,
                                order_menor=self.order_menor,
                                data_ultima_compra=self.ultima_compra)


    async def next_navigation(self, e):
        #if self.row_to < self.count:
        self.row += 20
        self.row_to += 20
        
        await self.__get_client_data_categorizado( 
                            e=e,
                            categoria=self.categoria,
                            row=self.row,
                            row_to=self.row_to,
                            order_maior=self.order_maior,
                            order_menor=self.order_menor,
                            data_ultima_compra=self.ultima_compra)
        


    def did_mount(self):
       self.page.run_task(self._get_client_data)


    def open_modal_view(self, e):
        self.edtNome.value = ''
        self.edtNoneSocial.value = ''
        self.edtDtNascimento.value = ''
        self.edtTelefone.value = ''  
        self.page.open(self.modalviewCreateClient)
        self.page.update()


    def close_modal_view_create_client(self, e):
        self.page.close(self.modalviewCreateClient)
        self.page.update()


    def close_modal_view(self, e):
        self.page.close(self.modalview)
        self.page.update()


    async def _get_client_data(self):
        
        self.id_loja: str = await self.page.client_storage.get_async("id"     )
        self.token:   str = await self.page.client_storage.get_async("token"  )
        self.r_token: str = await self.page.client_storage.get_async("r_token")      

        await self.controller.listClientData('')         




    async def __get_client_data_categorizado(self, e:None, 
        categoria:str='',  
        row:int=1,
        row_to:int=20,                                    
        order_maior:bool=False,
        order_menor:bool=False,
        data_ultima_compra:bool=False
    ):    
        self.categoria = categoria
        self.order_maior = order_maior
        self.order_menor = order_menor
        self.ultima_compra = data_ultima_compra
        self.row = row
        self.row_to = row_to
        
        await self.controller.listClientData(
            _categoria=self.categoria, 
            _row = row,
            _row_to = row_to,
            _order_maior=order_maior,
            _order_menor=order_menor,
            _data_ultima_compra=data_ultima_compra
            )
        

    def open_search_bar(self, e):
        """Mostra o campo de busca e oculta o título."""
        self.view_title.visible = False
        self.edtPesquisa.visible = True
        self.open_search_icon.visible = False
        self.close_search_icon.visible = True
        self.edtPesquisa.focus()
        self.page.update()      


    def close_search_bar(self, e):
        """Oculta o campo de busca, mostra o título e limpa o filtro."""
        self.view_title.visible = True
        self.edtPesquisa.visible = False
        self.open_search_icon.visible = True
        self.close_search_icon.visible = False
        self.edtPesquisa.value = "" # Limpa o texto do campo
        
        # Garante que todos os cards fiquem visíveis novamente
        for card in self.list.controls:
            if isinstance(card, CustonCard):
                card.visible = True
        
        self.page.update()         


    def filter_clients(self, e):
        """Filtra a lista de cards com base no texto digitado."""
        search_term = self.edtPesquisa.value.lower()
        
        # Percorre todos os cards na lista
        for card in self.list.controls:
            if isinstance(card, CustonCard):
                client_name = card.title.lower()
                # Se o termo de busca estiver no nome do cliente, torna o card visível
                if search_term in client_name:
                    card.visible = True
                # Caso contrário, oculta o card
                else:
                    card.visible = False
        
        self.page.update()         