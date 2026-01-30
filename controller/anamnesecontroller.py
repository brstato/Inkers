import flet as ft
from model.anamnesemodel import AnamneseModel
from controller.call_api import ProtectedApiCall
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from model.dto import AnamneseDTO
import time
import os


class AnamneseController:
    def __init__(self, page: ft.Page, instance):
        self.page = page
        self.instance = instance
        self.model = AnamneseModel()

    def validate_fields(self):
        error_found:bool = False
            
        if self.instance.signature_pad.is_empty():
            self.page.open(ft.SnackBar(ft.Text("Você deve assinar o documento para prosseguir.")))
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
            self.page.open(ft.SnackBar(ft.Text(control.error_text)))       
            self.page.update()
            return False
        return True


    async def get_data(self):
        self.instance.token   = await ft.SharedPreferences().get("token"  )
        self.instance.r_token = await ft.SharedPreferences().get("r_token")  


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

        dto = AnamneseDTO(
            profissao             = self.instance.profissao_input.value,
            como_conheceu         = self.instance.origem_dropdown.value,
            consumo               = self.instance.experiencia_radio.value,
            
            pratica_esporte       = sim_nao(self.instance.esporte_switch.value), 
            qual_esporte          = self.instance.esporte_input.value,
            diabetico             = sim_nao(self.instance.diabetes_switch.value),
            hipertenso            = sim_nao(self.instance.hipertenso_switch.value),
            hemofilico            = sim_nao(self.instance.hemofilico_switch.value),
            problema_de_pele      = sim_nao(self.instance.problema_pele_switch.value),
            qual_problema_de_pele = self.instance.problema_pele_input.value,
            gestante_amamentando  = sim_nao(self.instance.gestante_switch.value),
            alcool_drogas         = sim_nao(self.instance.drogas_switch.value),
            doenca_transmissivel  = sim_nao(self.instance.doenca_transmissivel_switch.value),       
            qual_doenca           = self.instance.doenca_transmissivel_input.value,
            alergia               = sim_nao(self.instance.alergia_switch.value),
            qual_alergia          = self.instance.alergias_input.value,
            medicamento           = sim_nao(self.instance.medicamento_switch.value),
            qual_medicamento      = self.instance.medicamentos_input.value,
            concorda_com_termos   = sim_nao(self.instance.termo_check.value),
            gosto_piercing        = sim_nao(self.instance.piercings_switch.value),
            gosto_tatuagem        = sim_nao(self.instance.tatuagem_switch.value),
            
            estilo_tatuagem       = self.instance.estilo_tatuagem_dropdown.value,
            nome                  = self.instance.nome_input.value,
            insta                 = self.instance.instagram_input.value,
            assinatura            = assinatura_base64,
            telefone              = self.instance.telefone_input.value,
            data_nascimento       = self.instance.nascimento_input.value,
            telefone_estudio      = self.instance.tel,
            nome_estudio          = self.instance.name
        )
 
        response = await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.CreateAnamnese,
            dados=dto
        ).call_api_refresh_token()

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