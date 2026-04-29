from model.config import Config
import httpx


class PortfolioModel:
    _client = httpx.AsyncClient(timeout=60.0)

    def __init__(self):
        self.update_portfolio_url   = Config.UPDATE_PORTFOLIO_URL
        self.get_portfolio_data_url = Config.GET_PORTFOLIO_DATA_URL
        self.remove_foto_url        = Config.REMOVE_FOTO_URL
        self.upload_foto_url        = Config.UPLOAD_FOTO_URL
        self.galeria_url            = Config.GET_GALERIA_URL
        self.upload_avatar_url      = Config.UPLOAD_AVATAR_URL
        self.upload_bio_foto_url    = Config.UPLOAD_FOTO_BIO_URL

    @staticmethod
    def clean_url(url: str) -> str:
        if not url:
            return ""
        # Remove domain and redundant slashes
        return url.split(".com.br")[-1].replace("//", "/")

    async def _post_request(self, url: str, payload: dict, token: str) -> httpx.Response:
        header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = await self._client.post(
            url=url,
            json=payload,
            headers=header
        )
        return response  


    async def _get_request(self, url: str, token: str) -> httpx.Response:
        header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = await self._client.request(
            "GET",
            url=url,
            headers=header
        )
        return response  


    async def update_portfolio(self, payload: dict, token: str):
        return await self._post_request(self.update_portfolio_url, payload, token)


    async def get_portfolio_data(self, token:str, id_loja:str):
        return await self._get_request(f"{self.get_portfolio_data_url}/{id_loja}", token)    


    async def remove_foto(self, token:str, id_foto:int):
        return await self._get_request(f"{self.remove_foto_url}/{id_foto}", token)    


    async def upload_foto(self, payload: dict, token: str):
        return await self._post_request(self.upload_foto_url, payload, token)  


    async def upload_avatar(self, payload: dict, token: str):
        return await self._post_request(self.upload_avatar_url, payload, token)


    async def upload_bio_foto(self, payload: dict, token: str):
        return await self._post_request(self.upload_bio_foto_url, payload, token)


    async def get_galeria(self, id_portfolio: int, token:str):
        return await self._get_request(f"{self.galeria_url}/{id_portfolio}", token)