FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY portfolio_manager/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar datos (aunque portfolio_manager no los usa directamente, 
# mantenemos consistencia)
COPY data/*.csv ./

# Copiar código
COPY portfolio_manager/portfolio_manager_ray.py .

# Variables de entorno para Ray
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "portfolio_manager_ray.py"]
