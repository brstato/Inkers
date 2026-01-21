import httpx

class LoginModel:
    recovery_passwordURL:str = "http://127.0.0.1:8082/api/v1/resenha"
    loginURL:str             = "http://127.0.0.1:8082/api/v1/login"
    refreshTokenURL:str      = "http://127.0.0.1:8082/api/v1/token/refresh"
    logingoogleURL:str       = "http://127.0.0.1:8082/api/v1/login_google"


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