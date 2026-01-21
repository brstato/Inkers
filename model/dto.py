from dataclasses import dataclass, asdict

@dataclass(slots=True)
class AnamneseDTO:
    profissao: str
    como_conheceu: str
    consumo: str
    pratica_esporte: str
    qual_esporte: str
    diabetico: str
    hipertenso: str
    hemofilico: str
    problema_de_pele: str
    qual_problema_de_pele: str
    gestante_amamentando: str
    alcool_drogas: str
    doenca_transmissivel: str
    qual_doenca: str
    alergia: str
    qual_alergia: str
    medicamento: str
    qual_medicamento: str
    concorda_com_termos: str
    gosto_piercing: str
    gosto_tatuagem: str
    estilo_tatuagem: str
    nome: str
    insta: str
    assinatura: str
    telefone: str
    data_nascimento: str
    telefone_estudio: str
    nome_estudio:str


    def to_dict(self):
        return asdict(self)