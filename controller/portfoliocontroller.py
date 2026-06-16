import flet as ft
import json
import base64
import asyncio
import os
import urllib.parse
import time
from model.portfoliomodel import PortfolioModel
from controller.call_api import ProtectedApiCall
from view.controls.custongaleriaitens import GaleriaItem
from view.controls.colors import AppColors
from view.controls.custondialog import CustonDialog
from utils.image_utils import pick_file_base64

os.environ["FLET_SECRET_KEY"] = os.getenv("FLET_SECRET_KEY")

class PortfolioController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.model = PortfolioModel()
        self.instance = instance


    async def get_galeria(self):
        try:
            response = await ProtectedApiCall(
                page        = self.page,
                instance    = self.instance,
                function    = self.model.get_galeria,
                id_portfolio= self.instance.id_site,
                token       = self.instance.token               
            ).call_api_refresh_token()

            if response.status_code == 200:
                data = response.json()
                data_galeria = data.get('itens', [])
                new_controls = []
                for item in data_galeria:
                    url_limpa = PortfolioModel.clean_url(item['url_foto'])
                    new_controls.append(
                        GaleriaItem(
                            id=item['id_foto'],
                            image=f"https://app.inkers.com.br{url_limpa}",
                            delete_click=self.delete_click
                        )
                    )
                self.instance.update_gallery(new_controls)

        except Exception as ex:
            print(f"Erro em get_galeria: {ex}")


    async def update_portfolio(self):
        self.instance.show_loading(True)

        form_data = self.instance.get_form_data()
        
        # Limpa o dominio e barras extras
        form_data['avatar'] = PortfolioModel.clean_url(form_data['avatar'])
        form_data['foto_bio'] = PortfolioModel.clean_url(form_data['foto_bio'])

        payload = {
            "id_loja"  : form_data['id_loja'],
            "titulo"   : form_data['titulo'],
            "subtitulo": form_data['subtitulo'],
            "avatar"   : form_data['avatar'],
            "foto_bio" : form_data['foto_bio'],
            "bio"      : form_data['bio'],
            "id_site"  : form_data['id_site']
        }

        response = await ProtectedApiCall(
            page    =self.page,
            instance=self.instance,
            function=self.model.update_portfolio,
            payload =payload,
            token   =self.instance.token
        ).call_api_refresh_token()

        if response.status_code == 200:
            self.page.show_dialog(
                CustonDialog(
                    page=self.page,
                    title="Sucesso",
                    content="Portfolio atualizado com sucesso!",
                    actions=[
                        ft.TextButton(
                            content="OK", 
                            on_click=lambda e: self.page.pop_dialog()
                        )
                    ]
                )
            )

            data = response.json()
            self.instance.id_portfolio = data.get('id_portfolio')
            await self.get_data()
        else:
            self.page.show_dialog(
                CustonDialog(
                    page=self.page,
                    title="Erro",
                    content="Erro ao atualizar portfolio!",
                    actions=[
                        ft.TextButton(
                            content="OK", 
                            on_click=lambda e: self.page.pop_dialog()
                        )
                    ]
                )
            )

        self.instance.show_loading(False)


    async def _pick_and_upload_generic(self, upload_function, success_message):
        try:
            base64_string, file_name = await pick_file_base64(self.page)

            if not base64_string or not file_name:
                if file_name:
                    self.page.show_dialog(
                        ft.SnackBar(
                            content=ft.Text("Erro: Falha ao processar imagem local."),
                            bgcolor=ft.Colors.RED,
                            open=True
                        )
                    )
                return

            self.instance.show_loading(True)

            payload = {
                "nome_arquivo": file_name,
                "imagem_base64": base64_string,
                "id_site": self.instance.id_site
            }

            response = await ProtectedApiCall(
                page    =self.page,
                instance=self.instance,
                function=upload_function,
                payload =payload,
                token   =self.instance.token
            ).call_api_refresh_token()

            if response.status_code == 200:
                self.page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text(success_message, color=AppColors.GRAY_LIGHT),
                        bgcolor=AppColors.GRAY_MED3,
                        open=True
                    )
                )
                await self.get_data() # Refresh all data to update image URLs
            else:
                print(f"Erro no upload: {response.content}")     

        except Exception as ex:
            print(f"Erro em upload genérico: {ex}")
        finally:
            self.instance.show_loading(False)


    async def pick_and_upload_avatar(self, e):
        await self._pick_and_upload_generic(
            self.model.upload_avatar, 
            "Avatar atualizado com sucesso!"
        )


    async def pick_and_upload_bio_foto(self, e):
        await self._pick_and_upload_generic(
            self.model.upload_bio_foto, 
            "Foto da bio atualizada com sucesso!"
        )


    async def pick_and_upload_foto(self, e):
        await self._pick_and_upload_generic(
            self.model.upload_foto, 
            "Foto adicionada com sucesso!"
        )


    async def delete_click(self, id):
        try:
            response = await ProtectedApiCall(
                page     = self.page,
                instance = self.instance,
                function = self.model.remove_foto,
                token    = self.instance.token,
                id_foto  = id
            ).call_api_refresh_token()

            if response.status_code == 200:            
                await self.get_galeria()
                            
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
            
            self.instance.show_loading(True)

            response = await ProtectedApiCall(
                page    =self.page,
                instance=self.instance,
                function=self.model.get_portfolio_data,
                token   =self.instance.token,
                id_loja =self.instance.id_loja
            ).call_api_refresh_token()

            if response.status_code == 200:    
                data = response.json()
                
                # Clean paths
                avatar_path = PortfolioModel.clean_url(data.get("avatar", ""))
                bio_foto_path = PortfolioModel.clean_url(data.get("foto_bio", ""))

                # Prepare data for view
                ts = int(time.time())

                view_data = {
                    "id_site": data.get("id_site", ""),
                    "titulo": data.get("titulo", ""),
                    "subtitulo": data.get("subtitulo", ""),
                    "bio": data.get("bio", ""),
                    "avatar": f"https://app.inkers.com.br{avatar_path}" if avatar_path else "",
                    "foto_bio": f"https://app.inkers.com.br{bio_foto_path}" if bio_foto_path else ""
                }
                
                self.instance.fill_form(view_data)

                # Update gallery
                itens = data.get("itens", [])    
                new_controls = []
                for item in itens:
                    url_limpa = PortfolioModel.clean_url(item['url_foto'])
                    new_controls.append(
                        GaleriaItem(
                            image=f"https://app.inkers.com.br{url_limpa}",
                            id   =item["id_foto"],
                            delete_click=self.delete_click
                        )
                    )
                self.instance.update_gallery(new_controls)

            elif response.status_code == 404:
                ...            
        except Exception as e:
            print(f"Erro em get_data: {e}")
        finally:
            self.instance.show_loading(False)



        
