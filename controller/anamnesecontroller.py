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

    async def get_data(self):
        self.instance.token   = await self.page.client_storage.get_async("token"  )
        self.instance.r_token = await self.page.client_storage.get_async("r_token")  


    async def create_anamnese(self, e):

        if not self.instance.signature_pad.is_empty():
            arquivo:str = f'sig_{int(time.time())}.png'

            caminho:str = os.path.join('/tmp', arquivo)

            # try:
            #     width, height = 400, 200
            #     image = Image.new("RGB", (width, height), "white")
            #     draw = ImageDraw.Draw(image)

            #     for stroke in self.instance.signature_pad.draw_data:
            #         if len(stroke) > 1:
            #             draw.line(stroke, fill="black", width=3)
            #         else:
            #             x, y = stroke[0]
            #             r = 1.5
            #             draw.ellipse((x-r, y-r, x+r, y+r), fill="black")
            #     image.save(caminho, format="PNG")
                                
            #     # CRÍTICO: Dá permissão para o Delphi/WKHTML lerem
            #     os.chmod(caminho, 0o777)
                
            # except Exception as ex:
            #     print(f"Erro ao salvar assinatura: {ex}")
            #     caminho = "" # Falhou, vai sem assinatura       

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
            id_loja_ex            = self.instance.id_loja,
            assinatura            = assinatura_base64,
            telefone              = self.instance.telefone_input.value,
            data_nascimento       = self.instance.nascimento_input.value                 
        )
 
        await ProtectedApiCall(
            self.page,
            self.instance,
            self.model.CreateAnamnese,
            dados=dto
        ).call_api_refresh_token()


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


    def selected_confirm_terms(self, e):
        if self.instance.termo_check.value == False:
            self.instance.signature_pad.visible = False
        else:    
            self.instance.signature_pad.visible = True
            self.instance.scroll_to(key="signature_area", duration=1000)
        self.page.update() 


    def selected_birth_date(self, e):
        self.instance.nascimento_input.value = self.instance.nascimento_calendar.value.strftime("%d/%m/%Y")
        self.page.update()        