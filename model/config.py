from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    BASE_API_URL = os.getenv('BASE_API_URL', 'http://127.0.0.1:8082/api/v1')


    GET_ITENS_URL         = f"{BASE_API_URL}/caixa/itens/list"
    GET_CLIENTS_URL       = f"{BASE_API_URL}/caixa/client/list"
    ABRIR_CAIXA_URL       = f"{BASE_API_URL}/caixa/abrir_caixa"    
    FECHAR_CAIXA_URL      = f"{BASE_API_URL}/caixa/fechar_caixa"       
    STATUS_CAIXA_URL      = f"{BASE_API_URL}/caixa/status"  
    RECEBER_VENDA_URL     = f"{BASE_API_URL}/caixa/venda" 
    GET_ITENS_INSUMO      = f"{BASE_API_URL}/caixa/insumo"
    UPDATE_INSUMO         = f"{BASE_API_URL}/caixa/insumo/update"
    UPDATE_NOTA_CLIENTE   = f"{BASE_API_URL}/caixa/cliente/update_nota"
    
    
    GET_AGENDA_URL           = f"{BASE_API_URL}/agenda/list"
    GET_AGENDA_RESUME_URL    = f"{BASE_API_URL}/agenda/resume"
    CREATE_AGENDAMENTO_URL   = f"{BASE_API_URL}/agenda/create"
    DELETE_AGENDA_URL        = f"{BASE_API_URL}/agenda/delete"
    DETAIL_AGENDA_URL        = f"{BASE_API_URL}/agenda/detail"
    UPDATE_AGENDA_URL        = f"{BASE_API_URL}/agenda/update"
    CONF_AGENDA_ZAP          = f"{BASE_API_URL}/agenda/send_confirmation"  
    CHECK_DIAS_FUNCIONAMENTO = f"{BASE_API_URL}/public/agenda/check"
    LIST_CLIENT_TEL          = f"{BASE_API_URL}/public/agenda/list_client_tel"
    LIST_PROFISSIONAL_ID     = f"{BASE_API_URL}/public/agenda/list_profissional_id"
    LIST_TURNOS_AGENDA       = f"{BASE_API_URL}/public/agenda/turnos"
    SOLICITAR_AGENDAMENTO    = f"{BASE_API_URL}/public/agenda/solicitar"
    LIST_PENDENTES_URL       = f"{BASE_API_URL}/agenda/pendentes"
    NOTIFY_PENDENTES_URL     = f"{BASE_API_URL}/agenda/notifica"
    

    CREATE_ANAMENESE_URL   = f"{BASE_API_URL}/anamnese/create"
    LIST_PROFISSIONAIS_URL = f"{BASE_API_URL}/anamnese/list_profissionais"
    

    GET_CONNECT_ZAP       = f"{BASE_API_URL}/whatsapp/connect"
    CREATE_ZAP_URL        = f"{BASE_API_URL}/whatsapp/create"
    

    CREATE_DESP_URL       = f"{BASE_API_URL}/despesas/create"
    RESUME_DESP_URL       = f"{BASE_API_URL}/despesas/resume"    
    LIST_MES_DESP_URL     = f"{BASE_API_URL}/despesas/list_mes"      
    DELETE_DESP_URL       = f"{BASE_API_URL}/despesas/delete"
    UPDATE_DESP_URL       = f"{BASE_API_URL}/despesas/update"
    BAIXAR_DESP_URL       = f"{BASE_API_URL}/despesas/baixa"
    
    
    UPDATE_ACCOUNT_URL    = f"{BASE_API_URL}/account/update"
    GET_ACCOUNT_DATA_URL  = f"{BASE_API_URL}/account/get_data"
    ACCOUNT_REGISTER_URL  = f"{BASE_API_URL}/account/register"
      
    # Client URLs
    CREATE_CLIENT_URL     = f"{BASE_API_URL}/client/create"
    DELETE_CLIENT_URL     = f"{BASE_API_URL}/client/delete"
    UPDATE_CLIENT_URL     = f"{BASE_API_URL}/client/update"
    DETAIL_CLIENT_URL     = f"{BASE_API_URL}/client/detail"
    LIST_CLIENT_URL       = f"{BASE_API_URL}/client/list"
    LIST_CLIENT_A_URL     = f"{BASE_API_URL}/client/list_A"
    LIST_CLIENT_B_URL     = f"{BASE_API_URL}/client/list_B"
    LIST_CLIENT_C_URL     = f"{BASE_API_URL}/client/list_C"
    LIST_CLIENT_MAIOR_URL = f"{BASE_API_URL}/client/list_maior"
    LIST_CLIENT_MENOR_URL = f"{BASE_API_URL}/client/list_menor"

    # Service URLs
    CREATE_SERVICE_URL    = f"{BASE_API_URL}/service/create"
    DELETE_SERVICE_URL    = f"{BASE_API_URL}/service/delete"
    UPDATE_SERVICE_URL    = f"{BASE_API_URL}/service/update"
    DETAIL_SERVICE_URL    = f"{BASE_API_URL}/service/detail"
    LIST_SERVICE_URL      = f"{BASE_API_URL}/service/list"

    # Product URLs
    LIST_PRODUCT_URL      = f"{BASE_API_URL}/product/list"
    CREATE_PRODUCT_URL    = f"{BASE_API_URL}/product/create"
    DELETE_PRODUCT_URL    = f"{BASE_API_URL}/product/delete"
    UPDATE_PRODUCT_URL    = f"{BASE_API_URL}/product/update"
    DETAIL_PRODUCT_URL    = f"{BASE_API_URL}/product/detail"

    # Login URLs
    RECOVERY_PASSWORD_URL = f"{BASE_API_URL}/resenha"
    LOGIN_URL             = f"{BASE_API_URL}/login"
    REFRESH_TOKEN_URL     = f"{BASE_API_URL}/token/refresh"
    LOGIN_GOOGLE_URL      = f"{BASE_API_URL}/login_google"

    # Professional URLs
    LIST_PROFESSIONAL_URL    = f"{BASE_API_URL}/professional/list"
    DELETE_PROFESSIONAL_URL  = f"{BASE_API_URL}/professional/delete"
    DETAIL_PROFESSIONAL_URL  = f"{BASE_API_URL}/professional/detail"
    EDIT_PROFESSIONAL_URL    = f"{BASE_API_URL}/professional/edit"
    CREATE_PROFESSIONAL_URL  = f"{BASE_API_URL}/professional/create"

    CREATE_EVENT_CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    G_REFRESH_TOKEN_URL       = "https://oauth2.googleapis.com/token"