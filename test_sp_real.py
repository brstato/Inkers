import flet as ft

async def main(page: ft.Page):
    async def task():
        try:
            await ft.SharedPreferences().set("test", "123")
            v = await ft.SharedPreferences().get("test")
            print("VALUE:", v)
        except Exception as e:
            print("ERROR IN TASK:", e)
    
    page.run_task(task)

ft.app(main)
