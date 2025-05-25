import os
from io import BytesIO
import zipfile
from PIL import Image, UnidentifiedImageError
import requests


def save_image_from_url(url: str, folder="assets/images", filename="output", resize: tuple | None = None) -> bool:
    try:
        os.makedirs(folder, exist_ok=True)
        response = requests.get(url, timeout=10)
        content_type = response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            return False
        try:
            img = Image.open(BytesIO(response.content))
        except UnidentifiedImageError:
            return False
        if resize:
            img = img.resize(resize)
        ext = img.format.lower() if img.format else "jpg"
        filename = f"{filename}.{ext}"
        path = os.path.join(folder, filename)
        img.save(path)
        return True
    except Exception:
        return False


def resize_images(folder="assets/images", width=100, height=100) -> int:
    count = 0
    if not os.path.exists(folder):
        return 0
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isfile(path) and file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            try:
                img = Image.open(path)
                resized = img.resize((width, height), Image.LANCZOS)
                new_name = os.path.splitext(file)[0] + ".png"
                new_path = os.path.join(folder, new_name)
                resized.save(new_path, format="PNG")
                if new_path != path:
                    os.remove(path)
                count += 1
            except Exception:
                pass
    return count


def zip_folder(folder="assets/images", zip_path="images.zip") -> None:
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder)
                zipf.write(full_path, arcname)
