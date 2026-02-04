import httpx
from model.config import Config


class ClientModel:
    createclientdataURL:str   = Config.CREATE_CLIENT_URL
    deleteclientdataURL:str   = Config.DELETE_CLIENT_URL
    editclientdataURL:str     = Config.UPDATE_CLIENT_URL
    detailclientdataURL:str   = Config.DETAIL_CLIENT_URL     
    getclientdataURL:str      = Config.LIST_CLIENT_URL   
    getclientdataAurl:str     = Config.LIST_CLIENT_A_URL
    getclientdataBurl:str     = Config.LIST_CLIENT_B_URL
    getclientdataCurl:str     = Config.LIST_CLIENT_C_URL    
    getclientdataMaiorurl:str = Config.LIST_CLIENT_MAIOR_URL 
    getclientdataMenorurl:str = Config.LIST_CLIENT_MENOR_URL     



    async def getclientData(self, id_loja:str, token:str) -> httpx.Response:
        
        payload = {
            "id":id_loja
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


    async def getclientDataMaior(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id":id_loja
        }   
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'             
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.getclientdataMaiorurl, 
                json=payload,
                headers=header
            )

            return response   


    async def getclientDataMenor(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id":id_loja
        }   
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'             
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.getclientdataMenorurl, 
                json=payload,
                headers=header
            )

            return response                       
        

    async def getclientDataA(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id":id_loja
        }   
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'             
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.getclientdataAurl, 
                json=payload,
                headers=header
            )

            return response     


    async def getclientDataB(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id":id_loja
        }   
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'             
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.getclientdataBurl, 
                json=payload,
                headers=header
            )

            return response 


    async def getclientDataC(self, id_loja:str, token:str) -> httpx.Response:
        payload = {
            "id":id_loja
        }   
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'             
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.getclientdataCurl, 
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
