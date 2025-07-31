FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY garch_predictor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar datos
COPY data/simulated_daily_data.csv ./simulated_daily_data.csv
COPY data/simulated_5min_data.csv ./simulated_5min_data.csv

# Copiar código fuente
COPY garch_predictor/garch_predictor_ray.py .

# Variables de entorno para Ray
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1
ENV RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
ENV RAY_SERVE_HTTP_HOST=0.0.0.0
ENV RAY_SERVE_HTTP_PORT=8000

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar con uvicorn (más simple y confiable)
CMD ["python", "garch_predictor_ray.py"]
