import httpx
from model.config import Config


class despesas_model:
    create_despesa_url:str      = Config.CREATE_DESP_URL
    resume_despesas_url:str     = Config.RESUME_DESP_URL
    list_mes_url:str            = Config.LIST_MES_DESP_URL
    delete_desp_url:str         = Config.DELETE_DESP_URL
    upadte_desp_url:str         = Config.UPDATE_DESP_URL
    baixa_desp_url:str          = Config.BAIXAR_DESP_URL
    list_categorias_url:str     = Config.LIST_CATEGORIAS_URL


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


    async def _get_request(self, url:str, token: str) -> httpx.Response:
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url=url,
                headers=header
            )
            return response        


    async def list_categorias(self, token:str):
        return await self._get_request(self.list_categorias_url, token)
                


    async def baixa_despesa(self, id:int, token: str) -> httpx.Response:
        payload = {
            "id_despesa": id
        }

        return await self._post_request(self.baixa_desp_url, payload, token)



    async def create_despesa(self, payload:dict, token: str) -> httpx.Response:
        return await self._post_request(self.create_despesa_url, payload, token=token)
    

    async def resume_despesas(self, token: str) -> httpx.Response:
        return await self._get_request(self.resume_despesas_url, token)
    

    async def list_despesas_mes(self, id_loja:str, date:str, token: str) -> httpx.Response:
        payload = {
            "id_loja": id_loja,
            "date": date
        }

        return await self._post_request(self.list_mes_url, payload, token)
    

    async def delete_despesas(self, id_despesa:int, token: str) -> httpx.Response:
        payload = {
            "id_despesa": id_despesa
        }

        return await self._post_request(self.delete_desp_url, payload, token)
    

    async def update_despesa(self, id_despesa:int, descricao: str, status:str, 
                             f_pagamento:str, valor:float, date:str, token: str) -> httpx.Response:
        payload = {
            "descricao": descricao,
            "status": status,
            "f_pagamento": f_pagamento,
            "valor": valor,
            "date": date,
            "id_despesa": id_despesa
        }

        return await self._post_request(self.upadte_desp_url, payload, token)