FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    WEB_CONCURRENCY=2

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Сервер не должен работать от root.
RUN useradd --system --no-create-home app
USER app

EXPOSE 3250

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3250/healthz', timeout=4)"

# --proxy-headers: правильные адреса и схема (https) за обратным прокси (nginx).
# Число процессов задаётся переменной WEB_CONCURRENCY.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3250", "--proxy-headers", "--forwarded-allow-ips", "*"]
