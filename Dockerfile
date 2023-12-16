# Используем базовый образ Python
FROM python:3.11.5

# Устанавливаем рабочую директорию внутри контейнера
# COPY . /test_task_product_manager/  # Это можно заменить на COPY . /, т.к. WORKDIR уже установил текущую рабочую директорию
WORKDIR /test_task_product_manager

# Устанавливаем Python в небуферизованный режим (отправляет данные сразу в консоль вместо ожидания заверешения приложения)
ENV PYTHONUNBUFFERED 1

# Копируем зависимости в контейнер
COPY requirements.txt .

# Выводим список файлов в директории (отладка)
RUN ls -l

# Выводим содержимое requirements.txt (отладка)
RUN cat requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы в контейнер
COPY . .

# Устанавливаем переменные окружения
ENV DJANGO_SETTINGS_MODULE=test_task_product_manager.settings

# Применяем миграции Django
RUN python manage.py migrate

# Открываем порт 8000
EXPOSE 8000

# Запускаем Django приложение
CMD ["python", "manage.py", "runsslserver", "0.0.0.0:8000"]