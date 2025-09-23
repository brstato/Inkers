import httpx
from model.loginmodel import LoginModel


class mainModel:
    getitensURL:str   = 'http://127.0.0.1:8082/api/v1/caixa/itens/list'
    getclientsURL:str = 'http://127.0.0.1:8082/api/v1/caixa/client/list'


    async def GetItensData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id_loja": id,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getitensURL, 
                json=payload,
                headers=header
            )

            return response
        

    async def GetClientsData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id_loja": id,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getclientsURL, 
                json=payload,
                headers=header
            )

            return response        