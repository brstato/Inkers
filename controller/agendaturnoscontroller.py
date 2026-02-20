import json
import datetime
from model.agendaturnosmodel import AgendaTurnosModel

class AgendaTurnosController:
    def __init__(self, page, instance):
        self.instance = instance  # Referência para a View
        self.page = page
        self.model = AgendaTurnosModel()
        
        # Variáveis de Estado (Memória)
        self.availability_map = {}
        self.config_loja = {}
        self.agenda_profissional = []

    def GetDayOfWeekDelphi(self, data: datetime.datetime) -> str:
        dia_python = data.isoweekday()
        dia_delphi = (dia_python % 7) + 1
        return str(dia_delphi)

    def CalcularTurnosDisponiveis(self, inicio_loja: str, fim_loja: str) -> list:
        Result = []
        if inicio_loja < "12:00": Result.append("Manhã")
        if fim_loja > "13:00":    Result.append("Tarde")
        if fim_loja >= "18:00":   Result.append("Noite")
        return Result

    async def ProcessarCalendario(self):
        self.availability_map.clear()

        for i in range(31):
            data_loop = self.instance.now + datetime.timedelta(days=i)
            data_br = data_loop.strftime("%d/%m/%Y")
            dia_semana_str = self.GetDayOfWeekDelphi(data_loop)
            
            config_dia = self.config_loja.get(dia_semana_str, {})
            loja_aberta = config_dia.get("aberto", False)
            
            if loja_aberta:
                inicio = config_dia.get("inicio", "00:00")
                fim = config_dia.get("fim", "00:00")
                turnos = self.CalcularTurnosDisponiveis(inicio, fim)
                
                if len(turnos) > 0:
                    self.availability_map[data_br] = turnos

        # Delega a construção da UI para a View
        self.instance.render_calendar(self.availability_map)

    async def init_data(self):
        self.instance.setup_appbar()
        self.instance.clear_lists()

    async def _get_client_data(self, e):
        telefone = self.instance.phone_input.value
        if not telefone:
            return

        self.instance.set_loading(True)

        try:
            response = await self.model.list_turnos_agenda(telefone)

            if response.status_code == 200:
                dados = json.loads(response.content)

                # Atualiza propriedades da View com dados limpos
                self.instance.name_input.value = dados.get("cliente", {}).get("nome", "")
                self.instance.id_profissional = dados.get("profissional", {}).get("id", 0)
                
                self.agenda_profissional = dados.get("agenda", [])
                
                config_str = dados.get("loja", {}).get("config_horario", "{}")
                try:
                    self.config_loja = json.loads(config_str)
                except:
                    self.config_loja = {}

                # Calcula horários e manda a View desenhar
                await self.ProcessarCalendario()

            elif response.status_code == 404:
                self.instance.name_input.value = ''
                self.instance.id_profissional = 0
                self.instance.show_message_dialog('Atenção!', 'Cliente não encontrado!')
            
            else:
                raise Exception(f"Erro HTTP {response.status_code}")

        except Exception as ex:
            print(f"Erro crítico no _get_client_data: {ex}")
            self.instance.show_message_dialog('Erro!', f'Falha ao carregar dados: {ex}')
            
        finally:
            self.instance.set_loading(False)

    async def select_date(self, index):
        dt = self.instance.dates_data[index]
        data_br = dt.strftime("%d/%m/%Y")
        
        if len(self.availability_map.get(data_br, [])) == 0:
            return 

        self.instance.selected_date_index = index
        # Diz para a view se redesenhar com base na nova seleção
        self.instance.render_calendar(self.availability_map)