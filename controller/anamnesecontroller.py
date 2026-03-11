import flet as ft
from model.anamnesemodel import AnamneseModel
from controller.call_api import ProtectedApiCall
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from model.dto import AnamneseDTO
import time
import os
from datetime import datetime
import json


class AnamneseController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.instance = instance
        self.model = AnamneseModel()
        self.init_time = time.time()

    def validate_birth_date(self, date_str):
        """Valida se a data está em formato válido e é uma data válida, e normaliza para DD/MM/YYYY"""
        if not date_str or date_str.strip() == '':
            return False, "Data de nascimento é obrigatória"
        
        date_str = date_str.strip()
        
        # Remove todos os caracteres não numéricos para contar dígitos
        digits_only = ''.join(filter(str.isdigit, date_str))
        
        # Se não tem exatamente 8 dígitos, tenta formatos com separadores
        if len(digits_only) != 8:
            # Tenta formatos com separadores
            formats_to_try = [
                '%d/%m/%Y',  # DD/MM/AAAA
                '%d-%m-%Y',  # DD-MM-AAAA
                '%d.%m.%Y',  # DD.MM.AAAA
                '%d %m %Y',  # DD MM AAAA
            ]
            
            parsed_date = None
            for fmt in formats_to_try:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date is None:
                return False, "Formato de data inválido. Use DD/MM/AAAA, DD-MM-AAAA, DD.MM.AAAA ou DDMMAAAA"
        else:
            # Tem 8 dígitos - formato DDMMAAAA
            try:
                day = int(digits_only[:2])
                month = int(digits_only[2:4])
                year = int(digits_only[4:])
                parsed_date = datetime(year, month, day)
                
                # Se chegou aqui, a data é válida, então normaliza para DD/MM/YYYY
                normalized_date = parsed_date.strftime('%d/%m/%Y')
                # Atualiza o campo com o formato padronizado
                self.instance.nascimento_input.value = normalized_date
                self.instance.nascimento_input.update()
                
            except (ValueError, IndexError):
                return False, "Data inválida. Verifique o dia, mês e ano"
        
        # Aqui parsed_date já foi definido
        # Verifica se não é uma data futura
        today = datetime.now()
        if parsed_date > today:
            return False, "Data de nascimento não pode ser no futuro"
        
        # Verifica se não é muito antiga (mais de 150 anos)
        if parsed_date.year < (today.year - 150):
            return False, "Data de nascimento inválida"
        
        # Verifica se não é muito recente (menos de 1 ano)
        if parsed_date > today.replace(year=today.year - 1):
            return False, "Data de nascimento deve ser de pelo menos 1 ano atrás"
            
        return True, ""
    

    def validate_fields(self):
        error_found:bool = False
            
        if self.instance.signature_pad.is_empty():
            self.page.show_dialog(ft.SnackBar(ft.Text("Você deve assinar o documento para prosseguir.")))
            self.page.update()
            return False

        validation_map = [
                    {
                        'control': self.instance.nome_input, 
                        'msg': "Nome é obrigatório"
                    },

                    {
                        'control': self.instance.telefone_input, 
                        'msg': "Telefone é obrigatório"
                    },
                    
                    {
                        'control': self.instance.nascimento_input, 
                        'msg': "Data de nascimento é obrigatória"
                    },
                    
                    {
                        'control': self.instance.profissao_input, 
                        'msg': "Profissão é obrigatória"
                    },
                    
                    {
                        'control': self.instance.origem_dropdown, 
                        'msg': "Selecione uma opção de como conheceu o estúdio"
                    },
                    
                    {
                        'control': self.instance.esporte_input, 
                        'msg': "Informe qual esporte", 
                        'check_if': self.instance.esporte_switch.value
                    },
                    {
                        'control': self.instance.problema_pele_input, 
                        'msg': "Informe o problema de pele", 
                        'check_if': self.instance.problema_pele_switch.value
                    },
                    {
                        'control': self.instance.doenca_transmissivel_input, 
                        'msg': "Informe a doença", 
                        'check_if': self.instance.doenca_transmissivel_switch.value
                    },
                    {
                        'control': self.instance.alergias_input, 
                        'msg': "Informe a alergia", 
                        'check_if': self.instance.alergia_switch.value
                    },
                    {
                        'control': self.instance.medicamentos_input, 
                        'msg': "Informe o medicamento", 
                        'check_if': self.instance.medicamento_switch.value
                    },
                    {
                        'control': self.instance.profissional_dropdown, 
                        'msg': "Selecione o profissional"
                    },
                ]
        
        for item in validation_map:
            control = item['control']
            should_check = item.get('check_if', True)
            control.error_text = None
            if should_check and (control.value is None or control.value == ''):
                control.error_text = item['msg']
                error_found = True
                error_key_field = control.key
                control.update()
                break
                             

        if error_found:
            self.page.show_dialog(ft.SnackBar(ft.Text(control.error_text)))       
            self.page.update()
            return False
        
        # Validação específica da data de nascimento
        is_valid_date, date_error = self.validate_birth_date(self.instance.nascimento_input.value)
        if not is_valid_date:
            self.instance.nascimento_input.error_text = date_error
            self.instance.nascimento_input.update()
            self.page.show_dialog(ft.SnackBar(ft.Text(date_error)))
            self.page.update()
            return False

        # Honeypot Check
        if self.instance.honeypot.value:
            # Silently fail or generic error.
            print("Bot detected: Honeypot filled")
            return False

        # Time Check (Minimum 5 seconds)
        if time.time() - self.init_time < 5:
            self.page.show_dialog(ft.SnackBar(ft.Text("Por favor, preencha o formulário com calma."))) 
            self.page.update()
            return False
        
        return True


    async def get_data(self):
        response = await self.model.list_profissionais(self.instance.tel)
        if response.status_code == 200:
            self.instance.profissional_options.clear()
            data = json.loads(response.content)
            for item in data:
                self.instance.profissional_options.append(
                    ft.dropdown.Option(key=item['id'], text=item['nome'])
                )   
            self.instance.profissional_dropdown.options = self.instance.profissional_options
            self.instance.profissional_dropdown.update()
                 

    async def create_anamnese(self, e):

        if not self.validate_fields():
            return
        self.page.pop_dialog()
        self.instance.progress_ring.visible = True
        self.page.update()  

        if not self.instance.signature_pad.is_empty():
            arquivo:str = f'sig_{int(time.time())}.png'

            caminho:str = os.path.join('/tmp', arquivo)      

        assinatura_base64:str = self.instance.signature_pad.export_to_base64()

        def sim_nao(valor):
            return "Sim" if valor else "Não"

        def v(val):
            return val if val is not None else ''

        dto = AnamneseDTO(
            profissao             = v(self.instance.profissao_input.value),
            como_conheceu         = v(self.instance.origem_dropdown.value),
            consumo               = v(self.instance.experiencia_radio.value),
            
            pratica_esporte       = sim_nao(self.instance.esporte_switch.value), 
            qual_esporte          = v(self.instance.esporte_input.value),
            diabetico             = sim_nao(self.instance.diabetes_switch.value),
            hipertenso            = sim_nao(self.instance.hipertenso_switch.value),
            hemofilico            = sim_nao(self.instance.hemofilico_switch.value),
            problema_de_pele      = sim_nao(self.instance.problema_pele_switch.value),
            qual_problema_de_pele = v(self.instance.problema_pele_input.value),
            gestante_amamentando  = sim_nao(self.instance.gestante_switch.value),
            alcool_drogas         = sim_nao(self.instance.drogas_switch.value),
            doenca_transmissivel  = sim_nao(self.instance.doenca_transmissivel_switch.value),       
            qual_doenca           = v(self.instance.doenca_transmissivel_input.value),
            alergia               = sim_nao(self.instance.alergia_switch.value),
            qual_alergia          = v(self.instance.alergias_input.value),
            medicamento           = sim_nao(self.instance.medicamento_switch.value),
            qual_medicamento      = v(self.instance.medicamentos_input.value),
            concorda_com_termos   = sim_nao(self.instance.termo_check.value),
            gosto_piercing        = sim_nao(self.instance.piercings_switch.value),
            gosto_tatuagem        = sim_nao(self.instance.tatuagem_switch.value),
            
            estilo_tatuagem       = v(self.instance.estilo_tatuagem_dropdown.value),
            nome                  = v(self.instance.nome_input.value),
            insta                 = v(self.instance.instagram_input.value),
            assinatura            = assinatura_base64,
            telefone              = v(self.instance.telefone_input.value),
            data_nascimento       = v(self.instance.nascimento_input.value),
            telefone_estudio      = v(self.instance.tel),
            nome_estudio          = v(self.instance.name),
            id_profissional       = v(self.instance.profissional_dropdown.value)
        )
 
        response = await self.model.CreateAnamnese(dto)

        if response.status_code == 200:
            self.page.go("/anamneseresponse")


    def selected_medicamento(self, e):
        if self.instance.medicamento_switch.value == False:
            self.instance.medicamentos_input.visible = False
        else:    
            self.instance.medicamentos_input.visible = True
        self.page.update()    


    def selected_alergia(self, e):
        if self.instance.alergia_switch.value == False:
            self.instance.alergias_input.visible = False
        else:    
            self.instance.alergias_input.visible = True
        self.page.update()           


    def selected_doenca(self, e):
        if self.instance.doenca_transmissivel_switch.value == False:
            self.instance.doenca_transmissivel_input.visible = False
        else:    
            self.instance.doenca_transmissivel_input.visible = True
        self.page.update()         


    def selected_problema_de_pele(self, e):
        if self.instance.problema_pele_switch.value == False:
            self.instance.problema_pele_input.visible = False
        else:    
            self.instance.problema_pele_input.visible = True
        self.page.update()      


    def selected_problema_esporte(self, e):
        if self.instance.esporte_switch.value == False:
            self.instance.esporte_input.visible = False
        else:    
            self.instance.esporte_input.visible = True
        self.page.update()            


    def selected_estilo_tatuagem(self, e):
        if self.instance.tatuagem_switch.value == False:
            self.instance.estilo_tatuagem_dropdown.visible = False
        else:    
            self.instance.estilo_tatuagem_dropdown.visible = True
        self.page.update()  


    def cancel_signature(self, e):
        self.instance.signature_pad.clear()
        self.page.pop_dialog()
        self.instance.termo_check.value = False
        self.page.update()


    def selected_confirm_terms(self, e):
               
        if self.instance.termo_check.value == False:
            #self.instance.signature_pad.visible = False
            self.page.pop_dialog()
        else:    
            self.instance.signature_pad.visible = True
            #self.instance.scroll_to(key="signature_area", duration=1000)
            self.page.show_dialog(self.instance.dialog_signature)
        self.page.update() 


    def selected_birth_date(self, e):
        self.instance.nascimento_input.value = self.instance.nascimento_calendar.value.strftime("%d/%m/%Y")
        self.page.update()        