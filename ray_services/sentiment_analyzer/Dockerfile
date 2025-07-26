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

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["python", "sentiment_analyzer_ray.py"]
