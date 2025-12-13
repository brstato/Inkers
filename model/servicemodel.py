import httpx


class ServiceModel:
    createservicedataURL:str = "http://127.0.0.1:8082/api/v1/service/create"
    deleteservicedataURL:str = "http://127.0.0.1:8082/api/v1/service/delete"
    editservicedataURL:str   = "http://127.0.0.1:8082/api/v1/service/update"
    detailservicedataURL:str = "http://127.0.0.1:8082/api/v1/service/detail"     
    getservicedataURL:str    = "http://127.0.0.1:8082/api/v1/service/list"   



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
