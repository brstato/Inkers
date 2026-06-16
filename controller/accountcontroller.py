import flet as ft
from model.accountmodel import AccountModel
from model.loginmodel import LoginModel
import json

class AccountController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.model = AccountModel()

    async def fetch_endereco(self, cep: str) -> dict:
        cep = "".join(filter(str.isdigit, cep))       
        if len(cep) != 8:
            raise ValueError("Informe um CEP válido.")
            
        response = await self.model.get_endereco(cep)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("CEP não encontrado")

    async def check_slug(self, slug: str, current_id: str) -> bool:
        response = await self.model.get_slug(slug)
        if response.status_code == 200:
            data = json.loads(response.content)
            slug_bool = bool(data.get("slug", False))
            id_loja = data.get("id_loja", "")
            if (slug_bool == True and id_loja != current_id) or (slug_bool == True and current_id == ""):
                return False
            return True
        return False


    async def load_account_data(self, id: str, token: str, r_token: str) -> dict:
        response = await self.model.getAccountData(id, token)

        if response.status_code == 401:
            response = await LoginModel().refresh_token_raw(r_token, id)
            if response.status_code == 200:
                data = json.loads(response.content)
                self.page.session.store.set("token",   data["token"  ])
                self.page.session.store.set("r_token", data["r_token"])

                token = data["token"]
                response = await self.model.getAccountData(id, token)
            else:
                raise PermissionError("Não autorizado")

        if response.status_code == 200:
            return json.loads(response.content)
        return {}


    async def save_account(self, data: dict, is_update: bool) -> dict:
        if not data.get("latitude") or not data.get("longitude"):
            lat, lng = await self.model.get_coordinates(
                data["endereco"], data["numero"], data["cidade"], data["estado"]
            )
            data["latitude"] = lat
            data["longitude"] = lng

        if not is_update:
            response = await self.model.register(
                data["username"], data["telefone"], data["email"], data["slug"],
                data["cep"], data["endereco"], data["bairro"], data["cidade"],
                data["estado"], data["numero"], data["complemento"], data["instagram"],
                data["m_pixel"], data["g_tag"], data["horarios"],
                data["latitude"], data["longitude"], data["google_ads_id"], 
                data["google_ads_nome"]
            )
            if response.status_code == 200:
                return {"success": True}
            elif response.status_code == 409:
                raise ValueError(f"O nome {data['username']} já está em uso!")
            else:
                raise Exception("Erro ao registrar a conta.")
        else:
            token = data["token"]
            r_token = data["r_token"]
            id = data["id"]
            response = await self.model.updateAccountData(
                id, data["username"], data["telefone"], data["email"],
                data["cep"], data["endereco"], data["bairro"], data["cidade"],
                data["estado"], data["numero"], data["complemento"], data["instagram"],
                data["m_pixel"], data["g_tag"], token, data["horarios"], data["slug"],
                data["latitude"], data["longitude"], data["google_ads_id"],
                data["google_ads_nome"]
            )
            
            if response.status_code == 401:
                response = await LoginModel().refresh_token_raw(r_token, id)
                if response.status_code == 200:
                    tokens = json.loads(response.content)
                    self.page.session.store.set("token",   tokens["token"  ])
                    self.page.session.store.set("r_token", tokens["r_token"])
                    token = tokens["token"]
                    
                    response = await self.model.updateAccountData(
                        id, data["username"], data["telefone"], data["email"],
                        data["cep"], data["endereco"], data["bairro"], data["cidade"],
                        data["estado"], data["numero"], data["complemento"], data["instagram"],
                        data["m_pixel"], data["g_tag"], token, data["horarios"], data["slug"],
                        data["latitude"], data["longitude"], data["google_ads_id"],
                        data["google_ads_nome"]
                    )

            if response.status_code == 200:
                self.page.session.store.set("account_name", data["username"])
                self.page.session.store.set("account_tel", data["telefone"])
                self.page.session.store.set("slug", data["slug"])
                return {"success": True, "token": token}
            else:
                raise Exception("Erro ao atualizar dados.")