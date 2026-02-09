import flet as ft
from datetime import datetime
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.anamnesecontroller import AnamneseController
from view.controls.signaturepad import SignaturePad
from view.controls.custonprogressring import CustonProgressRing
from urllib.parse import unquote


class AnamneseView(ft.View):
    def __init__(self, page:ft.Page, name:str='', tel:str=''):
        super().__init__(
            route="/anamnese", 
            scroll="auto",
            bgcolor=AppColors.BACKGROUND_DARK            
        )

        page = page
        page.title = "Inkers Anamnese"
        #page.padding = 20

        self.name:str = unquote(name)
        self.tel:str = tel
        self.token:str = ''
        self.r_token:str = ''

        self.controller = AnamneseController(page, self)

        self.progress_ring = CustonProgressRing(page.height)

        self.area_title = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Anamnese", color=AppColors.GRAY_LIGHT2, size=18),
                            ft.Container(expand=True),
                        ]
                    ),             
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value=self.name, color=AppColors.GRAY_LIGHT2, size=18),
                            ft.Container(expand=True),
                        ],
                    ),                           
                ]
            ),
        )


        self.nascimento_calendar = ft.DatePicker(
            on_change=self.controller.selected_birth_date,
        )

        self.nome_input = CustomTextField(
            label="Nome Completo",
            keyboard_type=ft.KeyboardType.NAME,
            #key="nome_input",
        )    

        self.telefone_input = CustomTextField(
            label="Telefone",
            keyboard_type=ft.KeyboardType.PHONE,
            #key="telefone_input",
        )             
        
        self.nascimento_input = CustomTextField(
            label="Data de Nascimento (DD/MM/AAAA)",
            keyboard_type=ft.KeyboardType.DATETIME,
            regex=r"[0-9/]",
        )

        self.nascimento_area = ft.Stack(
            controls=[
                self.nascimento_input,
                ft.IconButton(
                    icon_color=AppColors.GRAY_LIGHT2,
                    icon=ft.Icons.DATE_RANGE,
                    on_click = lambda e: [page.show_dialog(self.nascimento_calendar), page.update()],
                    right=5
                )
            ]
        )        

        self.profissao_input = CustomTextField(
            label="Profissão / Ocupação",
            #key="profissao_input",
        )        

        self.instagram_input = CustomTextField(
            label="Instagram (Opcional)", 
            prefix_text="@"
        )

        self.area_dados_pessoais = ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Dados pessoais", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                        ]
                    ),
                    
                    self.nome_input,
                    self.telefone_input,
                    self.nascimento_area,
                    self.instagram_input,
                    self.profissao_input
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
        )

        self.origem_dropdown = ft.Dropdown(
            label="Como conheceu nosso trabalho?",
            #key="origem_dropdown",
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            elevation=5,
            editable=True,
            enable_filter=True,
            expand=True,
            enable_search=True,
            menu_height=210,
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,                         
            options=[
                ft.dropdown.Option("Indicação de Amigo"),
                ft.dropdown.Option("Instagram / TikTok"),
                ft.dropdown.Option("Google / Maps"),
                ft.dropdown.Option("Já sou cliente"),
                ft.dropdown.Option("Passou em frente"),
            ],
            border_radius=10
        )        

        self.area_como_nos_conheceu = ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Como nos conheceu", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                        ],
                        expand=True,
                    ),
                    ft.Row(expand=True, controls=[self.origem_dropdown])
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
            
        )          

        self.tatuagem_switch = ft.Switch(
            label="Gosto de tatuagens", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_estilo_tatuagem            
        )

        self.estilo_tatuagem_dropdown = ft.Dropdown(
            label="Qual seu estilo de tatuagens?",
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            elevation=5,
            editable=True,
            enable_filter=True,
            expand=True,
            enable_search=True,
            menu_height=280,
            text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,                         
            options=[
                ft.dropdown.Option("Preto e cinza"),
                ft.dropdown.Option("Colorido"),
                ft.dropdown.Option("Delicado"),
                ft.dropdown.Option("Tribal"),
                ft.dropdown.Option("Oriental"),
                ft.dropdown.Option("Variado"),
            ],
            border_radius=10,
            visible=False,
        )

        self.piercings_switch = ft.Switch(
            label="Gosto de piercings", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            #on_change=self.controller.selected_medicamento            
        )        

        self.area_estilo = ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Estilo de preferência", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                        ]
                    ),
                    self.tatuagem_switch,
                    self.estilo_tatuagem_dropdown,
                    self.piercings_switch                    
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
        )

        self.experiencia_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(
                    value="primeira", 
                    label="É minha primeira tatuagem / piercing", 
                    active_color=AppColors.ORANGE_DARK,
                    label_style=ft.TextStyle(color=AppColors.GRAY_LIGHT2),
                ),
                ft.Radio(
                    value="algumas", 
                    label="Já tenho algumas", 
                    active_color=AppColors.ORANGE_DARK,
                    label_style=ft.TextStyle(color=AppColors.GRAY_LIGHT2),
                ),
                ft.Radio(
                    value="colecionador", 
                    label="Tenho várias / Colecionador", 
                    active_color=AppColors.ORANGE_DARK,
                    label_style=ft.TextStyle(color=AppColors.GRAY_LIGHT2),
                ),
            ])
        )

        self.area_habitos =  ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Consumo", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                        ]
                    ),
                    
                    self.experiencia_radio
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
        )         

        self.esporte_switch = ft.Switch(
            label="Pratica esportes com frequência?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_problema_esporte
        )

        self.esporte_input = CustomTextField(
            label="Qual?", 
            visible=False,
            #key="esporte_input",
        )  

        self.diabetes_switch = ft.Switch(
            label="Diabético?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
        )     

        self.hipertenso_switch = ft.Switch(
            label="Hipertenso / Cardíaco?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
        ) 

        self.hemofilico_switch = ft.Switch(
            label="Hemofilico?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
        )          

        self.problema_pele_switch = ft.Switch(
            label="Algum problema de pele?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_problema_de_pele
        )          

        self.problema_pele_input = CustomTextField(
            label="Qual?", 
            visible=False,
            #key="problema_pele_input",
        )

        self.gestante_switch = ft.Switch(
            label="Gestante ou amamentando?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
        )               

        self.drogas_switch = ft.Switch(
            label="Alcool ou drogas nas ultimas 24h?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
        )            

        self.doenca_transmissivel_switch = ft.Switch(
            label="Alguma doença transmissivel?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_doenca
        )           

        self.doenca_transmissivel_input = CustomTextField(
            label="Qual?", 
            visible=False,
            #key="doenca_transmissivel_input"
        )
        
        self.alergia_switch = ft.Switch(
            label="Alguma alergia?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_alergia
        ) 

        self.alergias_input = CustomTextField(
            label="Qual?", 
            visible=False,
            #key="alergias_input"
        )    

        self.medicamento_switch = ft.Switch(
            label="Faz uso de algum medicamento?", 
            label_text_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2,
            ),
            active_color=AppColors.ORANGE_DARK,
            on_change=self.controller.selected_medicamento
        )             
        
        self.medicamentos_input = CustomTextField(
            label="Qual?", 
            visible=False,
            #key="medicamentos_input"
        )        

        self.termo_texto_widget = ft.Text(
            value=(
                "Declaro que as informações acima são verdadeiras e assumo a responsabilidade de seguir "
                "as orientações de cuidados pós-procedimento (cicatrização). Estou ciente de que a tatuagem "
                "é um processo definitivo e que depende da visão artistica do profissional."
            ),
            size=12,
            text_align=ft.TextAlign.JUSTIFY,
            color=AppColors.GRAY_LIGHT2,
        )

        self.termo_check = ft.Checkbox(
            label="Li e concordo com o termo de responsabilidade.", 
            fill_color=AppColors.ORANGE_DARK,
            label_style=ft.TextStyle(
                color=AppColors.GRAY_LIGHT2
            ),
            on_change=self.controller.selected_confirm_terms
        )


        self.area_saude =  ft.Container(
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Saude", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                        ]
                    ),
                    self.esporte_switch,
                    self.esporte_input,
                    self.diabetes_switch,
                    self.hipertenso_switch,
                    self.hemofilico_switch,
                    self.problema_pele_switch,
                    self.problema_pele_input,
                    self.gestante_switch,
                    self.drogas_switch,
                    self.doenca_transmissivel_switch,
                    self.doenca_transmissivel_input,
                    self.alergia_switch,
                    self.alergias_input,
                    self.medicamento_switch,
                    self.medicamentos_input,
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
        )  

        self.signature_pad = SignaturePad(self, page, visible=False)

        self.area_signature = ft.Container(
            #key="signature_area",
            border_radius=ft.border_radius.all(10),
            border=ft.border.all(color=AppColors.GRAY_LIGHT4, width=0.1),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,  # Ponto inicial do gradiente
                end=ft.Alignment.BOTTOM_CENTER, # Ponto final do gradiente
                colors=[
                    AppColors.GRAY_DARK,    # Cor inicial
                    AppColors.BACKGROUND_DARK,   # Cor final
                ],                
            ),            
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            ft.Text(value="Assinatura", color=AppColors.GRAY_LIGHT3),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=AppColors.ORANGE_DARK,
                                on_click=lambda e: self.signature_pad.clear()
                            )
                        ]
                    ),
                    self.signature_pad
                ]
            ),
            shadow=ft.BoxShadow(
                color=AppColors.BLACK,
                blur_radius=20,
                offset=ft.Offset(0, 10)
            ),
            height=300,
        )


        self.btn_salvar = ft.Button(
            content="Salvar",
            bgcolor=AppColors.ORANGE_DARK,
            color=AppColors.WHITE,
            width=200,
            height=40,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=self.controller.create_anamnese
        )

        self.area_btn_salvar = ft.Row(
            controls=[
                self.btn_salvar
            ]
        )

        self.dialog_signature = ft.AlertDialog(
            modal=True,
            #title=ft.Text("Assinatura", color=AppColors.GRAY_LIGHT2),
            content=self.area_signature,
            actions=[
                self.area_btn_salvar,
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.Button(
                            color=AppColors.GRAY_LIGHT2,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                bgcolor=AppColors.TRANSPARENT,
                            ),
                            content="Fechar",
                            expand=True,
                            on_click=lambda e: self.controller.cancel_signature(e)
                        )
                    ]
                ),
            ],
        )

        self.list = ft.ListView(
            controls=[
            self.area_title,
            #self.area_dados_pessoais,
            self.nome_input,
            self.telefone_input,
            self.nascimento_area,
            self.instagram_input,
            self.profissao_input,            
            self.area_como_nos_conheceu,
            self.area_estilo,
            self.area_habitos,
            self.area_saude,
            self.termo_texto_widget,
            self.termo_check,
            #self.area_signature,
            #self.area_btn_salvar
            ]
        )

        self.controls = [
            ft.Stack(
                controls=[
                    self.list,
                    self.progress_ring
                ]
            )
        ]


    def did_mount(self):
        pass
        #self.controller.get_data()

