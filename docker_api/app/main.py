from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import os
import logging

app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Папка для изображений
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Константы
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Загрузка изображения"""
    
    # Проверка расширения
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Только JPEG и PNG")

    # Проверка размера
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл больше 5 МБ")

    # Сохранение файла
    file_path = os.path.join(IMAGE_DIR, "original_image")
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"message": "Файл загружен"}

@app.get("/process")
async def process_image():
    """Обработка изображения в чёрно-белое"""
    
    input_path = os.path.join(IMAGE_DIR, "original_image")
    output_path = os.path.join(IMAGE_DIR, "processed_image.png")

    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Загрузите изображение")

    try:
        image = Image.open(input_path)
        grayscale = image.convert("L")
        grayscale.save(output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка обработки")

    return FileResponse(output_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)