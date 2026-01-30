# main.py
#id do cliente 184100860737-52caf580q16d4ht8hgkl7ak8p7dr92js.apps.googleusercontent.com
#chave secreta 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
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
from view.anamneseview import AnamneseView
from view.anamnese_response import AnamneseResponse

async def main(page: ft.Page):
    # mudanca no projeto para InkedApp
    # Configurações iniciais da página/janela
    page.title = "InkedApp"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    #mainview = MainView(page)


    async def route_change(route):
        page.views.clear()

        troute = ft.TemplateRoute(page.route)

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

        page.update()

    page.on_route_change = route_change
    page.go(page.route)
    #page.go("/")

#if __name__ == "__main__":
#    ft.app(target=main, assets_dir="assets", port=8086)
app = ft.app(target=main, assets_dir="assets", export_asgi_app=True)

