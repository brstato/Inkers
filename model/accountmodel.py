import httpx
from model.loginmodel import LoginModel
from model.config import Config


class AccountModel:
    registerURL:str          = Config.ACCOUNT_REGISTER_URL
    getaccountdataURL:str    = Config.GET_ACCOUNT_DATA_URL
    updateaccountdataURL:str = Config.UPDATE_ACCOUNT_URL
    getslugurl:str           = Config.GET_SLUG_URL
    getenderecoURL:str       = Config.GET_ENDERECO_URL

    async def get_endereco(self, cep:str) -> httpx.Response:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(f"https://brasilapi.com.br/api/cep/v1/{cep}")
            return response


    async def updateAccountData(
        self, 
        id:str, 
        nome:str, 
        telefone:str, 
        email:str,
        cep:str,
        endereco:str,
        bairro:str,
        cidade:str,
        estado:str,
        numero:str,
        complemento:str,
        m_pixel:str,
        g_id:str,
        token, 
        horarios, 
        slug
    ) -> httpx.Response:
        
        payload = {
            "nome": nome,
            "telefone": telefone,
            "email": email,
            "cep": cep,
            "endereco": endereco,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "numero": numero,
            "complemento": complemento,
            #"senha": senha,
            "id": id,
            "horario": horarios,
            "slug": slug,
            "meta_pixel": m_pixel,
            "g_analytics_id": g_id,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.updateaccountdataURL, 
                json=payload,
                headers=header
            )

            return response


    async def getAccountData(self, id: str, token,) -> httpx.Response:
        payload = {
            "id": id,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getaccountdataURL, 
                json=payload,
                headers=header
            )

            return response


    async def register(self, 
                        username:str, 
                        telefone: str, 
                        email:str, 
                        cep:str,
                        endereco:str,
                        bairro:str,
                        cidade:str,
                        estado:str,
                        numero:str,
                        complemento:str,
                        #password: str, 
                        slug:str,
                        m_pixel:str,
                        g_id:str,
                        horario
    ) -> httpx.Response:
        payload = {
            "nome": username,
            "telefone": telefone,
            "email": email,
            "cep": cep,
            "endereco": endereco,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "numero": numero,
            "complemento": complemento,
            "slug": slug,
            "meta_pixel": m_pixel,
            "g_analytics_id": g_id,
            "horario": horario
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.registerURL, 
                json=payload,
                headers=header
            )

            return response


    async def get_slug(self, slug:str) -> httpx.Response:
        payload = {
            "slug": slug,
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.getslugurl, 
                json=payload,
                headers=header
            )

            return response