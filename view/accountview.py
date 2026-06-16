import flet as ft
from view.controls.colors import AppColors
from view.controls.custontextfield import CustomTextField
from controller.accountcontroller import AccountController
from view.controls.custonprogressring import CustonProgressRing
from view.controls.custonschedule import ScheduleItem
import asyncio
import json

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
        self.latitude = None
        self.longitude = None
        self.dd_conta_name = None
        self.dd_conta_value = None

        self.progressRing = CustonProgressRing(page.height)             

        self.controller = AccountController(page)    

        self.txt_username = CustomTextField("Estudio ou tatuador") 
        self.txt_slug     = CustomTextField(
            label="Apelido", 
            on_blur=self._get_slug,
            on_change=self._clean_slug
        )
        self.txt_telefone = CustomTextField("Telefone", regex=r"^[0-9]*$", keyboard_type=ft.KeyboardType.NUMBER) 
        self.txt_email    = CustomTextField("e-mail", keyboard_type=ft.KeyboardType.EMAIL) 
        self.txt_password = CustomTextField("Senha", password=True, can_reveal_password=True) 
        self.txt_endereco = CustomTextField(
            "Endereço", 
            max_length=1000,
        )
        self.txt_cep = CustomTextField(
            "CEP", 
            regex=r"^[0-9]*$", 
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._get_endereco
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

        self.area_m_pixel = ft.Stack(
            controls=[
                ft.Row(
                    controls=[self.txt_m_pixel]
                ),
                ft.TextButton(
                    content=ft.Text(
                        "?", 
                        size=16, 
                        weight=ft.FontWeight.BOLD, 
                        color=AppColors.GRAY_LIGHT
                    ), 
                    url="https://business.facebook.com/events_manager2/",
                    right=10,
                )
            ]
        )

        self.area_g_id = ft.Stack(
            controls=[
                ft.Row(
                    controls=[self.txt_g_id]
                ),
                ft.TextButton(
                    content=ft.Text(
                        "?", 
                        size=16, 
                        weight=ft.FontWeight.BOLD, 
                        color=AppColors.GRAY_LIGHT
                    ), 
                    url="https://analytics.google.com/",
                    right=10,
                )
            ]
        )

        self.dd_dropdown_options = []

        self.dd_contas = ft.Dropdown(
            label="Contas Google Ads",
            label_style=ft.TextStyle(
                color=AppColors.WHITE,
            ),
            elevation=5,
            expand=True,
            text_style=ft.TextStyle(
                color=AppColors.WHITE,
            ),
            border=ft.InputBorder.UNDERLINE,
            border_color=AppColors.ORANGE_DARK,
            focused_border_color=AppColors.ORANGE_DARK,
            bgcolor=AppColors.GRAY_DARK,
            options=self.dd_dropdown_options,
            visible=False,
            
        )

        self.area_contas = ft.Row(
            controls=[self.dd_contas]
        )

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
                    on_click=self._on_click_return
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
                self.area_g_id,           
                self.area_m_pixel,
                self.area_contas,
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


    def show_message(self, title, message, on_ok=None):
        from view.controls.custondialog import CustonDialog
        if not on_ok:
            on_ok = lambda e: [self.page.pop_dialog(), self.page.update()]
        dialog = CustonDialog(
            self.page, title, message,
            [ft.TextButton('OK', on_click=on_ok)]
        )
        self.page.show_dialog(dialog)
        self.page.update()


    async def _on_click_return(self, e):
        if self.r_token:
            await self.page.push_route("/main")
        else:
            await self.page.push_route("/")  


    def _clean_slug(self, e):
        if " " in e.control.value:
            e.control.value = e.control.value.replace(" ", "")
        if "." in e.control.value:
            e.control.value = e.control.value.replace(".", "")    
        e.control.update()


    async def _get_slug(self, e):
        self.progressRing.visible = True
        self.page.update()
        self.txt_slug.value = self.txt_slug.value.strip().replace(" ", "")
        self.txt_slug.update()
        
        slug = self.txt_slug.value
        if slug:
            is_valid = await self.controller.check_slug(slug, self.id)
            if not is_valid:
                self.show_message("Atenção", "Este apelido já está em uso!")
                self.txt_slug.border = ft.InputBorder.OUTLINE
            else:
                self.txt_slug.border = ft.InputBorder.UNDERLINE
        self.progressRing.visible = False
        self.page.update()


    async def _get_endereco(self, e):
        cep = self.txt_cep.value
        if not cep: return
        self.progressRing.visible = True
        self.page.update()
        try:
            data = await self.controller.fetch_endereco(cep)
            self.txt_endereco.value = data.get("street", "")
            self.txt_bairro.value   = data.get("neighborhood", "")
            self.txt_cidade.value   = data.get("city", "")
            self.txt_estado.value   = data.get("state", "")
            if "location" in data and "coordinates" in data["location"]:
                coords = data["location"]["coordinates"]
                self.latitude = coords.get("latitude")
                self.longitude = coords.get("longitude")
            self.txt_endereco.readOnly = True
            self.txt_bairro.readOnly = True
            self.txt_cidade.readOnly = True
            self.txt_estado.readOnly = True
            await self.txt_numero.focus()
        except ValueError as ex:
            self.show_message("Atenção!", str(ex))
        except Exception:
            self.txt_endereco.readOnly = False
            self.txt_bairro.readOnly = False
            self.txt_cidade.readOnly = False
            self.txt_estado.readOnly = False
        finally:
            self.progressRing.visible = False
            self.page.update()


    def load_schedule_data(self, json_data):
        if not json_data:
            return   
        for item in self.schedule_controls:
            day_config = json_data.get(item.day_id)
            if day_config:
                item.set_data(day_config)


    async def _getAccountData(self):
        self.id      = self.page.session.store.get("id") or ""
        self.token   = self.page.session.store.get("token") or ""
        self.r_token = self.page.session.store.get("r_token") or ""

        if self.id and self.r_token:
            self.progressRing.visible = True
            self.page.update()
            try:
                data = await self.controller.load_account_data(self.id, self.token, self.r_token)
                if data:
                    self.txt_username.value = data.get("nome", "")
                    self.txt_telefone.value = data.get("telefone", "")
                    self.txt_email.value    = data.get("email", "")
                    self.txt_slug.value     = data.get("slug", "")
                    self.txt_cep.value      = data.get("cep", "")
                    self.txt_endereco.value = data.get("endereco", "")
                    self.txt_bairro.value   = data.get("bairro", "")
                    self.txt_cidade.value   = data.get("cidade", "")
                    self.txt_estado.value   = data.get("estado", "")
                    self.txt_numero.value   = data.get("numero", "")
                    self.txt_complemento.value= data.get("complemento", "")
                    self.txt_instagram.value= data.get("insta", "")
                    self.txt_m_pixel.value  = data.get("meta_pixel", "")
                    self.txt_g_id.value     = data.get("g_tag", "")
                    self.latitude           = data.get("latitude")
                    self.longitude          = data.get("longitude")
                    self.dd_conta_name      = data.get("conta_google_ads_nome", "")
                    self.dd_conta_value     = data.get("conta_google_ads_id", "")
                    self.load_schedule_data(data.get("horario", {}))
                    
                    self.dd_contas.value = self.dd_conta_value
                    self.dd_contas.text  = self.dd_conta_name
                    if self.dd_conta_name: self.dd_contas.visible = True
     
                    try:
                        contas_raw = await ft.SharedPreferences().get("contas_detalhes")
                    except Exception as e:
                        await ft.SharedPreferences().remove("contas_detalhes")
                        contas_raw = None
                        print(f"Erro ao carregar contas_detalhes: {e}")
                    if contas_raw:
                        try:
                            contas = json.loads(contas_raw)
                            if isinstance(contas, list):
                                self.dd_dropdown_options.clear()
                                for conta in contas:
                                    self.dd_dropdown_options.append(
                                        ft.DropdownOption(
                                            key=conta["id"],
                                            text=f"{conta['nome']}",
                                            style=ft.ButtonStyle(
                                                color=AppColors.GRAY_LIGHT2,
                                            )
                                        )
                                    )
                                self.dd_contas.options = self.dd_dropdown_options    
                                self.dd_contas.visible = True
                        except Exception as json_err:
                            print(f"Erro ao decodificar contas_detalhes: {json_err}")                   


                    if not self.txt_telefone.value:
                        self.show_message("Atenção!", "Complete seus dados.")
            except PermissionError:
                self.page.go("/")
            except Exception as e:
                print(f"[ERRO]: {e}")
            finally:
                self.progressRing.visible = False
                self.page.update()


    async def _on_click_save(self, e):
        horarios = {}
        for item in self.schedule_controls:
            horarios[item.day_id] = item.get_data()

        is_update = bool(self.r_token)

        data = {
            "username": self.txt_username.value,
            "telefone": self.txt_telefone.value,
            "email": self.txt_email.value,
            "slug": self.txt_slug.value,
            "cep": self.txt_cep.value,
            "endereco": self.txt_endereco.value,
            "bairro": self.txt_bairro.value,
            "cidade": self.txt_cidade.value,
            "estado": self.txt_estado.value,
            "numero": self.txt_numero.value,
            "complemento": self.txt_complemento.value,
            "instagram": self.txt_instagram.value,
            "m_pixel": self.txt_m_pixel.value,
            "g_tag": self.txt_g_id.value,
            "horarios": horarios,
            "id": self.id,
            "token": self.token,
            "r_token": self.r_token,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "google_ads_id": self.dd_contas.value,
            "google_ads_nome": self.dd_contas.text
        }

        if not is_update:
            if not all([data["username"], data["telefone"], data["email"], data["slug"], data["cep"], data["endereco"], data["bairro"], data["cidade"], data["estado"], data["numero"], data["complemento"]]):
                self.show_message("Atenção", "Por favor preencha todos os campos.")
                return
            if self.txt_password.value != self.txt_conf_password.value:
                self.show_message("Atenção", "As senhas não coincidem!")
                return
        else:
            if not all([data["username"], data["telefone"], data["email"], data["cep"], data["endereco"], data["bairro"], data["cidade"], data["estado"], data["numero"], data["complemento"]]):
                self.show_message("Atenção", "Por favor preencha todos os campos.")
                return

        self.progressRing.visible = True
        self.page.update()
        try:
            result = await self.controller.save_account(data, is_update)
            if self.dd_contas.value:
                self.page.session.store.set("selected_google_ads_id", self.dd_contas.value)
                await ft.SharedPreferences().set("selected_google_ads_id", self.dd_contas.value)
            if not is_update:
                self.show_message("Sucesso", "Conta criada com sucesso!", lambda e: [self.page.pop_dialog(), self.page.update(), self.page.go("/")])
            else:
                self.show_message("Sucesso", "Dados atualizados com sucesso!")
        except ValueError as ex:
            self.show_message("Erro!", str(ex))
        except Exception as ex:
            self.show_message("Erro!", "Ocorreu um erro ao salvar.")
        finally:
            self.progressRing.visible = False
            self.page.update()

      