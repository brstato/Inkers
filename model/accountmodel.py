import httpx
from model.loginmodel import LoginModel
from model.config import Config
import urllib.parse
import os
import json


class AccountModel:
    registerURL:str          = Config.ACCOUNT_REGISTER_URL
    getaccountdataURL:str    = Config.GET_ACCOUNT_DATA_URL
    updateaccountdataURL:str = Config.UPDATE_ACCOUNT_URL
    getslugurl:str           = Config.GET_SLUG_URL
    getenderecoURL:str       = Config.GET_ENDERECO_URL
    updatemetatokenURL:str   = Config.UPDATE_META_LONG_TOKEN_URL
    getcoordinatesURL:str    = Config.GET_COORDINATES_URL_MAPBOX


    async def get_coordinates(self, logradouro:str, numero:str, cidade:str, estado:str):
        key = os.getenv("MAP")
        endereco_completo:str = f"{logradouro}, {numero}, {cidade}, {estado}, Brasil"
        endereco_url:str = urllib.parse.quote(endereco_completo)
        url:str = f"{self.getcoordinatesURL}{endereco_url}.json?access_token={key}&types=address"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    dados = response.json()
                    if "features" in dados and len(dados["features"]) > 0:
                        coords = dados["features"][0]["center"]
                        return coords[1], coords[0]
                else:
                    return None, None
            except Exception as e:  
                print(e)  
            
            

    async def get_endereco(self, cep:str) -> httpx.Response:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(f"https://brasilapi.com.br/api/cep/v2/{cep}")
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
        instagram:str,
        m_pixel:str,
        g_id:str,
        token, 
        horarios, 
        slug,
        latitude:float,
        longitude:float,
        google_ads_id:str,
        google_ads_nome:str,
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
            "insta": instagram,
            #"senha": senha,
            "id": id,
            "horario": horarios,
            "slug": slug,
            "meta_pixel": m_pixel,
            "g_analytics_id": g_id,
            "latitude": latitude,
            "longitude": longitude,
            "google_ads_id": google_ads_id,
            "google_ads_nome": google_ads_nome,
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


    async def update_meta_long_token(self, meta_long_token:str, token: str) -> httpx.Response:
        payload = {
            "meta_long_token": meta_long_token,
        }
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.updatemetatokenURL, 
                json=payload,
                headers=header
            )

            return response


    async def register(self, 
                        username:str, 
                        telefone: str, 
                        email:str, 
                        slug:str,
                        cep:str,
                        endereco:str,
                        bairro:str,
                        cidade:str,
                        estado:str,
                        numero:str,
                        complemento:str,
                        instagram:str,
                        m_pixel:str,
                        g_id:str,
                        horario,
                        latitude:float,
                        longitude:float,
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
            "insta": instagram,
            "slug": slug,
            "meta_pixel": m_pixel,
            "g_analytics_id": g_id,
            "horario": horario,
            "latitude": latitude,
            "longitude": longitude,
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