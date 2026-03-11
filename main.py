# main.py
#id do cliente 184100860737-52caf580q16d4ht8hgkl7ak8p7dr92js.apps.googleusercontent.com
#chave secreta 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
import traceback
import flet as ft
import flet.fastapi as flet_fastapi
from view.loginview import LoginView
from view.accountview import AccountView
from view.mainview import MainView
from view.professionalview import ProfessionalView
from view.productview import ProductView
from view.serviceview import ServiceView
from view.clientview import ClientView
from view.agendaview import AgendaView
from view.agendaturnosview import AgendaTurnosView
from view.anamneseview import AnamneseView
from view.anamnese_response import AnamneseResponse
from view.despesasview import DespesasView
from view.estudioview import EstudioView
from view.siteview import SiteView
import asyncio
from urllib.parse import urlparse

async def main(page: ft.Page):
    page.title = "App.Inkers"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.wasm = True    
    page.pwa = True
    #page.platform_brightness()

    def view_pop(view):
        page.views.pop() 
        top_view = page.views[-1] 
        page.go(top_view.route) 


    async def route_change(e=None):
        page.views.clear()
        troute = ft.TemplateRoute(page.route)

        url = page.url

        parsed_url = urlparse(url)

        DominioCompleto = parsed_url.netloc.split(":")[0]

        SubDominio = ""

        if DominioCompleto and ".inkers.com.br" in DominioCompleto:
            SubDominio = DominioCompleto.split(".")[0]

        try:
            if SubDominio == 'app' or SubDominio == 'devs' or SubDominio == 'dev':
                if troute.match("/"):
                    page.views.append(LoginView(page))
                elif troute.match("/account"):
                    page.views.append(AccountView(page)) 
                elif troute.match("/main"):
                    page.views.append(MainView(page))     
                elif troute.match("/professional"):   
                    page.views.append(ProfessionalView(page)) 
                elif troute.match("/product"):   
                    page.views.append(ProductView(page))    
                elif troute.match("/services"):   
                    page.views.append(ServiceView(page))   
                elif troute.match("/clients"):
                    page.views.append(ClientView(page))
                elif troute.match("/agenda"):
                    page.views.append(AgendaView(page))               
                elif troute.match("/anamnese/:name/:tel"):
                    page.views.append(AnamneseView(page, troute.name, troute.tel))         
                elif troute.match("/anamneseresponse"):                                  
                    page.views.append(AnamneseResponse())
                elif troute.match("/despesas"):
                    page.views.append(DespesasView(page))    
                elif troute.match("/agendaturnos"):
                    page.views.append(AgendaTurnosView(page))  
                elif troute.match("/site"):
                    page.views.append(SiteView(page))
                           
            else:
                page.views.append(EstudioView(page=page, name=SubDominio))

            page.update()

        except Exception as e:  
            print("ERRO FATAL NA VIEW:")
            traceback.print_exc()


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    #page.go("/")
    await route_change("/")        

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", port=8087, view=ft.AppView.WEB_BROWSER)
else:
    app = ft.app(target=main, assets_dir="assets", export_asgi_app=True)

