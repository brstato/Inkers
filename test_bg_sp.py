import flet as ft
import asyncio

async def main(page: ft.Page):
    async def bg_task():
        try:
            val = await ft.SharedPreferences().get("test")
            print("bg_task val:", val)
        except Exception as e:
            print("bg_task error:", e)
    
    page.run_task(bg_task)
    
ft.app(main)
