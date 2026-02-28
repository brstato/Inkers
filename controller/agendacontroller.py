import flet as ft
from model.professionalmodel import ProfessionlModel
from model.clientmodel import ClientModel
from utils.formatcurr import formatar_moeda_brasileira, _parse_currency
import json
from controller.call_api import ProtectedApiCall
from view.controls.controls_mainview.custoncardprofessional import CustonCardProfessional
from model.agendamodel import AgendaModel
from view.controls.custoncarditensagenda import CustonCardItensAgenda
from datetime import datetime, date, time
import calendar
from view.controls.custoncardcalendar import CustonCardDay, CustoncardMonth
import locale
from view.controls.custondialog import CustonDialog
from model.clientmodel import ClientModel
from view.controls.colors import AppColors



class AgendaController:
    def __init__(self, page: ft.Page, instance):
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        self.page = page
        self.instance = instance
        self.professionalModel = ProfessionlModel()
        self.agendamodel = AgendaModel()
        self.clientmodel = ClientModel()
        self.today = date.today()
        self.selected_year = self.today.year
        self.selected_month = self.today.month
        self.selected_day = self.today.day
        self.selected_date = self.today
        self.is_pendent: bool = False


    async def get_is_pendent(self):
       is_pendent = self.page.session.store.get("is_pendent")
       if is_pendent:
           self.instance.area_notificacoes.visible = True
       else:
           self.instance.area_notificacoes.visible = False
       self.page.update()


    async def abrir_lista_pendentes(self, e):
    
        self.instance.progressRing.visible = True
        self.page.update()
        
        self.instance.lista_cards_pendentes.controls.clear()
        
        try:
            # Reutiliza o seu método que busca do backend
            dados_pendentes = await self.list_pendentes()
            
            if dados_pendentes and "pendentes" in dados_pendentes:
                array_pendentes = dados_pendentes["pendentes"]
                
                # Guarda na memória para usarmos na hora de aprovar
                self.dados_pendentes_memoria = array_pendentes 
                
                if not array_pendentes:
                    self.instance.lista_cards_pendentes.controls.append(
                        ft.Text("Nenhuma solicitação pendente no momento.", color=AppColors.GRAY_LIGHT2)
                    )
                else:
                    for item in array_pendentes:
                        card = CustonCardItensAgenda(
                            page       =self.page,
                            instance   =self.instance,
                            telefone   =item.get("telefone"     ),
                            data_atend =item.get("data"         ),
                            hora_inicio=item.get("hora_ini"     ),
                            hora_fim   =item.get("hora_fim"     ),
                            name       =item.get("cliente"      ),
                            id_agenda  =item.get("id"           ),
                            id_client  =item.get("cod_client"   ),
                            
                            edit=self.iniciar_aprovacao_pendente, 
                            delete=self.confirm_delete_agendamento, 
                            tap=self.instance.list_agendamento.on_card_selected,
                            is_pendente=True 
                        )
                        self.instance.lista_cards_pendentes.controls.append(card)
            
            self.page.show_dialog(self.instance.modal_pendentes)
            
        except Exception as ex:
            print(f"Erro ao listar pendentes: {ex}")
            #await self.show_eror_dialog("Erro ao buscar solicitações.")
            
        finally:
            self.instance.progressRing.visible = False
            self.page.update()


    async def iniciar_aprovacao_pendente(self, e):
        id_selecionado = self.instance.id 
        
        pedido = next((p for p in getattr(self, 'dados_pendentes_memoria', []) if p["id"] == id_selecionado), None)
        
        if pedido:
            # 3. Fecha o modal de pendentes
            self.page.pop_dialog()
            
            # 4. Formata a data (O JSON envia YYYY-MM-DD, precisamos de DD/MM/YYYY)
            data_obj = datetime.strptime(pedido.get("data"), "%Y-%m-%d")
            data_br = data_obj.strftime("%d/%m/%Y")
            
            # 5. Preenche os seus campos já existentes do modal de agendamento normal!
            self.instance.edt_date_agendamento.value = data_br
            self.instance.edt_hora_ini.value         = pedido.get("hora_ini"     )
            self.instance.edt_hora_fim.value         = pedido.get("hora_fim"     )
            self.instance.edt_client_telefone.value  = pedido.get("telefone"     )
            self.instance.client_name                = pedido.get("cliente"      )
            self.instance.client_id                  = pedido.get("cod_client", 0)
            self.instance.edt_edt_sinal.value        = pedido.get("sinal",      0)
            self.instance.edt_edt_valor.value        = pedido.get("valor",      0)
            self.instance.id                         = id_selecionado            
            
            self.instance.edt_client_name.label = f"Cliente App: {pedido.get('cliente')}"
            
            self.page.show_dialog(self.instance.modal_create_agenda)
            self.page.update()


    async def list_pendentes(self):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.agendamodel.list_pendentes,
            id_profissional=self.instance.id_prof,
            token=self.instance.token
        ).call_api_refresh_token()

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None    


    async def renew_google_token(self): 

            if not self.instance.g_r_token:
                return False

            client_id = '184100860737-52caf580q16d4ht8hgkl7ak8p7dr92js.apps.googleusercontent.com'
            client_secret = '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'

            try:
                # Import requests se não tiver no topo: import requests
                response = await self.agendamodel.g_refresh_token(
                    client_id,
                    client_secret,
                    self.instance.g_r_token
                )
                
                if response.status_code == 200:
                    new_data = response.json()
                    new_access_token = new_data['access_token']
                    
                    # Atualiza na Memória
                    self.instance.g_token = new_access_token
                    
                    # Atualiza no Disco (Persistência)
                    self.page.session.store.set("google_access_token", new_access_token)
                    
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Erro na renovação: {e}")
                return False


    async def enviar_confirmacao(self, telefone, nome_cliente, data, hora, link_google):
            
            mensagem = (
                f"Olá, *{nome_cliente}*! 👋\n\n"
                f"Seu agendamento está confirmado.\n"
                f"🗓 *Data:* {data}\n"
                f"⏰ *Horário:* {hora}\n\n"
                f"Confira os detalhes e adicione à sua agenda clicando abaixo:\n"
                f"{link_google}"
            )
                
            response = await ProtectedApiCall(
                self.page,
                self.instance,
                self.agendamodel.enviar_confirmacao,
                mensagem=mensagem,
                telefone=telefone,
                zap_instance=self.instance.zap_instance,
                token=self.instance.token
            ).call_api_refresh_token()

            if response.status_code == 201 or response.status_code == 200:
                print("Mensagem enviada com sucesso!")
                return True
            else:
                print(f"Erro ao enviar WPP: {response.text}")
                return False


    async def create_event_google_calendar(self, titulo: str, data: str, hora_ini: str, hora_fim: str, descricao: str):

        try:
            # Tenta renovar o token antes de começar por precaução
            await self.renew_google_token()

            date_obj = datetime.strptime(data, "%d/%m/%Y").date()

            start_dt = datetime.combine(date_obj, datetime.strptime(hora_ini, "%H:%M").time())
            end_dt   = datetime.combine(date_obj, datetime.strptime(hora_fim, "%H:%M").time())

            start_iso = start_dt.isoformat()
            end_iso = end_dt.isoformat()  

            response = await self.agendamodel.CreateEventGoogleCalendar(
                    titulo=titulo, 
                    descricao=descricao,
                    start_iso=start_iso,
                    end_iso=end_iso,
                    token=self.instance.g_token
               )

            if response.status_code == 200:
                created_event = response.json()
                google_id = created_event.get("id")
                google_link = created_event.get("htmlLink")
                return google_id, google_link

            elif response.status_code == 401:
                # Se der 401, tenta renovar o token e repetir a requisição
                print("Token Google expirado, tentando renovar...")
                if await self.renew_google_token():
                    response = await self.agendamodel.CreateEventGoogleCalendar(
                        titulo=titulo, 
                        descricao=descricao,
                        start_iso=start_iso,
                        end_iso=end_iso,
                        token=self.instance.g_token
                    )
                    
                    if response.status_code == 200:
                        created_event = response.json()
                        google_id = created_event.get("id")
                        google_link = created_event.get("htmlLink")
                        return google_id, google_link

            # Se cair aqui, loga o erro e retorna vazio para evitar quebra no desempacotamento
            print(f"Erro no Google Calendar: {response.status_code} - {response.text}")
            return '', ''
                     
        except Exception as e:
            print(f"Excessão ao criar evento Google: {e}")
            return '', ''


    async def list_resume_agenda(self, date:str):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.agendamodel.GetAgendaResummeData,
            id_prof=self.instance.id_prof,
            date=date,
            token=self.instance.token
        ).call_api_refresh_token()

        array = json.loads(response.content)["message"]

        if not array:
            for card in self.instance.calendario.controls:
                if isinstance(card, CustonCardDay) and card.indicator.visible:
                    card.indicator.visible = False
            self.page.update()
            return

        datas_com_agendamento = set()        

        for item in array:
            data_str = item["date"]
            datetime_obj = datetime.strptime(data_str, '%d-%m-%y %H:%M:%S')
            datas_com_agendamento.add(datetime_obj.date())

        if not datas_com_agendamento:
            return

      
        for card in self.instance.calendario.controls:
            if isinstance(card, CustonCardDay):
                if card.card_date in datas_com_agendamento:
                    if not card.indicator.visible:
                        card.indicator.visible = True
                            
                else:
                    if card.indicator.visible:
                        card.indicator.visible = False
                        

        
        self.page.update()                               


    async def on_month_tap(self, card_instance: CustoncardMonth):
        if self.instance.id_prof == 0:
            dialog = CustonDialog(
                page=self.page,
                title="Atenção",
                content="Selecione um profissional antes de prosseguir.",
                actions=[
                    ft.TextButton(
                        content="OK", 
                        on_click=lambda e:[self.page.pop_dialog(),self.page.update()]
                        )
                    ]
            )
            self.page.show_dialog(dialog)
            self.page.update()
            return   

        self.instance.progressRing.visible = True
        self.page.update()

        self.instance.month_row.on_card_selected(card_instance)

        selected_date_from_card = card_instance.data_do_mes
        
        if selected_date_from_card:
            if selected_date_from_card.year == self.today.year and selected_date_from_card.month == self.today.month:
                self.selected_date = self.today
            else:
                self.selected_date = selected_date_from_card

            await self.build_calendar(self.selected_date.year, self.selected_date.month)
        
        self.instance.list_agendamento.controls.clear()

        await self.ListAgendamentos()

        #date_str = f"{self.selected_date.year}-{self.selected_date.month}-{self.selected_date.day}"
        date_str = self.selected_date.strftime('%Y-%m-%d')

        self.page.run_task(self.list_resume_agenda, date_str) 

        self.instance.progressRing.visible = False
        self.page.update()            


    async def build_month(self):
        
        self.instance.progressRing.visible = True
        self.page.update()
        
        ano_atual = self.today.year
        mes_atual = self.today.month        
        
        self.instance.month_row.controls.clear()

        for mes in range(12):
            novo_mes_num = (mes_atual - 1 + mes) % 12 + 1
            novo_ano_num = ano_atual + (mes_atual - 1 + mes) // 12
            data_do_mes = date(novo_ano_num, novo_mes_num, 1)
            nome_mes = data_do_mes.strftime("%B").upper()
            is_mes_atual = (novo_ano_num == ano_atual) and (novo_mes_num == mes_atual)

            card = CustoncardMonth(
                self.page,
                nome_mes,
                is_mes_atual,
                self.on_month_tap,
                data_do_mes
            )

            self.instance.month_row.controls.append(card)

        self.instance.progressRing.visible = False
        self.page.update()


    async def build_calendar(self, year:int, month:int):
        self.instance.progressRing.visible = True
        self.page.update()

        self.instance.calendario.controls.clear()
        start_day: int = 1

        if year == self.today.year and month == self.today.month:
            start_day = self.today.day

        num_dias = calendar.monthrange(year, month)[1]

        card_to_select = None

        for day in range(start_day, num_dias + 1):
            current_day_date = date(year, month, day)

            is_hoje = (current_day_date == self.today)
            
            day_abbr = current_day_date.strftime("%a").upper()

            card = CustonCardDay(
                self.page,
                current_day_date,
                is_hoje,
                day_abbr,
                self.on_day_tap
            )

            if current_day_date == self.selected_date:
                card_to_select = card

            self.instance.calendario.controls.append(card)

        if card_to_select:
            self.instance.calendario.on_card_selected(card_to_select)
        elif self.isinstance.calendario.controls:
            first_card = self.instance.calendario.controls[0]
            if isinstance(first_card, CustonCardDay):
                self.instance.calendario.on_card_selected(first_card)
                self.selected_date = first_card.card_date    

        self.instance.progressRing.visible = False


        self.page.update()


    async def ListProfissionais(self):
        
        self.instance.progressRing.visible = True
        self.page.update()
        
        self.instance.list_profissionais.controls.clear()

        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.professionalModel.getProfessionalData,
            id=self.instance.id_loja, 
            token=self.instance.token
        ).call_api_refresh_token()

        array = json.loads(response.content)["message"]

        for item in array:
            name      = item["name"    ]
            id_prof   = item["id"      ]
            comission = item["comissao"]

            card = CustonCardProfessional(
                instance=self.instance,
                name=name,
                id=id_prof,
                comission=comission,
                tap=self.on_professional_selected
            )

            self.instance.list_profissionais.controls.append(card) 

        if len(array) == 1:
            self.instance.id_prof = id_prof          

        self.instance.progressRing.visible = False

        self.page.update()        


    async def ListAgendamentos(self):
        self.instance.progressRing.visible = True
        self.page.update()

        self.instance.list_agendamento.controls.clear()

        str_date = self.selected_date.strftime('%Y-%m-%d')

        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.agendamodel.GetAgendaData,
            id_prof=self.instance.id_prof,
            date=str_date,
            token=self.instance.token
        ).call_api_refresh_token()

        array = json.loads(response.content)


        for item in array:
            cliente  = item["cliente"   ]
            hora_ini = item["hora_ini"  ]
            hora_fim = item["hora_fim"  ]
            telefone = item["telefone"  ]
            id_agenda= item["id"        ]
            id_client= item["cod_client"]
            event_id = item["event_id"  ]
            tarefa   = item["tarefa"    ]
            data     = item["data"      ]


            card = CustonCardItensAgenda(
                page=self.page,
                instance=self.instance,
                telefone=telefone,
                valor=0.00,
                atendimento=tarefa,
                hora_inicio=hora_ini,
                hora_fim=hora_fim,
                name=cliente,
                id_agenda=id_agenda,
                id_client=id_client,
                event_id=event_id,
                data_atend=data,
                delete=self.confirm_delete_agendamento,
                tap=self.instance.list_agendamento.on_card_selected,
                edit=self.detail_agendamento
            )
            self.instance.list_agendamento.controls.append(card)

        self.instance.progressRing.visible = False

        self.page.update()    


    async def get_data(self):
        self.instance.id_loja      = self.page.session.store.get("id"                  )
        self.instance.token        = self.page.session.store.get("token"               )
        self.instance.r_token      = self.page.session.store.get("r_token"             )   
        self.instance.g_token      = self.page.session.store.get("google_access_token" )  
        self.instance.zap_instance = self.page.session.store.get("zap_instance"        )
        self.instance.g_r_token    = self.page.session.store.get("google_refresh_token")

        refresh = self.instance.r_token
        
        if not self.instance.token or not self.instance.id_loja:
            self.page.go("/")
            self.page.update()
            return

        await self.ListProfissionais() 
        await self.build_month()
        await self.build_calendar(self.today.year, self.today.month) 
        await self.ListAgendamentos()
        await self.get_is_pendent()

        date_str = f"{self.today.year}-{self.today.month:02d}-{self.today.day:02d}"
        self.page.run_task(self.list_resume_agenda, date_str)

        self.page.run_task(self.list_clients)
        

    async def on_day_tap(self, card_instance: CustonCardDay):     
        self.instance.calendario.on_card_selected(card_instance)
        self.selected_date = card_instance.card_date
        await self.ListAgendamentos()


    async def on_professional_selected(self, card_instance: CustonCardProfessional):
        self.instance.progressRing.visible = True
        self.page.update()

        await self.instance.list_profissionais.on_card_selected(card_instance)

        self.instance.id_prof = card_instance.id

        await self.ListAgendamentos()

        date_str = self.selected_date.strftime('%Y-%m-%d')

        self.page.run_task(self.list_resume_agenda, date_str)

        self.instance.progressRing.visible = False
        self.page.update()


    async def list_clients(self):    
        self.instance.progressRing.visible = True
        self.page.update()

        response  = await ProtectedApiCall(
            self.page,
            self.instance,
            self.clientmodel.getclientData,
            id_loja=self.instance.id_loja,
            token=self.instance.token
        ).call_api_refresh_token()

        array = json.loads(response.content)["message"]

        options:list = []

        for item in array:
            nome          = item["nome"    ]
            telefone      = item["telefone"]
            id_client     = item["id"      ]

            dados = {
                "telefone": telefone,
                "id_client": id_client,
                "nome":nome
            }

            json_key = json.dumps(dados)

            options.append(
                ft.DropdownOption(
                    style=ft.ButtonStyle(
                        color=AppColors.GRAY_DARK,                    
                    ),
                    text=nome,
                    key=json_key
                )
            )

        self.instance.edt_client_name.options = options

        self.instance.progressRing.visible = False
        self.page.update()


    async def on_client_selected(self, e: ft.ControlEvent):

        json_key = e.control.value

        if json_key:
            dados_do_cliente = json.loads(json_key)

            self.instance.client_id       = dados_do_cliente.get('id_client')
            self.instance.client_telefone = dados_do_cliente.get('telefone', '')
            self.instance.client_name     = dados_do_cliente.get('nome',     '')

            self.instance.edt_client_telefone.value = self.instance.client_telefone

        self.page.update()


    async def selected_date_calendar(self, e):
       self.instance.edt_date_agendamento.value = self.instance.calendario_agenda.value.strftime("%d/%m/%Y") 
       self.page.update()        


    async def selected_time_ini(self, e):
       self.instance.edt_hora_ini.value = self.instance.hora_ini.value.strftime("%H:%M") 
       self.page.update()      


    async def selected_time_fim(self, e):
       self.instance.edt_hora_fim.value = self.instance.hora_fim.value.strftime("%H:%M") 
       self.page.update()            


    async def fechar_modal_agenda(self, e):
        self.page.pop_dialog()
        self.page.update()    


    async def create_agenda(self, e):
        self.page.pop_dialog()
        self.page.show_dialog(self.instance.modal_create_agenda)
        self.instance.edt_date_agendamento.value = ''
        self.instance.edt_hora_ini.value = ''
        self.instance.edt_hora_fim.value = ''
        self.instance.edt_date_agendamento.value = ''
        self.instance.edt_client_telefone.value = ''
        self.instance.edt_client_name.value = ''
        self.page.update()           


    async def show_eror_dialog(self, aviso:str)-> CustonDialog:
        dialog = CustonDialog(
            page=self.page,
            title='Atenção',
            content=aviso,
            actions=[
                ft.TextButton("OK", on_click=lambda e: [self.page.pop_dialog(), self.page.update()])
            ]
        )

        self.page.show_dialog(dialog)
        self.page.update()


    async def confirm_agendamento(self, e):
        data_str = self.instance.edt_date_agendamento.value  
        data_comparacao = datetime.strptime(data_str, '%d/%m/%Y').date()
        hoje = date.today()

        hora_ini_str = self.instance.edt_hora_ini.value
        hora_fim_str = self.instance.edt_hora_fim.value
  
        hora_ini_obj = datetime.strptime(hora_ini_str, '%H:%M').time()
        hora_fim_obj = datetime.strptime(hora_fim_str, '%H:%M').time()        

        if self.instance.id_prof == 0:
            await self.show_eror_dialog('Selecione o profissional!')
            return

        elif self.instance.client_id == 0:
            await self.show_eror_dialog('Selecione o cliente!')
            return
        
        elif not data_str:
            await self.show_eror_dialog('Selecione a data do agendamento!')
            return
        
        elif not hora_fim_str or not hora_ini_str: 
            await self.show_eror_dialog('Preencha a hora de início e fim!')
            return
        
        elif hoje > data_comparacao: 
            await self.show_eror_dialog('A data do agendamento não pode ser anterior a data de hoje!' )
            return   

        elif not hora_ini_str:
            await self.show_eror_dialog('Preencha o horario inicial para o atendimento!')
            return
        
        elif not hora_fim_str:
            await self.show_eror_dialog('Preencha o horario final para o atendimento!')
            return
        
        elif hora_ini_obj >= hora_fim_obj:
            await self.show_eror_dialog('O horario de inicio não pode ser maior que o horario de finalização do atendimento!')
            return
        
        event_id, event_link = await self.create_event_google_calendar(
            titulo=f"Atendimento - {self.instance.client_name}",
            data=data_str,
            hora_ini=hora_ini_str,
            hora_fim=hora_fim_str,
            descricao=f"Atendimento agendado para o cliente {self.instance.client_name}, valor: {self.instance.edt_edt_valor.value}, sinal: {self.instance.edt_edt_sinal.value}."
        )

        # Só envia confirmação com link se o link existir (ou envia sem)
        # O método enviar_confirmacao agora deve lidar com link_google sendo '' ou None se necessário
        await self.enviar_confirmacao(
            self.instance.client_telefone,
            self.instance.client_name,
            data_str,
            hora_ini_str,
            event_link if event_link else "Agendamento confirmado."
        )

        if self.instance.id == 0:

            await ProtectedApiCall(
                self.page,
                self.instance,
                self.agendamodel.CreateAgendamento,
                id_prof    =self.instance.id_prof, 
                date       =data_str, 
                hora_ini   =hora_ini_str, 
                hora_fim   =hora_fim_str,
                id_client  =self.instance.client_id, 
                name_client=self.instance.client_name, 
                telefone   =self.instance.edt_client_telefone.value,
                event_id   =event_id,
                token      =self.instance.token,
                valor      =self.instance.edt_edt_valor.value,
                sinal      =self.instance.edt_edt_sinal.value,
                id_loja    =self.instance.id_loja
            ).call_api_refresh_token()

        else:

            await ProtectedApiCall(
                self.page,
                self.instance,
                self.agendamodel.UpadateAgendaData,
                id_agenda  =self.instance.id, 
                id_prof    =self.instance.id_prof,  
                telefone   =self.instance.edt_client_telefone.value, 
                id_client  =self.instance.client_id,
                date       =data_str, 
                hora_ini   =hora_ini_str,
                hora_fim   =hora_fim_str,
                name_client=self.instance.client_name, 
                event_id   =event_id,
                token      =self.instance.token,
                valor      =self.instance.edt_edt_valor.value,
                sinal      =self.instance.edt_edt_sinal.value,                
            ).call_api_refresh_token()    

        self.page.pop_dialog()
        self.page.update()

        self.instance.id = 0

        date_str = self.selected_date.strftime('%Y-%m-%d')

        await self.list_resume_agenda(date_str)
        await self.ListAgendamentos()


    async def delete_agendamento(self):
        await ProtectedApiCall(
            self.page,
            self.instance,
            self.agendamodel.DeleteAgendaData,
            id_agenda = self.instance.id,
            token = self.instance.token
        ).call_api_refresh_token()

        self.instance.id = 0

        date_str = self.selected_date.strftime('%Y-%m-%d')
        await self.list_resume_agenda(date_str)
        await self.ListAgendamentos()
        await self.abrir_lista_pendentes(None)


    async def confirm_delete_agendamento(self, e):
        dialog = CustonDialog(
            self.page,
            'Atenção',
            'Deseja excluir este agendamento?',
            [
                ft.TextButton(
                    'Cancelar',
                    on_click=lambda e:[self.page.pop_dialog(), self.page.update()]
                ),
                ft.TextButton(
                    'Excluir',
                    on_click=lambda e:[
                        self.page.pop_dialog(),
                        self.page.update(),
                        self.page.run_task(self.delete_agendamento)
                    ]
                )
            ]
        )
        self.page.show_dialog(dialog)
        self.page.update()


    async def detail_agendamento(self, e):
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.agendamodel.DetailAgendaData,
            id_agenda = self.instance.id,
            token = self.instance.token
        ).call_api_refresh_token()

        data = json.loads(response.content)

        raw_date_string = data.get("data")

        input_format = "%d-%m-%y %H:%M:%S"
        output_format = "%d/%m/%Y"        

        date_obj = datetime.strptime(raw_date_string, input_format)

        date = date_obj.strftime(output_format)

        client_name  = data.get("client"  )
        client_phone = data.get("telefone")

        key = None

        for option in self.instance.edt_client_name.options:
            option_data = json.loads(option.key)
            if option_data.get("nome") == client_name and option_data.get("telefone") == client_phone:
                key = option.key
                break

        self.instance.edt_client_name.value      = key
        self.instance.edt_date_agendamento.value = date
        self.instance.edt_client_telefone.value  = data.get("telefone" )
        self.instance.edt_hora_ini.value         = data.get("hora_ini" )
        self.instance.edt_hora_fim.value         = data.get("hora_fim" )
        self.instance.client_id                  = data.get("id_client")
        self.instance.id_prof                    = data.get("id_prof"  )
        self.instance.edt_edt_valor.value        = data.get("valor"    )
        self.instance.edt_edt_sinal.value        = data.get("sinal"    )

        self.page.show_dialog(self.instance.modal_create_agenda)
        self.page.update()
