FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY intraday_strategy/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar datos
COPY data/simulated_5min_data.csv ./simulated_5min_data.csv
COPY data/simulated_daily_data.csv ./simulated_daily_data.csv

# Copiar código
COPY intraday_strategy/intraday_strategy_ray.py .

# Variables de entorno para Ray
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1
ENV RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
ENV RAY_SERVE_HTTP_HOST=0.0.0.0
ENV RAY_SERVE_HTTP_PORT=8000

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "intraday_strategy_ray.py"]
