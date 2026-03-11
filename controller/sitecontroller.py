import flet as ft
from model.sitemodel import SiteModel

class SiteController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.model = SiteModel()
        self.instance = instance


    async def get_data(self):    
        try:         

            id_loja = await ft.SharedPreferences().get("id")
            token = await ft.SharedPreferences().get("token")
            
            self.instance.id_loja = id_loja
            self.instance.token = token

            if not self.instance.token or not self.instance.id_loja:    
                await self.page.push_route("/")
                self.page.update()
                return             
            
            self.page.update()
        except Exception as e:
            print(f"Erro em get_data: {e}")


    async def update_site(self):
        payload = {
            "titulo":self.instance.edt_titulo.value,
            "subtitulo":self.instance.edt_subtitulo.value,
            "id_loja":self.instance.id_loja
        }

        return await self.model.update_site(payload, self.instance.token)
