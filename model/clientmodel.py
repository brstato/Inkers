import httpx


class ClientModel:
    createclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/create"
    deleteclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/delete"
    editclientdataURL:str   = "http://127.0.0.1:8082/api/v1/client/update"
    detailclientdataURL:str = "http://127.0.0.1:8082/api/v1/client/detail"     
    getclientdataURL:str    = "http://127.0.0.1:8082/api/v1/client/list"   



    async def getclientData(self, id:str, token:str, categoria:str='', row:int=0, row_to:int=0, 
                        order_maior:bool=False, order_menor:bool=False, ultima_compra:bool=False
    ) -> httpx.Response:
        
        payload = {
            "id":id,
            "categoria":categoria,
            "order_maior":order_maior,
            "order_menor":order_menor,
            "data_ultima_compra":ultima_compra,
            "row":row,
            "row_to":row_to
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


    async def editclientData(self, id:int, nome:str, telefone:str, aniversario:str, 
                            token:str) -> httpx.Response:
        payload = {
            "id":id,
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


    async def DetailclientData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
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
        

    async def deleteclientData(self, id:int, token:str) -> httpx.Response:
        payload = {
            "id":id
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
