FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dépendances système + lxml compilé nativement (plus fiable que PyPI wheel sur réseau lent)
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installer lxml séparément d'abord (paquet lourd, plus susceptible de timeout)
RUN pip install --no-cache-dir --timeout 120 lxml

# Installer le reste
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles

RUN python manage.py collectstatic --noinput \
    --settings=config.settings.production 2>/dev/null || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120"]
