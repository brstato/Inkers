import flet as ft

async def main(page: ft.Page):
    print("Has client_storage?", hasattr(page, "client_storage"))

ft.app(main)
