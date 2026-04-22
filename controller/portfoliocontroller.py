import flet as ft
import json
import base64
import asyncio
import os
from model.portfoliomodel import PortfolioModel
from controller.call_api import ProtectedApiCall
from view.controls.custongaleriaitens import GaleriaItem
from view.controls.colors import AppColors

class PortfolioController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.model = PortfolioModel()
        self.instance = instance


    async def pick_and_upload_foto(self, e):
        # Abre a caixa de diálogo e aguarda o usuário selecionar
        files = await ft.FilePicker().pick_files(
            allow_multiple=False, 
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg", "webp"]    
        )

        # Se o usuário fechar a janela sem escolher nada
        if not files:
            return

        self.instance.loading.visible = True
        self.page.update()

        try:
            # Em apps web Flet recentes, '.bytes' não está disponível. 
            # Devemos fazer o upload interno para obter o arquivo base64.
            file = files[0]
            upload_url = self.page.get_upload_url(file.name, 60)
            
            upload_done = asyncio.Event()

            async def on_upload_local(e: ft.FilePickerUploadEvent):
                if e.file_name == file.name and getattr(e, 'progress', 0) == 1.0:
                    upload_done.set()
                elif getattr(e, 'error', None):
                    print("Upload local error:", e.error)
                    upload_done.set()

            self.instance.file_picker.on_upload = on_upload_local
            
            await self.instance.file_picker.upload([
                ft.FilePickerUploadFile(file.name, upload_url=upload_url)
            ])
            await upload_done.wait()
            
            # Carrega-o da pasta uploads
            file_path = os.path.join("uploads", file.name)
            if not os.path.exists(file_path):
                print("Arquivo não salvo pelo Flet.")
                self.instance.loading.visible = False
                self.page.update()
                return

            with open(file_path, "rb") as f:
                base64_string = base64.b64encode(f.read()).decode('utf-8')
            os.remove(file_path)

            # O id_loja será pego via JWT no servidor
            payload = {
                "nome_arquivo": file.name,
                "imagem_base64": base64_string
            }

            response = await ProtectedApiCall(
                page    =self.page,
                instance=self.instance,
                function=self.model.upload_foto,
                payload =payload,
                token   =self.instance.token
            ).call_api_refresh_token()

            if response.status_code == 200:
                await self.get_data() 
            else:
                print(f"Erro no upload: {response.content}")

        except Exception as ex:
            print(f"Erro em pick_and_upload_foto: {ex}")
        finally:
            self.instance.loading.visible = False
            self.page.update()


    async def delete_click(self, id):
        try:
            response = await ProtectedApiCall(
                page = self.page,
                instance = self.instance,
                function = self.model.remove_foto,
                token = self.instance.token,
                id_foto = id
            ).call_api_refresh_token()

            if response.status_code == 200:            
                for control in self.instance.galeria.controls:
                    if isinstance(control, GaleriaItem):
                        if control.id == id:
                            self.instance.galeria.controls.remove(control)
                            self.page.update()
                            break
                            
        except Exception as e:    
            print(f"Erro em delete_click: {e}")


    async def get_data(self):    
        try:                 
            token:   str = self.page.session.store.get("token"  )
            r_token: str = self.page.session.store.get("r_token")
            id_loja: str = self.page.session.store.get("id"     )
            slug:    str = self.page.session.store.get("slug"   )
            
            self.instance.id_loja = id_loja
            self.instance.token   = token
            self.instance.r_token = r_token
            self.instance.slug    = slug

            if not self.instance.token or not self.instance.id_loja:    
                await self.page.push_route("/")
                self.page.update()
                return             
            
            self.instance.loading.visible = True


            response = await ProtectedApiCall(
                page    =self.page,
                instance=self.instance,
                function=self.model.get_portfolio_data,
                token   =self.instance.token,
                id_loja =self.instance.id_loja
            ).call_api_refresh_token()

            try:
                data = json.loads(response.content)
            except json.JSONDecodeError:
                print(f"Failed to decode JSON. Status: {response.status_code}, Content: {response.content}")
                self.instance.loading.visible = False
                self.page.update()
                return

            titulo    = data.get("titulo",    "")
            subtitulo = data.get("subtitulo", "")
            bio       = data.get("bio",       "")
            avatar    = f"https://{self.instance.slug}.inkers.com.br/{data.get("avatar",    "")}"
            bio_foto  = f"https://{self.instance.slug}.inkers.com.br/{data.get("foto_bio",  "")}"
            itens     = data.get("itens",     [])    

            self.instance.edt_titulo.value    = titulo
            self.instance.edt_subtitulo.value = subtitulo
            self.instance.edt_bio.value       = bio
            self.instance.img_avatar.src      = avatar
            self.instance.bio_image.src       = bio_foto

            for item in itens:
                self.instance.galeria.controls.append(
                    GaleriaItem(
                        image=f"https://{self.instance.slug}.inkers.com.br/{item["url_foto"]}",
                        id   =item["id_foto"],
                        delete_click=self.delete_click
                    )
                )
            
            self.instance.loading.visible = False

            self.page.update()
        except Exception as e:
            print(f"Erro em get_data: {e}")


    async def update_portfolio(self):
        payload = {
            "titulo":self.instance.edt_titulo.value,
            "subtitulo":self.instance.edt_subtitulo.value,
            "id_loja":self.instance.id_loja
        }

        return await self.model.update_portfolio(payload, self.instance.token)
