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
from view.portfolioview import PortfolioView
import asyncio
from urllib.parse import urlparse

APP_ID_ONESIGNAL = "77e0ed01-8f73-4091-8870-6561dd849c44"

async def main(page: ft.Page):
    page.title = "App.Inkers"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.wasm = True    
    page.pwa = True
    js_inicializacao = f"""
    javascript:(function(){{
        if(!document.getElementById('os-script')){{
            var s=document.createElement('script');
            s.id='os-script';
            s.src='https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js';
            s.defer=true;
            document.head.appendChild(s);
            
            window.OneSignalDeferred = window.OneSignalDeferred || [];
            window.OneSignalDeferred.push(async function(OS) {{
                await OS.init({{ appId: '{APP_ID_ONESIGNAL}' }});
                OS.Slidedown.promptPush();
            }});
        }}
    }})();
    """
    await page.launch_url(js_inicializacao.strip())
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
                elif troute.match("/portfolio"):
                    page.views.append(PortfolioView(page))
                           
            page.update()

        except Exception as e:  
            print("ERRO FATAL NA VIEW:")
            traceback.print_exc()


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    #page.go("/")
    await route_change("/")        

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", upload_dir="uploads")
else:
    app = ft.app(target=main, assets_dir="assets", upload_dir="uploads", export_asgi_app=True)

