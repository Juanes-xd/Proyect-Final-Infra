# 🚀 COMANDOS DE REFERENCIA RÁPIDA

## ⚡ Setup Rápido (Start Here!)

```bash
# 1. Construir y levantar servicios
docker-compose -f docker-compose-ray.yml up -d --build

# 2. Verificar que todo funcione
docker ps

# 3. Ejecutar benchmarks
cd benchmarks && pip install -r requirements.txt
cd scripts && python ray_comparison_benchmark.py
```

## 🐳 Docker Commands

```bash
# Construir todo desde cero
docker-compose -f docker-compose-ray.yml build --no-cache

# Levantar servicios en background  
docker-compose -f docker-compose-ray.yml up -d

# Ver logs en vivo
docker-compose -f docker-compose-ray.yml logs -f

# Detener todo
docker-compose -f docker-compose-ray.yml down

# Limpiar todo (CUIDADO!)
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -aq) --force
```

## 📊 Benchmark Commands

```bash
# Navegar a benchmarks
cd benchmarks/scripts

# Ejecutar todos los benchmarks
python ray_comparison_benchmark.py     # Principal
python ray_performance_benchmark.py    # Detallado
python identify_bottlenecks.py         # Análisis
python compare_performance.py          # A/B Testing

# Ver resultados
cd ../results && ls -la
```

## 🌐 Testing Commands

```bash
# Test servicios originales
curl http://localhost:8001/status  # Sentiment
curl http://localhost:8002/status  # Portfolio  
curl http://localhost:8003/status  # GARCH
curl http://localhost:8004/status  # Intraday

# Test servicios Ray
curl http://localhost:8005/status  # Ray Sentiment
curl http://localhost:8006/status  # Ray GARCH
curl http://localhost:8007/status  # Ray Portfolio
curl http://localhost:8008/status  # Ray Intraday
```

## 🔍 Debug Commands

```bash
# Ver estado de contenedores
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Ver logs de un servicio específico
docker-compose -f docker-compose-ray.yml logs ray-portfolio-manager

# Entrar a un contenedor
docker exec -it ray-portfolio-manager /bin/bash

# Ver uso de recursos
docker stats
```

## 📈 One-Liner Health Check

```bash
# Verificar todo de una vez
for port in 8001 8002 8003 8004 8005 8006 8007 8008; do echo -n "Puerto $port: "; curl -s http://localhost:$port/status > /dev/null && echo "✅ OK" || echo "❌ FAIL"; done
```

## 🛠️ Rebuild Específico

```bash
# Rebuild solo un servicio
docker-compose -f docker-compose-ray.yml build ray-sentiment-analyzer
docker-compose -f docker-compose-ray.yml up -d ray-sentiment-analyzer

# Restart un servicio
docker-compose -f docker-compose-ray.yml restart ray-portfolio-manager
```

## 🎯 Quick Results Check

```bash
# Ver últimos resultados de benchmark
cd benchmarks/results
ls -lt | head -5  # Linux/Mac
dir /o-d | findstr /r "^[0-9]" | head -5  # Windows PowerShell
```

## 📊 Expected Results

Después de ejecutar benchmarks deberías ver:
- ✅ Portfolio Management: **+52.1% throughput improvement**
- ✅ GARCH Prediction: **+23.6% throughput improvement**  
- ✅ Ray Remote: **100% success rate**
- ✅ Average throughput: **22.17 req/s**
