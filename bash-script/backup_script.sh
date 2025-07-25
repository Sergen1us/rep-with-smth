#!/bin/bash

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "Использование: $0 <путь_к_директории>"
    exit 1
fi

SOURCE_DIR="$1"

# Проверка существования директории
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Ошибка: Директория $SOURCE_DIR не существует"
    exit 1
fi

# Создание директории для бэкапов
BACKUP_DIR="/backup"
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR" 2>/dev/null || BACKUP_DIR="/tmp/backup"
    mkdir -p "$BACKUP_DIR"
fi

# Создание имени архива
DIR_NAME=$(basename "$SOURCE_DIR")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="${DIR_NAME}_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="$BACKUP_DIR/$ARCHIVE_NAME"

# Логирование
echo "[$(date)] Начало бэкапа: $SOURCE_DIR" >> /var/log/backup.log 2>/dev/null || echo "[$(date)] Начало бэкапа: $SOURCE_DIR"

# Создание архива
if tar -czf "$ARCHIVE_PATH" -C "$(dirname "$SOURCE_DIR")" "$DIR_NAME"; then
    echo "[$(date)] Архив создан: $ARCHIVE_PATH" >> /var/log/backup.log 2>/dev/null || echo "Архив создан: $ARCHIVE_PATH"
    
    # Удаление старых архивов (>7 дней)
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +7 -delete 2>/dev/null
    
    echo "[$(date)] Бэкап завершен успешно" >> /var/log/backup.log 2>/dev/null || echo "Бэкап завершен успешно"
else
    echo "[$(date)] Ошибка создания архива" >> /var/log/backup.log 2>/dev/null || echo "Ошибка создания архива"
    exit 1
fi