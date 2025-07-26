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

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["python", "garch_predictor_ray.py"]
