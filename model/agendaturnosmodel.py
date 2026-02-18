from model.config import Config
import httpx

class AgendaTurnosModel:
    def __init__(self):
        self.check_dias_funcionamento_url = Config.CHECK_DIAS_FUNCIONAMENTO

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


    async def check_dias_funcionamento(self, telefone_loja: str, id_profissional: int):
        payload = {
            'telefone_loja': telefone_loja,
            'id_profissional': id_profissional,
        }    
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.check_dias_funcionamento_url,
                json=payload,
            )
            return response    


    async def list_client_tel(self, telefone: str):
        payload = {
            'telefone': telefone,
        }    
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.list_client_tel_url,
                json=payload,
            )
            return response             


