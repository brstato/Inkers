import flet as ft
from view.controls.colors import AppColors
from model.agendaturnosmodel import AgendaTurnosModel

class AgendaTurnosController:
    def __init__(self, page: ft.Page, instance):
        self.instance = instance
        self.page = page
        self.model = AgendaTurnosModel()
        self.availability_map = {}

    async def init_data(self):
        """Chamado pelo did_mount da View para carregar tudo"""
        self.instance.progress_ring.visible = True # Se tiver loading, ativa aqui
        self.page.update()
        
        await self._fetch_availability()
        await self._build_calendar()
        
        self.instance.progress_ring.visible = False
        self.page.update()

    async def _fetch_availability(self):
        """Busca dados da API e preenche o mapa de disponibilidade"""
        try:
            # O ID do profissional pode vir da navegação ou ser 0 para buscar da loja geral
            # Estou assumindo 0 ou pegando de algum lugar da view se tiver
            id_prof_dummy = 0 
            
            # Chama seu Model recém-criado
            response = await self.model.check_dias_funcionamento(
                telefone_loja=self.instance.tel,
                telefone_profissional=self.instance.tel               
            )

            if response.status_code == 200:
                data = response.json()
                # O Delphi retorna algo como: 
                # { "calendario": [ { "data": "18/02/2026", "turnos": ["Manhã", "Tarde"] }, ... ] }
                
                self.availability_map = {}
                calendario = data.get("calendario", [])
                
                for dia_info in calendario:
                    data_str = dia_info.get("data") # Formato dd/mm/yyyy vindo do Delphi
                    turnos = dia_info.get("turnos", [])
                    
                    # Guarda os turnos disponíveis para este dia.
                    # Se a lista turnos estiver vazia, o dia é considerado fechado.
                    self.availability_map[data_str] = turnos
            else:
                print(f"Erro API: {response.status_code}")
                
        except Exception as e:
            print(f"Erro ao buscar disponibilidade: {e}")
            self.availability_map = {}

    def _setup_appbar(self):
        # AppBar personalizado ou padrão (ajustado para escuro)
        self.instance.appbar = ft.AppBar(
            title=ft.Text(f"Agenda - {self.instance.name}", color=AppColors.GRAY_LIGHT2),
            bgcolor=AppColors.BACKGROUND_DARK,
            elevation=0,
            leading=None
        ) 

    async def _build_calendar(self):
        """Reconstrói a linha de dias baseado no índice selecionado"""
        self.instance.date_controls_row.controls.clear()
        try:
            current_date = self.instance.dates_data[self.instance.selected_date_index]

            meses_pt = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
                "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]            
        except:
            pass    
        
        dias_pt = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]

        for i, dt in enumerate(self.instance.dates_data):
            # Formata data para bater com a chave do dicionário (dd/mm/yyyy)
            date_str = dt.strftime("%d/%m/%Y")
            
            # Verifica se o dia existe no mapa E se tem turnos
            turnos_do_dia = self.availability_map.get(date_str, [])
            is_available = len(turnos_do_dia) > 0
            
            is_selected = (i == self.instance.selected_date_index)

            # --- Lógica de Estilos ---
            if not is_available:
                # DIA BLOQUEADO (Escuro e sem clique)
                day_color = ft.Colors.GREY_800
                weekday_color = ft.Colors.GREY_900
                weight_day = "normal"
                on_click_action = None
                opacity = 0.3
            else:
                # DIA DISPONÍVEL
                if is_selected:
                    day_color = AppColors.ORANGE_DARK
                    weekday_color = AppColors.GRAY_LIGHT4
                    weight_day = "bold"
                else:
                    day_color = AppColors.GRAY_LIGHT2
                    weekday_color = AppColors.GRAY_LIGHT2
                    weight_day = "normal"
                
                on_click_action = lambda e, idx=i: self.page.run_task(self._select_date, idx)
                opacity = 1.0

            size_day = 22 if is_selected else 18

            btn = ft.Container(
                on_click=on_click_action,
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                border_radius=10,
                opacity=opacity, # Visualmente "apagado" se indisponível
                animate_opacity=300,
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(dias_pt[dt.weekday()], size=12, color=weekday_color),
                        ft.Text(str(dt.day), size=size_day, color=day_color, weight=weight_day),
                    ]
                )
            )
            self.instance.date_controls_row.controls.append(btn)
        
        self.page.update()
        
        # Atualiza os turnos baseados no dia selecionado inicialmente
        current_date_str = self.instance.dates_data[self.instance.selected_date_index].strftime("%d/%m/%Y")
        self._update_shifts_display(current_date_str)           

    async def _select_date(self, index):
        # Segurança: só seleciona se estiver disponível
        dt = self.instance.dates_data[index]
        date_str = dt.strftime("%d/%m/%Y")
        
        if len(self.availability_map.get(date_str, [])) == 0:
            return # Ignora clique em dia fechado

        self.instance.selected_date_index = index
        await self._build_calendar() # Reconstrói para mudar a cor da seleção
        
        self._update_shifts_display(date_str) 

    def _update_shifts_display(self, date_str):
        """Mostra apenas os turnos retornados pelo backend para aquele dia"""
        turnos_disponiveis = self.availability_map.get(date_str, [])
        
        self.instance.shifts_row.controls.clear()
        
        if not turnos_disponiveis:
             self.instance.shifts_row.controls.append(
                 ft.Text("Nenhum horário disponível", color=AppColors.GRAY_LIGHT2)
             )
        else:
            # Mapeamento de Nome do Backend -> Ícone e Horário
            info_turnos = {
                "Manhã": {"horario": "08:00 - 12:00", "icon": ft.icons.SUNNY},
                "Tarde": {"horario": "13:00 - 18:00", "icon": ft.icons.WB_TWILIGHT},
                "Noite": {"horario": "18:00 - 22:00", "icon": ft.icons.NIGHTLIGHT_ROUND}
            }
            
            for nome_turno in turnos_disponiveis:
                # Verifica se o turno retornado existe no nosso mapa (segurança)
                dados = info_turnos.get(nome_turno)
                if dados:
                    card = self._create_shift_card(nome_turno, dados["horario"], dados["icon"])
                    self.instance.shifts_row.controls.append(card)
        
        self.page.update()        

    def _create_shift_card(self, title, time_range, icon):
        return ft.Container(
            expand=True,
            bgcolor=AppColors.BACKGROUND_DARK,
            border_radius=15,
            padding=ft.Padding.all(15),
            on_click=lambda e: self.open_phone_input(title),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, color=AppColors.ORANGE_DARK, size=30),
                    ft.Text(title, weight="bold", size=16),
                    ft.Text(time_range, size=12, color=AppColors.GRAY_LIGHT2)
                ]
            )
        )    

    def open_phone_input(self, shift_name):
        self.instance.selected_shift = shift_name
        self.page.show_dialog(self.instance.bottom_sheet)

    def close_sheet(self, e):
        self.page.pop_dialog()
        self.page.show_dialog(
            ft.SnackBar(
                ft.Text(
                    f"Agendado para {self.instance.selected_shift}, aguardando aprovação!"
                ), 
            bgcolor=AppColors.ORANGE_DARK
            )
        ) 
        self.page.update()    