from model.config import Config
import httpx


class AgendaModel:
    def __init__(self):
        self.get_agenda_url        = Config.GET_AGENDA_URL
        self.get_agenda_resume_url = Config.GET_AGENDA_RESUME_URL
        self.create_agenda_url     = Config.CREATE_AGENDAMENTO_URL
        self.delete_agenda_url     = Config.DELETE_AGENDA_URL
        self.detail_agenda_url     = Config.DETAIL_AGENDA_URL
        self.update_agenda_url     = Config.UPDATE_AGENDA_URL


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
        

    async def UpadateAgendaData(self, id_agenda: int, id_prof:int, telefone:int, id_client:int, 
                                date:str, hora_ini:str, hora_fim:str,
                                 name_client:str, token:str):
        payload = {
            "id":id_agenda,
            "id_prof": id_prof,
            "date":date,
            "hora_ini":hora_ini,
            "hora_fim":hora_fim,
            "id_client":id_client,
            "client":name_client,
            "telefone":telefone
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
                                 name_client:str, token:str):
        payload = {
            "id_prof": id_prof,
            "date":date,
            "hora_ini":hora_ini,
            "hora_fim":hora_fim,
            "id_client":id_client,
            "client_name":name_client,
            "telefone":telefone
        }

        await self._post_request(self.create_agenda_url, payload, token)
