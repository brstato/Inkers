import flet as ft
from model.studiomodel import StudioModel
import json

class StudioController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.studio_model = StudioModel()
        self.instance = instance

    async def get_info_studio(self, slug: str):
        response = await self.studio_model.get_info_studio(slug)
        if response.status_code == 200:
            data = json.loads(response.content)
            nome = data.get("nome")
            self.instance.telefone = data.get("telefone")
            self.instance.whatsapp_url = f"https://wa.me/55{self.instance.telefone}"
            self.instance.btn_whatsapp.url = self.instance.whatsapp_url
            self.instance.btn_whatsapp_footer.url = self.instance.whatsapp_url
            self.instance.txt_name_studio.value = nome
            self.instance.titulo.value = data.get("titulo")
            self.instance.subtitulo.value = data.get("subtitulo")
            self.page.update()

                        

