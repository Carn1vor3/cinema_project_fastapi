FROM python:3.12-slim

WORKDIR /app

# Встановлюємо Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Копіюємо конфіги для кешування
COPY pyproject.toml poetry.lock* /app/

# Встановлюємо залежності глобально, без virtualenv
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копіюємо весь код
COPY . /app

# Запуск uvicorn глобально
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
