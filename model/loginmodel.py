import httpx
from model.config import Config

class LoginModel:
    recovery_passwordURL:str = Config.RECOVERY_PASSWORD_URL
    loginURL:str             = Config.LOGIN_URL
    refreshTokenURL:str      = Config.REFRESH_TOKEN_URL
    logingoogleURL:str       = Config.LOGIN_GOOGLE_URL


    async def login_google(self, g_email:str, g_id:str, g_token:str, g_name:str) -> httpx.Response:
        payload = {
            "g_email":g_email,
            "g_id":   g_id,
            "g_token":g_token,
            "g_name": g_name
        }
        header = {
            'Content-Type': 'application/json'           
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.logingoogleURL, 
                json=payload,
                headers=header
            )

        return response           


    async def refresh_token(self, r_token:str, id:str) -> httpx.Response:
        payload = {
            "uuid": id,
            "r_token": r_token
        }
        header = {
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:

            response = await client.post(
                url=self.refreshTokenURL, 
                json=payload,
                headers=header
            )

        return response              


    async def recovery_password(self, username:str) -> httpx.Response:
        payload = {
            "email": username
        }
        header = {
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.post(
                url=self.recovery_passwordURL, 
                json=payload,
                headers=header
            )

        return response
    

    async def login(self, username:str, password:str) -> httpx.Response:
        payload = {
            "email":username,
            "senha":password
        }
        header = {
            'Content-Type': 'application/json'           
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.loginURL, 
                json=payload,
                headers=header
            )

        return response               