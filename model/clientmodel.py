import httpx


class ClientModel:
    createclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/create"
    deleteclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/delete"
    editclientdataURL:str   = "http://127.0.0.1:8082/api/v1/client/update"
    detailclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/detail"     
    getclientdataURL:str    = "http://127.0.0.1:8082/api/v1/client/list"   



    async def getclientData(self, id:str, token:str) -> httpx.Response:
        
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getclientdataURL, 
                json=payload,
                headers=header
            )

            return response      


    async def createclientData(self, nome:str, telefone:str,  
        id_loja:str, aniversario:str, token:str
    ) -> httpx.Response:
        
        payload = {
            "id_loja":id_loja,
            "nome":nome,
            "telefone":telefone,
            "aniversario":aniversario
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.createclientdataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def editclientData(self, id_client:int, nome:str, telefone:str, aniversario:str, 
                            token:str) -> httpx.Response:
        payload = {
            "id":id_client,
            "nome":nome,
            "telefone":telefone,
            "aniversario":aniversario,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.editclientdataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def DetailclientData(self, id_client:str, token:str) -> httpx.Response:
        payload = {
            "id":id_client
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.detailclientdataURL, 
                json=payload,
                headers=header
            )

            return response          
        

    async def deleteclientData(self, id_client:int, token:str) -> httpx.Response:
        payload = {
            "id":id_client
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.deleteclientdataURL, 
                json=payload,
                headers=header
            )

            return response          
