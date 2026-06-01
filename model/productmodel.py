import httpx
from model.config import Config


class ProductModel:
    getproductdataURL:str    = Config.LIST_PRODUCT_URL
    createproductdataURL:str = Config.CREATE_PRODUCT_URL
    deleteproductdataURL:str = Config.DELETE_PRODUCT_URL
    editproductdataURL:str   = Config.UPDATE_PRODUCT_URL
    detailproductdataURL:str = Config.DETAIL_PRODUCT_URL     
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


    async def createProductData(self, nome:str, inf_valor:str, insumo:str,  
                                id_loja:str, comissionado:str, valor_custo:float, valor_venda:float,
                                quantidade_estoque:int, min_estoque: int,
                                token:str) -> httpx.Response:
        payload = {
            "id_loja":id_loja,
            "nome":nome,
            "inf_valor":inf_valor,
            "insumo":insumo,
            "valor_custo":valor_custo,
            "valor_venda":valor_venda,
            "quantidade_estoque":quantidade_estoque,
            "min_estoque":min_estoque,
            "comissionado":comissionado
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.createproductdataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def editProductData(self, id:int, nome:str, inf_valor:str, insumo:str, comissionado:str, 
                             valor_custo:float, valor_venda:float,
                            quantidade_estoque:int, min_estoque: int,
                            token:str) -> httpx.Response:
        payload = {
            "id":id,
            "nome":nome,
            "inf_valor":inf_valor,
            "insumo":insumo,
            "valor_custo":valor_custo,
            "valor_venda":valor_venda,
            "quantidade_estoque":quantidade_estoque,
            "min_estoque":min_estoque,
            "comissionado":comissionado
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.editproductdataURL, 
                json=payload,
                headers=header
            )

            return response  


    async def DetailProductData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.detailproductdataURL, 
                json=payload,
                headers=header
            )

            return response    


    async def getProductData(self, id:str, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getproductdataURL, 
                json=payload,
                headers=header
            )

            return response        
        

    async def deleteProductData(self, id:int, token:str) -> httpx.Response:
        payload = {
            "id":id
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.deleteproductdataURL, 
                json=payload,
                headers=header
            )

            return response          
