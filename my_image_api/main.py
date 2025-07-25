from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import os
import uuid
import logging

app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Папка для хранения изображений
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Максимальный размер файла (5 МБ)
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Имена файлов
ORIGINAL_FILENAME = "original_image"
PROCESSED_FILENAME = "processed_image.png"


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Загружает изображение (только JPEG и PNG).
    Отклоняет файлы размером более 5 МБ.
    """
    # Проверка расширения файла
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logging.warning("Недопустимое расширение файла: %s", file.filename)
        raise HTTPException(status_code=400, detail="Только файлы JPEG и PNG разрешены.")

    # Проверка MIME-типа
    if file.content_type not in ["image/jpeg", "image/png"]:
        logging.warning("Недопустимый формат файла: %s", file.content_type)
        raise HTTPException(status_code=400, detail="Только JPEG и PNG поддерживаются.")

    # Проверка размера файла
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        logging.warning("Файл слишком большой: %s байт", len(contents))
        raise HTTPException(status_code=400, detail="Файл превышает 5 МБ.")

    # Сохранение файла
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(IMAGE_DIR, ORIGINAL_FILENAME)
    with open(file_path, "wb") as f:
        f.write(contents)

    logging.info("Файл успешно загружен: %s", file.filename)
    return {"message": "Файл загружен успешно."}


@app.get("/process")
async def process_image():
    """
    Обрабатывает загруженное изображение и возвращает чёрно-белую версию.
    """
    input_path = os.path.join(IMAGE_DIR, ORIGINAL_FILENAME)
    output_path = os.path.join(IMAGE_DIR, PROCESSED_FILENAME)

    if not os.path.exists(input_path):
        logging.error("Исходное изображение не найдено.")
        raise HTTPException(status_code=404, detail="Сначала загрузите изображение.")

    try:
        image = Image.open(input_path)
        grayscale = image.convert("L")
        grayscale.save(output_path)
    except Exception as e:
        logging.error("Ошибка при обработке изображения: %s", str(e))
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения.")

    logging.info("Изображение успешно обработано и сохранено.")
    return FileResponse(output_path, media_type="image/png", filename=PROCESSED_FILENAME)