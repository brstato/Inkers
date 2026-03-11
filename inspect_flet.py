import flet as ft

print(f"Flet version: {ft.version.version if hasattr(ft, 'version') else 'unknown'}")
print(f"Has SharedPreferences: {hasattr(ft, 'SharedPreferences')}")
if hasattr(ft, 'SharedPreferences'):
    print(f"SharedPreferences type: {type(ft.SharedPreferences)}")
    print(f"SharedPreferences dir: {dir(ft.SharedPreferences)}")

print(f"Has client_storage on Page: {hasattr(ft.Page, 'client_storage')}")
