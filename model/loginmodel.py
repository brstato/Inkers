import httpx

class LoginModel:
    recovery_passwordURL:str = "http://127.0.0.1:8082/v1/resenha"
    loginURL:str             = "http://127.0.0.1:8082/api/v1/login"
    refreshTokenURL:str      = "http://127.0.0.1:8082/api/v1/token/refresh"


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

        async with httpx.AsyncClient() as client:

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