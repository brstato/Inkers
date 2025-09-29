class Config:
    BASE_API_URL = "http://127.0.0.1:8082/api/v1/caixa"

    GET_ITENS_URL = f"{BASE_API_URL}/itens/list"
    GET_CLIENTS_URL = f"{BASE_API_URL}/client/list"
    ABRIR_CAIXA_URL = f"{BASE_API_URL}/abrir_caixa"    