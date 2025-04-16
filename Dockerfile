# syntax=docker/dockerfile:1-labs
FROM python:3.12.9-slim
LABEL authors="me"

WORKDIR /Project

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test,front --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY --exclude=app/dash  . .

CMD ["python", "main.py"]