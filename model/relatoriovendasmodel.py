import httpx
from model.config import Config


class RelatorioVendasModel:
    resume_vendas_url:str     = Config.RESUME_VENDAS_URL
    list_mes_entradas_url:str = Config.LIST_MES_ENTRADAS_URL
    detail_venda_url:str      = Config.DETAIL_VENDA_URL
    


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


    async def _get_request(self, url:str, token: str, parametro: str = '') -> httpx.Response:
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url=url + parametro,
                headers=header
            )
            return response
    

    async def resume_vendas(self, token: str) -> httpx.Response:
        return await self._get_request(self.resume_vendas_url, token)
    

    async def list_vendas_mes(self, month_number:int, year:int, token: str) -> httpx.Response:
        payload = {
            "mes": month_number,
            "ano": year
        }

        return await self._post_request(self.list_mes_entradas_url, payload, token)


    async def entrada_detalhes(self, id_venda:str, token: str) -> httpx.Response:
        return await self._post_request(self.detail_venda_url, payload={"id_venda": id_venda}, token=token)
    

