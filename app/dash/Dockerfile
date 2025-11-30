# syntax=docker/dockerfile:1.7-labs
FROM python:3.12.9-slim
LABEL authors="me"

WORKDIR /Project

COPY  poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test,extra --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY  app/db app/db
COPY  app/utils app/utils
COPY  app/dash/assets/ ./assets/
COPY  app/dash/data_processing.py app/dash/
COPY  app/dash/crud/read_data_for_calculation.py app/dash/crud/
COPY  dash_plotly.py project_settings.py ./
CMD ["python", "dash_plotly.py"]