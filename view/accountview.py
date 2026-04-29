import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.accountcontroller import AccountController
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custonschedule import ScheduleItem
import asyncio

class AccountView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/account",
            bgcolor=AppColors.BACKGROUND_DARK,
            padding=ft.padding.all(20),
            scroll=ft.ScrollMode.AUTO
        )

        #page = page

        self.id:str = ""
        self.token:str = ""
        self.r_token:str = ""

        self.progressRing = CustonProgressRing(page.height)             

        self.controller = AccountController(page, self)    

        self.txt_username = CustomTextField("Estudio ou tatuador") 
        self.txt_slug     = CustomTextField(
            label="Apelido", 
            on_blur=self.controller.get_slug,
            on_change=lambda e: self.controller.clean_slug(e)
        )
        self.txt_telefone = CustomTextField("Telefone", regex=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER) 
        self.txt_email    = CustomTextField("e-mail", keyboard_type=ft.KeyboardType.EMAIL) 
        self.txt_password = CustomTextField("Senha", password=True, can_reveal_password=True) 
        self.txt_endereco = CustomTextField(
            "Endereço", 
            max_length=1000,
            #on_blur=self.controller.get_endereco
        )
        self.txt_cep = CustomTextField(
            "CEP", 
            regex=r"^[0-9]*$", 
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self.controller.get_endereco
        )
        self.txt_cidade = CustomTextField("Cidade", readOnly=True)
        self.txt_estado = CustomTextField("Estado", readOnly=True)
        self.txt_bairro = CustomTextField("Bairro", readOnly=True)
        self.txt_numero = CustomTextField("Número")
        self.txt_m_pixel= CustomTextField("Meta Pixel", max_length=50)
        self.txt_g_id   = CustomTextField("Google Analytics ID", max_length=50)
        self.txt_complemento = CustomTextField("Complemento")
        self.txt_instagram = CustomTextField("Instagram")
        self.txt_conf_password = CustomTextField("Confirme a senha", password=True, can_reveal_password=True)

        self.days_map = [
            ("2", "Seg"), ("3", "Ter"), ("4", "Qua"), 
            ("5", "Qui"), ("6", "Sex"), ("7", "Sáb"), ("1", "Dom")
        ]

        self.schedule_controls = []

        for day_id, day_name in self.days_map:
            item = ScheduleItem(day_id, day_name)
            self.schedule_controls.append(item)

        self.schedule_container = ft.Column(
            controls=[
                ft.Text("Horários de Funcionamento", size=16, weight=ft.FontWeight.BOLD, color=AppColors.ORANGE_BURNT),
                ft.Column(controls=self.schedule_controls, spacing=2)
            ]
        )            

        self.btn_save = ft.Row(
            controls=[
                ft.Button(
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, AppColors.GRAY_DARK),
                    ),
                    expand=True,
                    height=45,
                    elevation=5,
                    content='Salvar',
                    bgcolor=AppColors.ORANGE_BURNT,
                    color=AppColors.GRAY_LIGHT,

                    on_click=self._on_click_save
                )
            ],
        )


        self.btn_return = ft.Row(
            controls=[
                ft.OutlinedButton(
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, AppColors.GRAY_DARK),
                        color=AppColors.GRAY_LIGHT,
                    ),
                    expand=True,
                    height=45,
                    content='Voltar',
                    on_click=self.controller.navigation
                )
            ],
        )        

        main_container = ft.Column(
            controls=[
                self.txt_username,
                self.txt_slug,
                self.txt_telefone,
                self.txt_email,
                self.txt_cep,
                self.txt_endereco,
                self.txt_bairro,
                self.txt_cidade,
                self.txt_estado,
                self.txt_numero,
                self.txt_complemento,
                self.txt_instagram,
                self.txt_m_pixel,
                self.txt_g_id,
                ft.Divider(color=AppColors.GRAY_DARK), 
                self.schedule_container,                    
                ft.Container(height=20),
                self.btn_save,
                self.btn_return 
            ],            
            expand=True,
            spacing=15
        )

        self.controls = [
            ft.Stack(
                controls=[
                    main_container,
                    self.progressRing
                ],
                expand=True
            ),
        ]


    def did_mount(self):
       self.page.run_task(self._getAccountData)      


    async def _on_click_save(self, e):
        await self.controller.handle_save(e, self)


    def load_schedule_data(self, json_data):
        if not json_data:
            return   

        for item in self.schedule_controls:
            day_config = json_data.get(item.day_id)
            if day_config:
                item.set_data(day_config)


    async def _getAccountData(self):
        self.id      = self.page.session.store.get("id")
        self.token   = self.page.session.store.get("token")
        self.r_token = self.page.session.store.get("r_token") 

        await self.controller.getAccountData(self)          