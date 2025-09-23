# main.py

import flet as ft
from view.loginview import LoginView
from view.accountview import AccountView
from view.mainview import MainView
from view.professionalview import ProfessionalView
from view.productview import ProductView
from view.serviceview import ServiceView
from view.clientview import ClientView

def main(page: ft.Page):
    # Configurações iniciais da página/janela
    page.title = "CaixaCerto"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    #page.window_width = 500
    #page.window_height = 700    

    # Adicionar o caminho para os assets (logo)
    page.assets_dir = "assets"
    page.update()

    mainview = MainView(page)


    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(LoginView(page))
        elif page.route == "/account":
            page.views.append(AccountView(page)) 
        elif page.route == "/main":
            page.views.append(mainview)     
        elif page.route == "/professional":   
            page.views.append(ProfessionalView(page)) 
        elif page.route == "/product":   
            page.views.append(ProductView(page))    
        elif page.route == "/services":   
            page.views.append(ServiceView(page))   
        elif page.route == "/clients":
            page.views.append(ClientView(page))                        

        page.update()

    page.on_route_change = route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")