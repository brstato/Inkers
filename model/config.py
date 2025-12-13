class Config:
    BASE_API_URL = "http://127.0.0.1:8082/api/v1"

    GET_ITENS_URL    = f"{BASE_API_URL}/caixa/itens/list"
    GET_CLIENTS_URL  = f"{BASE_API_URL}/caixa/client/list"
    ABRIR_CAIXA_URL  = f"{BASE_API_URL}/caixa/abrir_caixa"    
    FECHAR_CAIXA_URL = f"{BASE_API_URL}/caixa/fechar_caixa"       
    STATUS_CAIXA_URL = f"{BASE_API_URL}/caixa/status"   