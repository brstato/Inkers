from email import header
from model.config import Config
import httpx


class AgendaModel:
    def __init__(self):
        self.create_event_calendar_url = Config.CREATE_EVENT_CALENDAR_URL
        self.g_refresh_token_url       = Config.G_REFRESH_TOKEN_URL

        self.get_agenda_url        = Config.GET_AGENDA_URL
        self.get_agenda_resume_url = Config.GET_AGENDA_RESUME_URL
        self.create_agenda_url     = Config.CREATE_AGENDAMENTO_URL
        self.delete_agenda_url     = Config.DELETE_AGENDA_URL
        self.detail_agenda_url     = Config.DETAIL_AGENDA_URL
        self.update_agenda_url     = Config.UPDATE_AGENDA_URL
        self.enviar_confirmacao_url= Config.CONF_AGENDA_ZAP   
        self.list_pendentes_url    = Config.LIST_PENDENTES_URL


    async def _post_request(self, url:str, payload:dict, token: str) -> httpx.Response:
        header = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'            
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=header
            )
            return response    
        

    async def g_refresh_token(self, client_id: str, client_secret:str, refresh_token: str):
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }    
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.g_refresh_token_url,
                data=payload,
            )
            return response 


    async def enviar_confirmacao(self, mensagem, telefone:str, zap_instance:str, token:str):
        payload = {
            "message":{
                "number": f"55{telefone}",
                "text": mensagem,
                "linkPreview": False
            },             
            "instance":{"zap_instance": zap_instance}
        }

        return await self._post_request(self.enviar_confirmacao_url, payload, token)


    async def CreateEventGoogleCalendar(self, titulo:str, descricao:str, start_iso:str, end_iso:str, token:str):
        payload = {
            "summary": titulo,      # Título do evento (ex: "Corte de Cabelo - Cliente X")
            "description": descricao, # Detalhes
            "start": {
                "dateTime": start_iso,
                "timeZone": "America/Sao_Paulo", # Ajuste conforme sua região
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": "America/Sao_Paulo",
            },
            # "reminders": { ... } # Opcional: configurar lembretes
        }

        return await self._post_request(self.create_event_calendar_url, payload, token)
    

    async def UpadateAgendaData(self, id_agenda: int, id_prof:int, telefone:str, id_client:int, 
                                date:str, hora_ini:str, hora_fim:str,
                                 name_client:str, event_id:str, token:str, sinal:str, valor:str):
        payload = {
            "id":id_agenda,
            "id_prof": id_prof,
            "date":date,
            "hora_ini":hora_ini,
            "hora_fim":hora_fim,
            "id_client":id_client,
            "client":name_client,
            "telefone":telefone,
            "event_id":event_id,
            "sinal":sinal,
            "valor":valor
        }    


        await self._post_request(self.update_agenda_url, payload, token)


    async def DetailAgendaData(self, id_agenda: int, token: str):
        payload = {
            "id":id_agenda
        }

        return await self._post_request(self.detail_agenda_url, payload, token)


    async def DeleteAgendaData(self, id_agenda: int, token:str):
        payload = {
            "id":id_agenda
        }
        
        return await self._post_request(self.delete_agenda_url, payload, token)
    

    async def GetAgendaData(self, id_prof:int, date:str, token:str):
        payload = {
            "id": id_prof,
            "data":date
        }        

        return await self._post_request(self.get_agenda_url, payload, token)        
    

    async def GetAgendaResummeData(self, id_prof:int, date:str, token:str):
        payload = {
            "id": id_prof,
            "data":date
        }

        return await self._post_request(self.get_agenda_resume_url, payload, token)
    

    async def CreateAgendamento(self, id_prof:int, telefone:int, id_client:int, 
                                date:str, hora_ini:str, hora_fim:str,
                                 name_client:str, event_id:str, token:str,
                                 valor='', sinal='', id_loja:str=''):
        payload = {
            "id_prof": id_prof,
            "date":date,
            "hora_ini":hora_ini,
            "hora_fim":hora_fim,
            "id_client":id_client,
            "client_name":name_client,
            "telefone":telefone,
            "event_id":event_id,
            "valor":valor,
            "sinal":sinal,
            "id_loja":id_loja
        }

        await self._post_request(self.create_agenda_url, payload, token)


    async def list_pendentes(self, id_profissional: int, token: str):
        payload = {
            "id_profissional": id_profissional
        }    

        return await self._post_request(self.list_pendentes_url, payload, token)
