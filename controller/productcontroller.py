import flet as ft
from view.controls.custoncard import CustonCard
from view.controls.custondialog import CustonDialog
from model.loginmodel import LoginModel
from utils.formatcurr import formatar_moeda_brasileira
from model.productmodel import ProductModel
import json
import asyncio

class ProductController:
    def __init__(self, page: ft.Page, instance):
        self.id_prof:int 
        self.instance = instance
        self.page    = page
        self.model   = ProductModel()

        self.dialog  = None    
        
        self.id_loja = self.instance.id_loja
        self.token   = self.instance.token
        self.r_token = self.instance.r_token
  


    async def createProduct(self, e):

        self.page.pop_dialog(self.instance.modalviewCreateProduct)
        
        self.instance.progressRing.visible = True
        self.page.update()          

        response = await self.model.createProductData(
            self.instance.edtNome.value,
            self.instance.infvalor.value, 
            self.instance.insumo.value,   
            self.instance.id_loja,         
            self.instance.Comissionado.value,
            self.instance.edtValcusto.value,
            self.instance.edtValVenda.value,
            self.instance.edtEstoque.value,
            self.instance.edtMEstoque.value,        
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")          

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.createProductData(
                    self.instance.edtNome.value,
                    self.instance.infvalor.value, 
                    self.instance.insumo.value,   
                    self.instance.id_loja,         
                    self.instance.Comissionado.value,
                    self.instance.edtValcusto.value,
                    self.instance.edtValVenda.value,
                    self.instance.edtEstoque.value,
                    self.instance.edtMEstoque.value,        
                    self.instance.token
                )          

        self.instance.progressRing.visible = False
        self.page.update()   
        await self.listProductData()  


    async def editProduct(self, e):

        self.page.pop_dialog()
        
        self.instance.progressRing.visible = True
        self.page.update() 

        response = await self.model.editProductData(
            self.instance.id_prod,
            self.instance.edtNome.value,
            self.instance.infvalor.value, 
            self.instance.insumo.value,            
            self.instance.Comissionado.value,
            self.instance.edtValcusto.value,
            self.instance.edtValVenda.value,
            self.instance.edtEstoque.value,
            self.instance.edtMEstoque.value,        
            self.instance.token
        )

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
            await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await ft.SharedPreferences().get("token")
            self.instance.r_token = await ft.SharedPreferences().get("r_token")

            if response.status_code != 200:
                self.page.go("/")

            else:
                await self.model.editProductData(
                    self.instance.id_prod,
                    self.instance.edtNome.value,
                    self.instance.infvalor.value, 
                    self.instance.insumo.value,            
                    self.instance.Comissionado.value,
                    self.instance.edtValcusto.value,
                    self.instance.edtValVenda.value,
                    self.instance.edtEstoque.value,
                    self.instance.edtMEstoque.value,        
                    self.instance.token
                )

        self.id_prod = 0

        self.instance.progressRing.visible = False
        self.page.update()  

        await self.listProductData()        



    async def deleteProduct(self, id_prof):

        self.instance.progressRing.visible = True
        self.page.update()        

        response = await self.model.deleteProductData(id_prof, self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:
                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])   

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                await self.model.deleteProductData(id_prof, self.instance.token)
            else:
                self.page.go("/")    

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listProductData()



    async def listProductData(self):
        if not self.instance.token or not self.instance.id_loja:    
            self.page.go("/")
            self.page.update()
            return

        self.instance.progressRing.visible = True
        self.page.update()

        response = await self.model.getProductData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.getProductData(self.instance.id_loja, self.instance.token)

                self.page.update()
            else:    
                self.page.go("/login")

        elif response.status_code == 200:
            
            array = json.loads(response.content)["message"]

            self.instance.list.controls.clear()

            for item in array:
                name      = item["nome"       ]
                v_custo   = item["valor_custo"]
                v_venda   = item["valor_venda"]
                v_vendido = item["vendas"     ]
                id_prod   = item["id"         ]
                margem    = item["margem"     ]
                estoque   = item["qt_estoque" ]
                m_estoque = item["min_estoque"]

                card = CustonCard(
                    page=self.page,
                    width=self.instance.width,
                    icon=ft.Icons.CATEGORY,
                    title=name,
                    desc=f'Custo: {formatar_moeda_brasileira(v_custo)} | Venda: {formatar_moeda_brasileira(v_venda)}',
                    sub_desc=f'Margem: {margem}%, Vendido: {formatar_moeda_brasileira(v_vendido)}',
                    detail=f'Estoque: {estoque} | Min.: {m_estoque}',
                    id=id_prod,
                    callback=lambda id_prod: self.deleteProduct(id_prod),
                    tap=self.instance.list.on_card_selected,
                    callback2=lambda id_prod:self.open_modal_view_detail(id_prod)
                )

                self.instance.list.controls.append(card) 
            
            #self.page.update()

        self.instance.progressRing.visible = False
        self.page.update()    




    async def open_modal_view_detail(self, id):
        self.instance.id_prod = id        
        response = await self.model.DetailProductData(id=id, token=self.instance.token)

        if response.status_code != 200:
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await ft.SharedPreferences().set("token", json.loads(response.content)["token"])
                await ft.SharedPreferences().set("r_token", json.load(response.content)["r_token"])

                self.instance.token = await ft.SharedPreferences().get("token")
                self.instance.r_token = await ft.SharedPreferences().get("r_token")

                response = await self.model.DetailProductData(id=id, token=self.instance.token)
            else:    
                self.page.go("/login")                

        elif response.status_code == 200:
            data = json.loads(response.content)
            
            self.instance.edtValcusto.value  = formatar_moeda_brasileira(data.get("valor_custo", 0))
            self.instance.edtValVenda.value  = formatar_moeda_brasileira(data.get("valor_venda", 0))
            self.instance.edtNome.value      = data.get("nome", "")
            self.instance.edtEstoque.value   = str(data.get("estoque", 0))
            self.instance.edtMEstoque.value  = str(data.get("min_estoque", 0))
            
            # Converter para booleano corretamente
            inf_valor = data.get("inf_valor", False)
            insumo = data.get("insumo", False)
            comissionado = data.get("comissionado", False)
            
            # Se for string, converter para booleano
            self.instance.infvalor.value = bool(inf_valor) if isinstance(inf_valor, bool) else str(inf_valor).lower() == "true"
            self.instance.insumo.value = bool(insumo) if isinstance(insumo, bool) else str(insumo).lower() == "true"
            self.instance.Comissionado.value = bool(comissionado) if isinstance(comissionado, bool) else str(comissionado).lower() == "true"

            self.page.show_dialog(self.instance.modalview)

        self.page.update()    
