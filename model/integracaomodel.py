from model.config import Config
import httpx


class IntegracaoModel:
    def __init__(self):
        self.update_meta_ads_id_url = Config.UPDATE_META_ADS_ID_URL
        self.update_meta_pixel_id_url = Config.UPDATE_META_PIXEL_ID_URL
        self.update_google_analytics_id_url = Config.UPDATE_GOOGLE_ANALYTICS_ID_URL
        self.update_status_campanha_meta_url = Config.UPDATE_STATUS_CAMPANHA_META_URL
    
    async def _post_request(self, url:str, payload:dict, token: str) -> httpx.Response:
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response  
    
    async def atualizar_meta_ads_id(self, meta_ads_id:str, token: str) -> httpx.Response:
        payload = {
            "MetaAdsId": meta_ads_id
        }   

        return await self._post_request(self.update_meta_ads_id_url, payload, token)


    async def atualizar_meta_pixel_id(self, meta_pixel_id:str, token: str) -> httpx.Response:
        payload = {
            "MetaPixelId": meta_pixel_id
        }   

        return await self._post_request(self.update_meta_pixel_id_url, payload, token)        


    async def atualizar_google_analytics_id(self, google_analytics_id:str, token: str) -> httpx.Response:
        payload = {
            "GoogleAnalyticsId": google_analytics_id
        }   

        return await self._post_request(self.update_google_analytics_id_url, payload, token)             


    async def atualizar_status_campanha_meta(self, status_campanha_meta:bool, token: str) -> httpx.Response:
        payload = {
            "StatusCampanhaMeta": status_campanha_meta
        }   

        return await self._post_request(self.update_status_campanha_meta_url, payload, token)                     