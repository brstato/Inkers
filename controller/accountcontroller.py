import flet as ft
from model.accountmodel import AccountModel
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
import json


class AccountController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.model = AccountModel()

        self.dialog = None

        self.instance = instance


    async def get_endereco(self):
        self.instance.progressRing.visible = True   
        self.page.update()

        endereco = self.instance.txt_endereco.value

        response = await self.model.get_endereco(endereco)

        if response.status_code == 200:
            data = json.loads(response.content)
            self.instance.txt_endereco.value = data["logradouro"] + ", " + data["numero"] + ", "+ data["bairro"] + ", " + data["cidade"] + " - " + data["uf"] + ", "+ data["cep"]
        elif response.status_code == 400:
            dialog = CustonDialog(
                self.page,
                'Atenção',
                'Informe o CEP.',
                [
                    ft.TextButton(
                        'OK', 
                        on_click=lambda e: 
                        [
                            self.page.pop_dialog(), 
                            self.page.update()
                        ]
                    )
                ]
            )
            self.page.show_dialog(dialog)
        self.instance.progressRing.visible = False
        self.page.update()
        

            


    async def get_slug(self):
        self.instance.progressRing.visible = True
        self.page.update()
        
        # Remove espaços antes de consultar
        self.instance.txt_slug.value = self.instance.txt_slug.value.strip().replace(" ", "")
        self.instance.txt_slug.update()
        
        slug = self.instance.txt_slug.value
        response = await self.model.get_slug(slug)
        if response.status_code == 200:
            data = json.loads(response.content)
            slug_bool:bool = bool(data.get("slug", False))
            id_loja:str    = data.get("id_loja", "")
            if (slug_bool == True and id_loja != self.instance.id) or (slug_bool == True and self.instance.id == ""):
                dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Este apelido já está em uso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(dialog)    

                self.instance.txt_slug.border = ft.InputBorder.OUTLINE 
            else:        
                self.instance.txt_slug.border = ft.InputBorder.UNDERLINE
        self.instance.progressRing.visible = False
        self.page.update()
                

    def clean_slug(self, e):
        # Remove espaços enquanto digita
        if " " in e.control.value:
            e.control.value = e.control.value.replace(" ", "")
        if "." in e.control.value:
            e.control.value = e.control.value.replace(".", "")    
        e.control.update()


    async def get_schedule_json_data(self, view_instance):
        import json
        data = {}
        for item in view_instance.schedule_controls:
            data[item.day_id] = item.get_data()    
        return data     


    async def getAccountData(self, view_instance):
        id:str      = self.page.session.store.get("id"     )
        token:str   = self.page.session.store.get("token"  )
        r_token:str = self.page.session.store.get("r_token")

        if id and r_token:

            view_instance.progressRing.visible = True
            self.page.update()
            
            response = await self.model.getAccountData(id, token)

            if response.status_code == 401:
                response = await LoginModel().refresh_token(r_token, id)
                if response.status_code == 200:
                    self.page.session.store.set("token",   json.loads(response.content)["token"  ])
                    self.page.session.store.set("r_token", json.loads(response.content)["r_token"])

                    token: str = self.page.session.store.get("token")
                    r_token: str = self.page.session.store.get("r_token")

                    response = await self.model.getAccountData(id, token)

                    data = json.loads(response.content)

                    view_instance.txt_username.value = data.get("nome",     "")
                    view_instance.txt_telefone.value = data.get("telefone", "")                
                    view_instance.txt_email.value    = data.get("email",    "")
                    view_instance.txt_slug.value     = data.get("slug",     "")

                    self.page.update()
                else:    
                    self.page.go("/")

            elif response.status_code == 200:
                data = json.loads(response.content)
                view_instance.txt_username.value = data.get("nome",     "")
                view_instance.txt_telefone.value = data.get("telefone", "")
                view_instance.txt_email.value    = data.get("email",    "")
                view_instance.txt_slug.value     = data.get("slug",     "")

                horario_data = data.get("horario", {})

                view_instance.load_schedule_data(horario_data)

            if not view_instance.txt_telefone.value:
                dialog = CustonDialog(
                    self.page,
                    'Atenção!',
                    'Complete seus dados.',
                    [
                        ft.TextButton('Ok', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )    
                self.page.show_dialog(dialog)

            view_instance.progressRing.visible = False
            self.page.update()
        else:
            return    


    async def navigation(self, e):
        if self.dialog is not None:
            self.page.pop_dialog()
            self.dialog = None
            self.page.update() 
            
        if self.instance.r_token:
            await self.page.push_route("/main")
        else:
            await self.page.push_route("/")    


    async def handle_save(self, e, view_instance):

        horario_funcionamento = await self.get_schedule_json_data(view_instance)    

        self.username = view_instance.txt_username.value
        self.telefone = view_instance.txt_telefone.value
        self.email    = view_instance.txt_email.value
        #self.password = view_instance.txt_password.value
        #self.conf_pass= view_instance.txt_conf_password.value
        self.slug     = view_instance.txt_slug.value

        self.id:str      = view_instance.id
        self.token:str   = view_instance.token
        self.r_token = view_instance.r_token

        if not self.r_token:

            if not all([self.username, self.telefone, self.email, self.slug]):#self.password, self.conf_pass, self.slug]):
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor preencha todos os campos.",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update()
                return
        
            if self.password != self.conf_pass:
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="As senhas não coincidem!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update()
                return    
        
            view_instance.progressRing.visible = True
            self.page.update()

            response = await self.model.register(
                self.username,
                self.telefone,
                self.email,
                #self.password,
                self.slug,
                horario_funcionamento
            )    

            view_instance.progressRing.visible = False         
            
            if response.status_code == 200:
                self.dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content="Conta criada com sucesso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update(), self.page.go("/")])
                    ]
                )
                self.page.show_dialog(self.dialog)  
                return

            if response.status_code == 409:
                self.dialog = CustonDialog(
                    self.page,
                    title="Erro!",
                    content=f"Atenção o nome {self.username} ja esta em uso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog) 
                return                  
                    
        else:
            if not all([self.username, self.telefone, self.email]):
                self.dialog = CustonDialog(
                    self.page,
                    title="Atenção",
                    content="Por favor preencha todos os campos.",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update()
                return

            # if self.password != self.conf_pass:
            #     self.dialog = CustonDialog(
            #         self.page,
            #         title="Atenção",
            #         content="As senhas não coincidem!",
            #         actions=[
            #             ft.TextButton('OK', on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
            #         ]
            #     )
            #     self.page.show_dialog(self.dialog)          
            #     self.page.update()
            #     return                

            view_instance.progressRing.visible = True
            self.page.update()

            response = await self.model.updateAccountData(
                self.id,
                self.username,
                self.telefone,
                self.email,
                #self.password,
                self.token, 
                horario_funcionamento,
                self.slug   
            )    

            view_instance.progressRing.visible = False     
            self.page.update()     
            
            if response.status_code == 200:
                self.dialog = CustonDialog(
                    self.page,
                    title="Sucesso",
                    content="Dados atualizados com sucesso!",
                    actions=[
                        ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                    ]
                )
                self.page.show_dialog(self.dialog)          
                self.page.update() 

            elif response.status_code == 401:
                

                response = await LoginModel().refresh_token(r_token, id)
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    self.page.session.store.set("token",   data["token"  ])
                    self.page.session.store.set("r_token", data["r_token"])

                    token:str   = data["token"  ]
                    r_token:str = data["r_token"]

                    view_instance.token  = token
                    view_instance.r_token = r_token

                    response = await self.model.updateAccountData(
                        id,
                        self.username,
                        self.telefone,
                        self.email,
                        #self.password,
                        token,
                        horario_funcionamento,
                        self.slug   
                    )    

                    if response.status_code == 200:
                        self.dialog = CustonDialog(
                            self.page,
                            title="Sucesso",
                            content="Dados atualizados com sucesso!",
                            actions=[
                                ft.TextButton('OK', on_click=lambda e:[self.page.pop_dialog(), self.page.update()])
                            ]
                        )
        self.page.update()