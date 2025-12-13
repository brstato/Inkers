import httpx
from model.loginmodel import LoginModel
from model.config import Config


class mainModel:
    get_itens_url:str   = Config.GET_ITENS_URL
    get_clients_url:str = Config.GET_CLIENTS_URL
    abrir_caixa_url:str = Config.ABRIR_CAIXA_URL
    fechar_caixa_url:str= Config.FECHAR_CAIXA_URL
    status_caixa_url:str= Config.STATUS_CAIXA_URL


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
        

    async def status_caixa(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id_loja": id_loja
        }

        return await self._post_request(self.status_caixa_url, payload, token)


    async def fechar_caixa(
        self, 
        id_caixa:int, 
        pr_fechou:int,
        troco:float,
        dinheiro:float,
        pix:float,
        debito:float,
        credito:float, 
        token:str
    ) -> httpx.Response:
        
        payload = {
            "id_caixa": id_caixa,
            "id_func": pr_fechou,
            "troco": troco,
            "dinheiro": dinheiro,
            "pix": pix,
            "debito": debito,
            "credito": credito
        }
        
        return await self._post_request(self.fechar_caixa_url, payload, token)           
        

    async def AbrirCaixa(
        self, 
        id_loja:str,
        data_abertura:str, 
        troco_abertura:float, 
        pr_abriu:int,
        token:str
    ) -> httpx.Response:
        
        payload = {
            "id_loja": id_loja,
            "data_abertura":data_abertura,
            "troco_abertura":troco_abertura,
            "pr_abriu":pr_abriu
        }
        
        return await self._post_request(self.abrir_caixa_url, payload, token)    


    async def GetItensData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id_loja": id,
        }

        return await self._post_request(self.get_itens_url, payload, token)
        

    async def GetClientsData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id_loja": id,
        }
        return await self._post_request(self.get_clients_url, payload, token)      