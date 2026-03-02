from model.config import Config
import httpx

class StudioModel:
    def __init__(self):
        self.get_info_studio_url = Config.GET_INFO_STUDIO_URL

    async def _post_request(self, url:str, payload:dict) -> httpx.Response:
        header = {
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response      


    async def get_info_studio(self, slug: str):
        payload = {
            "slug": slug
        }    

        return await self._post_request(self.get_info_studio_url, payload)