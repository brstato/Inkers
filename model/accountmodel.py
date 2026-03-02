import httpx
from model.loginmodel import LoginModel
from model.config import Config


class AccountModel:
    registerURL:str          = Config.ACCOUNT_REGISTER_URL
    getaccountdataURL:str    = Config.GET_ACCOUNT_DATA_URL
    updateaccountdataURL:str = Config.UPDATE_ACCOUNT_URL
    getslugurl:str           = Config.GET_SLUG_URL

    async def updateAccountData(self, id:str, nome:str, telefone:str, email:str,
            senha:str, token, horarios, slug) -> httpx.Response:
        
        payload = {
            "nome": nome,
            "telefone": telefone,
            "email": email,
            "senha": senha,
            "id": id,
            "horario": horarios,
            "slug": slug
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.updateaccountdataURL, 
                json=payload,
                headers=header
            )

            return response


    async def getAccountData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id": id,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getaccountdataURL, 
                json=payload,
                headers=header
            )

            return response


    async def register(self, 
                        username:str, 
                        telefone: str, 
                        email:str, 
                        password: str, 
                        slug:str,
                        horario
    ) -> httpx.Response:
        payload = {
            "nome": username,
            "telefone": telefone,
            "email": email,
            "senha":password,
            "slug": slug,
            "horario": horario
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.registerURL, 
                json=payload,
                headers=header
            )

            return response


    async def get_slug(self, slug:str) -> httpx.Response:
        payload = {
            "slug": slug,
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getslugurl, 
                json=payload,
                headers=header
            )

            return response