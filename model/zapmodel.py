import httpx
from model.loginmodel import LoginModel
from model.config import Config


class ZapModel:
    get_connect_zap_url:str     = Config.GET_CONNECT_ZAP
    create_instance_zap_url:str = Config.CREATE_ZAP_URL


    async def _post_request(self, url:str, payload:dict, token: str) -> httpx.Response:
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response


    async def GetConnectionZap(self, zap_instance: str, token: str) -> httpx.Response:
        payload = {
            "instance": zap_instance
        }

        return await self._post_request(self.get_connect_zap_url, payload, token)
    

    async def CreateInstanceZap(self, id_loja:str, zap_number:str, token: str) -> httpx.Response:
        payload = {
            "id_loja":id_loja,
            "number": zap_number
        }

        return await self._post_request(self.create_instance_zap_url, payload, token)
