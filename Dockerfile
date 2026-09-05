FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

FROM base AS test
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY src/ ./src/
COPY tests/ ./tests/
COPY conftest.py ./
RUN python -m pytest -v && touch /test_passed

FROM base AS runtime
# Depend on the test stage so tests run on every build; the marker
# file is the only thing pulled in, keeping the runtime image clean.
COPY --from=test /test_passed /test_passed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/
EXPOSE 8000
CMD ["python", "app.py"]
