import flet as ft
from model.loginmodel import LoginModel

class ProtectedApiCall:
    def __init__(self, page: ft.Page, instance=None, function=None, **kwargs):
        
        self.page = page

        self.instance = instance

        self.function = function

        self.kwargs = kwargs

        self.model = LoginModel()
        

    async def call_api_refresh_token(self):

        response = await self.function(**self.kwargs)

        if response is not None:
            if response.status_code in [401, 403]:
                response = await self.model.refresh_token_raw(self.instance.r_token, self.instance.id_loja)

                if response.status_code == 200:
                    data = response.json()
                    self.instance.token = data["token"]
                    self.instance.r_token = data["r_token"]

                    if 'token' in self.kwargs:
                        self.kwargs['token'] = self.instance.token

                    self.page.session.store.set("token", self.instance.token)
                    self.page.session.store.set("r_token", self.instance.r_token)
                
                    response = await self.function(**self.kwargs)

                else:
                    self.page.go("/")    

        return response            


