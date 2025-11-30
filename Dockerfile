FROM python:3.9-slim

# Эти переменные ускоряют Python в контейнере и делают логи читаемыми
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем только зависимости (для кэширования слоев Docker)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь остальной код проекта
COPY . .

# Открываем порт (это больше для документации, но полезно)
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]