# Dockerfile
FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Dependencias del SO necesarias para xhtml2pdf/reportlab/cairo/pango/freetype
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev \
    libfreetype6 libjpeg62-turbo libpng16-16 zlib1g \
    shared-mime-info fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Recolectar archivos estáticos (requiere SECRET_KEY en build time o usar --noinput)
RUN python manage.py collectstatic --noinput || echo "Collectstatic failed, will run at startup"

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "600", "--workers", "2"]
