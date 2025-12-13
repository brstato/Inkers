import httpx
import model.config


class ProfessionlModel:
    getprofessionaldataURL:str    = "http://127.0.0.1:8082/api/v1/professional/list"
    deleteprofessionaldataURL:str = "http://127.0.0.1:8082/api/v1/professional/delete"
    detailprofessionaldataURL:str = "http://127.0.0.1:8082/api/v1/professional/detail"
    editprofessionaldataURL:str   = "http://127.0.0.1:8082/api/v1/professional/edit"    
    createprofessionaldataURL:str = "http://127.0.0.1:8082/api/v1/professional/create"   



    async def createProfessionalData(self, id:str, name:str, tel:str, comission:str, token:str) -> httpx.Response:
        payload = {
            "id_loja":id,
            "name":name,
            "tel":tel,
            "comission":comission
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.createprofessionaldataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def editProfessionalData(self, id:str, name:str, tel:str, comission:str, token:str) -> httpx.Response:
        payload = {
            "id":id,
            "name":name,
            "tel":tel,
            "comission":comission
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.editprofessionaldataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def DetailProfessionalData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.detailprofessionaldataURL, 
                json=payload,
                headers=header
            )

            return response    


    async def getProfessionalData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getprofessionaldataURL, 
                json=payload,
                headers=header
            )

            return response        
        

    async def deleteProfessionalData(self, id:int, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.deleteprofessionaldataURL, 
                json=payload,
                headers=header
            )

            return response          
