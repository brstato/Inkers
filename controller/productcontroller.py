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

        self.page.close(self.instance.modalviewCreateProduct)
        
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

            await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
            await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await self.page.client_storage.get_async("token")
            self.instance.r_token = await self.page.client_storage.get_async("r_token")          

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

        self.page.close(self.instance.modalview)
        
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

            await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
            await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

            self.instance.token = await self.page.client_storage.get_async("token")
            self.instance.r_token = await self.page.client_storage.get_async("r_token")

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
                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])   

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                await self.model.deleteProductData(id_prof, self.instance.token)
            else:
                self.page.go("/")    

        self.instance.progressRing.visible = False
        self.page.update()                              

        await self.listProductData()



    async def listProductData(self):

        self.instance.progressRing.visible = True
        self.page.update()

        response = await self.model.getProductData(self.instance.id_loja, self.instance.token)

        if response.status_code != 200:
            
            response = await LoginModel().refresh_token(self.instance.r_token, self.instance.id_loja)

            if response.status_code == 200:

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

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

                await self.page.client_storage.set_async("token", json.loads(response.content)["token"])
                await self.page.client_storage.set_async("r_token", json.load(response.content)["r_token"])

                self.instance.token = await self.page.client_storage.get_async("token")
                self.instance.r_token = await self.page.client_storage.get_async("r_token")

                response = await self.model.DetailProductData(id=id, token=self.instance.token)
            else:    
                self.page.go("/login")                

        elif response.status_code == 200:
            self.instance.edtValcusto.value  = formatar_moeda_brasileira(json.loads(response.content)["valor_custo"])
            self.instance.edtValVenda.value  = formatar_moeda_brasileira(json.loads(response.content)["valor_venda"])
            self.instance.edtNome.value      = json.loads(response.content)["nome"        ]
            self.instance.infvalor.value     = json.loads(response.content)["inf_valor"   ] 
            self.instance.insumo.value       = json.loads(response.content)["insumo"      ]            
            self.instance.Comissionado.value = json.loads(response.content)["comissionado"]
            self.instance.edtEstoque.value   = json.loads(response.content)["estoque"     ]
            self.instance.edtMEstoque.value  = json.loads(response.content)["min_estoque" ]

            self.page.open(self.instance.modalview)

        self.page.update()    
