import flet as ft
import asyncio

async def main(page: ft.Page):
    async def task():
        try:
            await page.client_storage.set_async("test", "456")
            v = await page.client_storage.get_async("test")
            print("CLIENT STORAGE:", v)
            
            await ft.SharedPreferences().set("test2", "789")
            v2 = await ft.SharedPreferences().get("test2")
            print("SHARED PREFS:", v2)
        except Exception as e:
            print("ERROR:", e)
    
    page.run_task(task)

ft.app(main, view=ft.AppView.WEB_BROWSER, port=8089)
