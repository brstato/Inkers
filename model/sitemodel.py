from model.config import Config
import httpx


class SiteModel:
    def __init__(self):
        self.update_site_url = Config.UPDATE_SITE_URL

    async def _post_request(self, url: str, payload: dict, token: str) -> httpx.Response:
        header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        async with httpx.AsyncClient(timeout=60.0)as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response  


    async def update_site(self, payload: dict, token: str):
        return await self._post_request(self.update_site_url, payload, token)