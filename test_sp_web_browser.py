import flet as ft

async def main(page: ft.Page):
    try:
        await ft.SharedPreferences().set("test", "123")
        page.add(ft.Text("OK!"))
    except Exception as e:
        page.add(ft.Text(f"ERROR: {e}"))

ft.app(target=main)
