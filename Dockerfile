FROM python:3.9

WORKDIR /app

# Копирование содержимого текущей директории внутрь контейнера
COPY ./requirements.txt .

# Установка зависимостей из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Запуск скрипта checkerV5.py
CMD ["python", "checkerV5.py"]