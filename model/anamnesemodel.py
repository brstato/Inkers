from model.config import Config
from model.dto import AnamneseDTO
import httpx


class AnamneseModel:
    def __init__(self):
        self.create_anamnese_url = Config.CREATE_ANAMENESE_URL


    async def _post_request(self, url: str, payload: dict)    -> httpx.Response:
        header = {
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient(timeout=60.0)as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response   



    async def CreateAnamnese(self, dados: AnamneseDTO):

        return await self._post_request(self.create_anamnese_url, dados.to_dict())