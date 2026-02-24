FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-dev

COPY src ./src

ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]
