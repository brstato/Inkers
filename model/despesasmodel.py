import httpx
from model.config import Config


class despesas_model:
    create_despesa_url:str      = Config.CREATE_DESP_URL
    resume_despesas_url:str     = Config.RESUME_DESP_URL
    list_mes_url:str            = Config.LIST_MES_DESP_URL
    delete_desp_url:str         = Config.DELETE_DESP_URL
    upadte_desp_url:str         = Config.UPDATE_DESP_URL


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


    async def create_despesa(self, descricao: str, status:str, 
                             f_pagamento:str, id_loja:str, 
                             valor:float, qtd:int, date:str, token: str) -> httpx.Response:
        payload = {
            "descricao": descricao,
            "status": status,
            "f_pagamento": f_pagamento,
            "id_loja": id_loja,
            "valor": valor,
            "qtd": qtd,
            "date": date
        }

        return await self._post_request(self.create_despesa_url, payload, token)
    

    async def resume_despesas(self, id_loja:str, token: str) -> httpx.Response:
        payload = {
            "id_loja": id_loja
        }

        return await self._post_request(self.resume_despesas_url, payload, token)
    

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