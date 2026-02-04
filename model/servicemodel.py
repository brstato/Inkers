import httpx
from model.config import Config


class ServiceModel:
    createservicedataURL:str = Config.CREATE_SERVICE_URL
    deleteservicedataURL:str = Config.DELETE_SERVICE_URL
    editservicedataURL:str   = Config.UPDATE_SERVICE_URL
    detailservicedataURL:str = Config.DETAIL_SERVICE_URL     
    getservicedataURL:str    = Config.LIST_SERVICE_URL   



    async def getServiceData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getservicedataURL, 
                json=payload,
                headers=header
            )

            return response      


    async def createServiceData(self, nome:str, inf_valor:str,  
                                id_loja:str, comissionado:str, valor_custo:float, valor_venda:float,
                                token:str) -> httpx.Response:
        payload = {
            "id_loja":id_loja,
            "nome":nome,
            "inf_valor":inf_valor,
            "valor_custo":valor_custo,
            "valor_venda":valor_venda,
            "comissionado":comissionado
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.createservicedataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def editServiceData(self, id:int, nome:str, inf_valor:str, comissionado:str, 
                             valor_custo:float, valor_venda:float,
                             token:str) -> httpx.Response:
        payload = {
            "id":id,
            "nome":nome,
            "inf_valor":inf_valor,
            "valor_custo":valor_custo,
            "valor_venda":valor_venda,
            "comissionado":comissionado
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.editservicedataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def DetailServiceData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.detailservicedataURL, 
                json=payload,
                headers=header
            )

            return response    


    async def getServiceData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getservicedataURL, 
                json=payload,
                headers=header
            )

            return response        
        

    async def deleteServiceData(self, id:int, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.deleteservicedataURL, 
                json=payload,
                headers=header
            )

            return response          
