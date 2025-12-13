import httpx


class ProductModel:
    getproductdataURL:str    = "http://127.0.0.1:8082/api/v1/product/list"
    createproductdataURL:str = "http://127.0.0.1:8082/api/v1/product/create"
    deleteproductdataURL:str = "http://127.0.0.1:8082/api/v1/product/delete"
    editproductdataURL:str   = "http://127.0.0.1:8082/api/v1/product/update"
    detailproductdataURL:str = "http://127.0.0.1:8082/api/v1/product/detail"     
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
                            comissao:int, quantidade_estoque:int, min_estoque: int,
                            token:str) -> httpx.Response:
        payload = {
            "id":id,
            "nome":nome,
            "inf_valor":inf_valor,
            "insumo":insumo,
            "valor_custo":valor_custo,
            "valor_venda":valor_venda,
            "comissao":comissao,
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
