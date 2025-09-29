from model.loginmodel import LoginModel
import flet as ft

class ProtectedApiCall:
    def __init__(self, page: ft.Page, instance, function, **kwargs):
        
        self.page = page

        self.instance = instance

        self.function = function

        self.kwargs = kwargs

        self.model = LoginModel()
        

    async def call_api_refresh_token(self):

        response = await self.function(**self.kwargs)

        if response.status_code != 200:
            response = await self.model.refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:
                data = response.json()
                self.instance.token = data["token"]
                self.instance.r_token = data["r_token"]

                await self.page.client_storage.set_async("token", self.instance.token)
                await self.page.client_storage.set_async("r_token", self.instance.r_token)
            
                response = await self.function(**self.kwargs)

            else:
                self.page.go("/")    

        return response            


