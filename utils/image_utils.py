import flet as ft
import asyncio
import os
import io
import base64
from PIL import Image

async def pick_file_base64(page: ft.Page, allowed_extensions=["png", "jpg", "jpeg", "webp"]):
    """
    Picks a file using FilePicker, uploads it locally to the 'uploads' folder,
    reads it as a base64 string, and then deletes the local file.
    
    Returns:
        tuple: (base64_string, file_name) or (None, None) if cancelled or failed.
    """
    upload_done = asyncio.Event()
    file_info = {"name": None, "base64": None, "error": None}

    async def on_upload_local(e: ft.FilePickerUploadEvent):
        if getattr(e, 'progress', 0) == 1.0:
            upload_done.set()
        elif getattr(e, 'error', None):
            file_info["error"] = e.error
            upload_done.set()

    picker = ft.FilePicker(on_upload=on_upload_local)

    try:
        files = await picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=allowed_extensions
        )

        if not files:
            return None, None

        file = files[0]
        file_info["name"] = file.name
        
        # Ensure uploads directory exists
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        upload_url = page.get_upload_url(file.name, 60)
        
        await picker.upload([
            ft.FilePickerUploadFile(
                name=file.name,
                upload_url=upload_url
            )
        ])

        await upload_done.wait()

        if file_info["error"]:
            print(f"Error during local upload: {file_info['error']}")
            return None, None

        file_path = os.path.join("uploads", file.name)
        
        if os.path.exists(file_path):
            with Image.open(file_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                file_info["base64"] = base64.b64encode(buffer.getvalue()).decode("utf-8")
            os.remove(file_path)

            if '.' in file_info["name"]:
                nome_sem_extensao = file_info["name"].rsplit('.', 1)[0]
                file_info["name"] = f"{nome_sem_extensao}.jpg"
            else:
                file_info["name"] = f"{file_info['name']}.jpg"                

        return file_info["base64"], file_info["name"]

    except Exception as ex:
        print(f"Error in pick_file_base64: {ex}")
        return None, None
    finally:
        if picker in page.overlay:
            page.overlay.remove(picker)
            page.update()
