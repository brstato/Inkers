# main.py

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

def main(page: ft.Page):
    # Configurações iniciais da página/janela
    page.title = "InkedApp"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    mainview = MainView(page)


    def route_change(route):
        page.views.clear()

        troute = ft.TemplateRoute(page.route)

        if troute.match("/"):
            page.views.append(LoginView(page))
        elif troute.match("/account"):
            page.views.append(AccountView(page)) 
        elif troute.match("/main"):
            page.views.append(mainview)     
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
        elif troute.match("/anamnese/:id"):
            page.views.append(AnamneseView(page, troute.id))                                       

        page.update()

    page.on_route_change = route_change
    page.go("/anamnese/D5412312-87CF-46F3-B1E6-879241B1E40F")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
#app = ft.app(target=main, assets_dir="assets", export_asgi_app=True)
