# syntax=docker/dockerfile:1.7-labs
FROM python:3.12.9-slim
LABEL authors="me"

WORKDIR /Project

COPY --from=root  poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test,extra --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY --from=root  app/db app/db
COPY --from=root app/utils app/utils
COPY --from=root  dash_plotly.py ./
CMD ["python", "dash_plotly.py"]