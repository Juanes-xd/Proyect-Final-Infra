FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY sentiment_analyzer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar datos
COPY data/sentiment_data.csv ./sentiment_data.csv

# Copiar código fuente
COPY sentiment_analyzer/sentiment_analyzer_ray.py .

# Variables de entorno para Ray
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1
ENV RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
ENV RAY_SERVE_HTTP_HOST=0.0.0.0
ENV RAY_SERVE_HTTP_PORT=8000

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar con uvicorn (más simple y confiable)
CMD ["python", "sentiment_analyzer_ray.py"]
