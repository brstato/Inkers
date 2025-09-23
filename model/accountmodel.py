import httpx
from model.loginmodel import LoginModel

class AccountModel:
    registerURL:str          = "http://127.0.0.1:8082/api/v1/account/register"
    getaccountdataURL:str    = "http://127.0.0.1:8082/api/v1/account/get_data"
    updateaccountdataURL:str = "http://127.0.0.1:8082/api/v1/account/update"


    async def updateAccountData(self, id:str, nome:str, telefone:str, email:str,
            senha:str, token,) -> httpx.Response:
        
        payload = {
            "nome": nome,
            "telefone": telefone,
            "email": email,
            "senha": senha,
            "id": id,
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


    async def register(self, username:str, telefone: str, email:str, password: str) -> httpx.Response:
        payload = {
            "nome": username,
            "telefone": telefone,
            "email": email,
            "senha":password
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