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


    async def confirmar_agendamento(self):
        telefone        = self.instance.phone_input.value
        cliente_nome    = self.instance.name_input.value
        id_prof         = self.instance.id_profissional
        turno_escolhido = self.instance.selected_shift
        cliente_id      = self.instance.cliente_id
        
        if not turno_escolhido or not telefone:
            return

        dt       = self.instance.dates_data[self.instance.selected_date_index]
        data_iso = dt.strftime("%Y-%m-%d")

        horarios = {
            "Manhã": {"ini": "08:00", "fim": "12:00"},
            "Tarde": {"ini": "13:00", "fim": "18:00"},
            "Noite": {"ini": "18:00", "fim": "22:00"}
        }
        
        hora_ini = horarios[turno_escolhido]["ini"]
        hora_fim = horarios[turno_escolhido]["fim"]

        payload = {
            "uuid": self.instance.uuid,
            "cliente_id": cliente_id,
            "id_profissional": id_prof,
            "cliente": cliente_nome,
            "telefone": telefone,
            "data": data_iso,
            "hora_ini": hora_ini,
            "hora_fim": hora_fim
        }

        print("\n--- JSON PRONTO PARA ENVIO ---")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("------------------------------\n")

        self.instance.set_loading(True)
        try:
            response = await self.model.solicitar_agendamento(payload)
            
            if response.status_code == 200 or response.status_code == 201:                
                self.instance.selected_shift = None
                await self._get_client_data(None)
            else:
                self.instance.show_message_dialog(f"Erro {response.status_code}", f"Falha ao solicitar agendamento {response.text}")
                
        except Exception as ex:
            print(f"Erro ao confirmar agendamento: {ex}")
            self.instance.show_message_dialog("Erro", "Falha de comunicação com o servidor.")
            
        finally:
            self.instance.set_loading(False)
            self.page.update()


    async def ProcessarCalendario(self):
        self.availability_map.clear()

        # 1. CORREÇÃO: Organiza a agenda à prova de formatos de data variados do JSON
        agenda_por_data = {}
        for agendamento in self.agenda_profissional:
            data_raw = str(agendamento.get("data", "")).strip()
            
            # Extrai estritamente o YYYY-MM-DD
            data_padrao = ""
            if "T" in data_raw: data_padrao = data_raw.split("T")[0]
            elif " " in data_raw: data_padrao = data_raw.split(" ")[0]
            elif "/" in data_raw:
                p = data_raw.split("/")
                if len(p) == 3:
                    if len(p[0]) == 2: # Se for DD/MM/YYYY converte para YYYY-MM-DD
                        data_padrao = f"{p[2]}-{p[1]}-{p[0]}"
                    else:
                        data_padrao = data_raw.replace("/", "-")
            else:
                data_padrao = data_raw[:10]

            if data_padrao:
                if data_padrao not in agenda_por_data:
                    agenda_por_data[data_padrao] = []
                agenda_por_data[data_padrao].append(agendamento)

        # 2. Percorre os próximos 31 dias
        for i in range(31):
            data_loop = self.instance.now + datetime.timedelta(days=i)
            data_br = data_loop.strftime("%d/%m/%Y")
            data_iso = data_loop.strftime("%Y-%m-%d") # "2026-02-23"
            
            dia_semana_str = self.GetDayOfWeek(data_loop)
            config_dia = self.config_loja.get(dia_semana_str, {})
            loja_aberta = config_dia.get("aberto", False)
            
            if loja_aberta:
                inicio = config_dia.get("inicio", "00:00")
                fim = config_dia.get("fim", "00:00")
                
                # A) Turnos base que a loja funciona hoje
                turnos_base = self.CalcularTurnosDisponiveis(inicio, fim)
                
                # B) Pega os agendamentos já marcados para este dia específico
                agendamentos_do_dia = agenda_por_data.get(data_iso, [])
                
                # C) Descobre quais turnos já estão ocupados pelo profissional
                turnos_ocupados = set()
                for ag in agendamentos_do_dia:
                    turno_ag = self.ObterTurnoPelaHora(ag.get("hora_ini", "00:00"))
                    turnos_ocupados.add(turno_ag)
                
                # D) Remove os turnos ocupados da lista de disponíveis
                turnos_livres = [t for t in turnos_base if t not in turnos_ocupados]
                
                # E) Log visual no terminal (Para o programador auditar os dados)
                if len(agendamentos_do_dia) > 0:
                    print(f"[{data_br}] Ocupados: {turnos_ocupados} | Livres p/ Tela: {turnos_livres}")
                
                # F) Se sobrou algum turno livre, o dia fica disponível para clique
                if len(turnos_livres) > 0:
                    self.availability_map[data_br] = turnos_livres

        # Delega a construção da UI para a View
        self.instance.render_calendar(self.availability_map)


    def ObterTurnoPelaHora(self, hora_ini: str) -> str:
        try:
            # CORRIGIDO: Agora usa a variável correta "hora_ini"
            hora_int = int(str(hora_ini).strip().split(":")[0])
        except Exception as e:
            print(f"Erro ao converter hora '{hora_ini}': {e}")
            return "Manhã" 

        if hora_int < 12:
            return "Manhã"
        elif hora_int < 18:
            return "Tarde"
        else:
            return "Noite"


    def GetDayOfWeek(self, data: datetime.datetime) -> str:
        dia_python = data.isoweekday()
        dia_delphi = (dia_python % 7) + 1
        return str(dia_delphi)


    def CalcularTurnosDisponiveis(self, inicio_loja: str, fim_loja: str) -> list:
        Result = []
        # CORREÇÃO: Usa inteiros para avaliar o horário da loja
        try:
            h_ini = int(str(inicio_loja).strip().split(":")[0])
            h_fim = int(str(fim_loja).strip().split(":")[0])
        except:
            h_ini = 8
            h_fim = 18

        if h_ini < 12: Result.append("Manhã")
        if h_fim >= 13: Result.append("Tarde")
        if h_fim >= 18: Result.append("Noite")
        return Result

 
    async def init_data(self):
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

                self.instance.name_input.value = dados.get("cliente",      {}).get("nome",      "")
                self.instance.uuid             = dados.get("loja",         {}).get("uuid",      "")
                self.instance.cliente_id       = dados.get("cliente",      {}).get("cliente_id", 0)     
                self.instance.id_profissional  = dados.get("profissional", {}).get("id",         0)
                
                self.agenda_profissional = dados.get("agenda", [])
                
                config_str = dados.get("loja", {}).get("config_horario", "{}")
                
                try:
                    self.config_loja = json.loads(config_str)
                except:
                    self.config_loja = {}

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