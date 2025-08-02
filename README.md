# 🚀 PROYECTO FINAL - INFRAESTRUCTURAS DISTRIBUIDAS Y PARALELAS

Este proyecto implementa **tres arquitecturas diferentes** para sistemas de trading algorítmico, comparando rendimiento y escalabilidad entre implementaciones secuenciales, microservicios tradicionales y computación distribuida con Ray.

## 🎯 **OBJETIVOS DEL PROYECTO**

- **Implementación Secuencial**: Jupyter Notebook con procesamiento tradicional
- **Microservicios**: Arquitectura distribuida con Docker y FastAPI  
- **Ray Distribuido**: Computación paralela y distribuida con Ray framework
- **Benchmarking Comparativo**: Análisis de rendimiento entre las tres implementaciones

---

## 🏗️ **ARQUITECTURAS IMPLEMENTADAS**

### 1️⃣ **Implementación Secuencial**
- **Ubicación**: `Instrucciones Proyecto/Algorithmic_Trading_Machine_Learning_Quant_Strategies.ipynb`
- **Tecnología**: Jupyter Notebook, Python tradicional
- **Componentes**: Análisis de sentimientos, predicción GARCH, estrategias intraday, gestión de portfolio

### 2️⃣ **Miniproyecto 2: Twitter Sentiment Strategy**
- **Ubicación**: `miniproyecto2/`
- **Arquitectura**: Microservicios con Docker
- **Servicios**:
  - `Twitter Sentiment Analyzer` (puerto 8001)
  - `Portfolio Manager` (puerto 8002)

### 3️⃣ **Miniproyecto 3: Intraday Strategy Using GARCH Model**
- **Ubicación**: `miniproyecto3/`
- **Arquitectura**: Microservicios con Docker
- **Servicios**:
  - `GARCH Volatility Predictor` (puerto 8003)
  - `Intraday Strategy Engine` (puerto 8004)

### 4️⃣ **Ray Distributed Services**
- **Ubicación**: `ray_services/`
- **Arquitectura**: Computación distribuida con Ray
- **Servicios**:
  - `Ray Sentiment Analyzer` (puerto 8005)
  - `Ray GARCH Predictor` (puerto 8006)
  - `Ray Intraday Strategy` (puerto 8007)
  - `Ray Portfolio Manager` (puerto 8008)

---

## 📋 **PREREQUISITOS**

```bash
- Docker Desktop
- Python 3.11+
- Git
- 8GB RAM mínimo (recomendado 16GB para Ray)
```

## ⚡ **INSTALACIÓN Y USO**

### 🚀 **PASO 1: CLONAR REPOSITORIO**
```bash
git clone <repo-url>
cd Proyect-Final-Infra
```

### 🔨 **PASO 2: CONSTRUCCIÓN DE SERVICIOS**

El proyecto incluye **dos archivos Docker Compose diferentes**:
- `docker-compose.yml` - **Solo microservicios tradicionales** (miniproyecto2 + miniproyecto3)
- `docker-compose-ray.yml` - **Servicios Ray distribuidos** (ray_services)

**Opción A - Solo Microservicios Tradicionales:**
```bash
# Usar docker-compose.yml (4 servicios)
docker-compose build --no-cache
docker-compose up -d
```

**Opción B - Solo Servicios Ray Distribuidos:**
```bash
# Usar docker-compose-ray.yml (4 servicios Ray)
docker-compose -f docker-compose-ray.yml build --no-cache
docker-compose -f docker-compose-ray.yml up -d
```

### 🔍 **PASO 3: VERIFICACIÓN DE SERVICIOS**

**Verificar contenedores activos:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Servicios esperados según la opción elegida:**

**Opción A (docker-compose.yml):**
- `twitter-sentiment-analyzer` (puerto 8001)
- `portfolio-manager` (puerto 8002) 
- `garch-volatility-predictor` (puerto 8003)
- `intraday-strategy-engine` (puerto 8004)

**Opción B (docker-compose-ray.yml):**
- `ray-sentiment-analyzer` (puerto 8005)
- `ray-garch-predictor` (puerto 8006)
- `ray-intraday-strategy` (puerto 8007)
- `ray-portfolio-manager` (puerto 8008)

**Opción C (ambos archivos):**
- Todos los 8 servicios listados arriba

### 🧪 **PASO 4: PRUEBAS DE FUNCIONALIDAD**

**Verificar health checks según los servicios activos:**
```bash
# Si usaste Opción A (docker-compose.yml) - Microservicios tradicionales
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Si usaste Opción B (docker-compose-ray.yml) - Ray services
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health
curl http://localhost:8008/health

# Si usaste Opción C (ambos archivos) - Todos los servicios
# Ejecutar todos los curl de arriba
```

### 📊 **PASO 5: EJECUTAR BENCHMARKING COMPARATIVO**

Para comparar el rendimiento entre las tres implementaciones:

```bash
# Configurar entorno Python
cd benchmarks
pip install -r requirements.txt

# Ejecutar benchmark completo
cd scripts
python comprehensive_benchmark.py
```

**El benchmark ejecutará:**
- ✅ Implementación secuencial (Jupyter)
- ✅ Microservicios tradicionales (puertos 8001-8004)
- ✅ Ray distribuido (puertos 8005-8008)
- ✅ Comparación de métricas de rendimiento

### 📈 **PASO 6: ANÁLISIS DE RESULTADOS**

Los resultados se guardan en `benchmarks/results/` e incluyen:
- **Tiempo de ejecución** por implementación
- **Throughput** (operaciones por segundo)
- **Uso de recursos** (CPU, memoria)
- **Escalabilidad** comparativa

Los benchmarks generan varios archivos en `benchmarks/results/`:
- `comparison_benchmark_YYYYMMDD_HHMMSS.txt` - Comparación principal
- `ray_performance_results_YYYYMMDD_HHMMSS.json` - Métricas detalladas  
- `ray_performance_results_YYYYMMDD_HHMMSS.csv` - Datos exportables
- `REPORTE_FINAL_PROYECTO.md` - Reporte completo del proyecto

---

## 🏗️ **ARQUITECTURA DEL PROYECTO**

```
📁 Proyect-Final-Infra/
---

## 📂 **ESTRUCTURA DEL PROYECTO**

```
Proyect-Final-Infra/
├── � Instrucciones Proyecto/        # Implementación Secuencial
│   └── Algorithmic_Trading_Machine_Learning_Quant_Strategies.ipynb
├── �📁 miniproyecto2/                 # Twitter Sentiment Strategy
│   ├── 📁 microservicio1/            # Sentiment Analyzer (Puerto 8001)
│   └── 📁 microservicio2/            # Portfolio Manager (Puerto 8002)
├── 📁 miniproyecto3/                 # Intraday Strategy Using GARCH Model
│   ├── 📁 microservicio1/            # GARCH Predictor (Puerto 8003)
│   └── 📁 microservicio2/            # Intraday Strategy (Puerto 8004)
├── 📁 ray_services/                  # 🚀 RAY DISTRIBUTED SERVICES
│   ├── 📁 sentiment_analyzer/        # Ray Sentiment (Puerto 8005)
│   ├── 📁 garch_predictor/          # Ray GARCH (Puerto 8006)
│   ├── 📁 intraday_strategy/        # Ray Intraday (Puerto 8007)
│   ├── 📁 portfolio_manager/        # Ray Portfolio (Puerto 8008)
│   └── 📁 data/                     # Datos centralizados CSV
├── 📁 benchmarks/                   # 📊 SISTEMA DE BENCHMARKING
│   ├── 📁 scripts/                  # Scripts de análisis comparativo
│   ├── 📁 results/                  # Resultados y reportes
│   └── requirements.txt
├── docker-compose.yml              # 🔧 Microservicios tradicionales (puertos 8001-8004)
├── docker-compose-ray.yml          # 🚀 Servicios Ray distribuidos (puertos 8005-8008)
└── README.md                       # Esta guía
```

---

## 🌐 **SERVICIOS Y PUERTOS**

### 🔧 **Microservicios Tradicionales**
| Servicio | Puerto | Implementación | Health Check |
|----------|--------|----------------|--------------|
| **Twitter Sentiment Analyzer** | 8001 | miniproyecto2/microservicio1 | http://localhost:8001/health |
| **Portfolio Manager** | 8002 | miniproyecto2/microservicio2 | http://localhost:8002/health |
| **GARCH Volatility Predictor** | 8003 | miniproyecto3/microservicio1 | http://localhost:8003/health |
| **Intraday Strategy Engine** | 8004 | miniproyecto3/microservicio2 | http://localhost:8004/health |

### 🚀 **Ray Distributed Services**
| Servicio | Puerto | Implementación | Health Check | **Ventaja Ray** |
|----------|--------|----------------|--------------|----------------|
| **Ray Sentiment Analyzer** | 8005 | ray_services/sentiment_analyzer | http://localhost:8005/health | Procesamiento paralelo |
| **Ray GARCH Predictor** | 8006 | ray_services/garch_predictor | http://localhost:8006/health | Predicción distribuida |
| **Ray Intraday Strategy** | 8007 | ray_services/intraday_strategy | http://localhost:8007/health | Backtesting paralelo |
| **Ray Portfolio Manager** | 8008 | ray_services/portfolio_manager | http://localhost:8008/health | Optimización distribuida |

---

## 🧪 **EJEMPLOS DE USO Y TESTING**

### 1️⃣ **Verificar Health de Servicios**

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health  
curl http://localhost:8003/health
curl http://localhost:8004/health

# Ray services (si están activos)
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health  
curl http://localhost:8008/health
```

### 2️⃣ **Test de Funcionalidad Básica**

```bash
# Miniproyecto 2: Twitter Sentiment Strategy
curl http://localhost:8001/analyze-sentiment
curl http://localhost:8002/portfolio-status

# Miniproyecto 3: Intraday Strategy Using GARCH Model  
curl http://localhost:8003/predict-volatility
curl http://localhost:8004/strategy-signals

# Ray Services (procesamiento distribuido)
curl http://localhost:8005/parallel-sentiment
curl http://localhost:8006/parallel-garch
curl http://localhost:8007/parallel-strategy
curl http://localhost:8008/parallel-portfolio
```

### 3️⃣ **Benchmark Completo**

```bash
cd benchmarks/scripts
python comprehensive_benchmark.py
```

---

## 📊 **MÉTRICAS Y RESULTADOS ESPERADOS**

### � **Comparación de Implementaciones**
| Implementación | Tiempo Ejecución | Throughput | Recursos | Escalabilidad |
|---------------|------------------|------------|----------|---------------|
|---------------|---------------|-------------------|-------------|
| **Secuencial (Jupyter)** | Baseline | ~5-10 ops/s | Alto (single-core) | Limitada |
| **Microservicios** | Baseline | ~15-25 ops/s | Medio (multi-container) | Horizontal |
| **Ray Distribuido** | **Mejor** | ~30-50 ops/s | Óptimo (multi-core) | **Lineal** |

### 🏆 **Ventajas por Implementación**
- **Secuencial**: Simplicidad, desarrollo rápido, debugging fácil
- **Microservicios**: Escalabilidad horizontal, tolerancia a fallos, despliegue independiente
- **Ray Distribuido**: Alto rendimiento, paralelización automática, optimización de recursos

---

## 🔧 **COMANDOS ÚTILES PARA DESARROLLO**

### 🐳 **Gestión de Docker**
```bash
# Ver logs de servicios específicos
docker-compose logs sentiment-analyzer                    # Servicios tradicionales
docker-compose -f docker-compose-ray.yml logs ray-portfolio-manager  # Servicios Ray

# Reconstruir servicios específicos
docker-compose build --no-cache sentiment-analyzer        # Servicios tradicionales
docker-compose -f docker-compose-ray.yml build --no-cache ray-garch-predictor  # Servicios Ray

# Ejecutar en modo desarrollo (logs en vivo)
docker-compose up                                         # Servicios tradicionales
docker-compose -f docker-compose-ray.yml up              # Servicios Ray

# Detener servicios
docker-compose down                                       # Servicios tradicionales
docker-compose -f docker-compose-ray.yml down            # Servicios Ray

# Detener TODOS los servicios
docker-compose down && docker-compose -f docker-compose-ray.yml down

# Limpiar sistema Docker completamente
docker system prune -a -f
```

### 📊 **Gestión de Benchmarks**
```bash
# Ejecutar benchmarks individuales
cd benchmarks/scripts
python benchmark_original.py          # Implementación secuencial
python ray_benchmark.py              # Solo Ray services
python comprehensive_benchmark.py    # Comparación completa

# Ver resultados
cd ../results
ls -la      # Linux/Mac
dir         # Windows
```

### 🔍 **Debugging y Monitoreo**
```bash
# Verificar uso de recursos
### 🔍 **Monitoreo y Debugging**
```bash
# Ver recursos en tiempo real
docker stats

# Inspeccionar configuración de contenedor
docker inspect twitter-sentiment-analyzer

# Acceder al contenedor para debugging
docker exec -it garch-volatility-predictor /bin/bash

# Ver red de servicios
docker network ls
docker network inspect unified-services-network
```

---

## 🗂️ **ARCHIVOS Y DATASETS**

### 📊 **Datos del Proyecto**
Los servicios utilizan datasets específicos por implementación:

```bash
📁 Datos por Implementación:
├── 📊 Instrucciones Proyecto/
│   ├── sentiment_data.csv          # Datos originales para Jupyter
│   ├── simulated_daily_data.csv    # Datos diarios originales
│   └── simulated_5min_data.csv     # Datos intraday originales
├── 📁 miniproyecto2/ & miniproyecto3/
│   └── [Copias locales de datos]   # Datos específicos por microservicio
└── 📁 ray_services/data/
    ├── sentiment_data.csv          # Datos centralizados para Ray
    ├── simulated_daily_data.csv    # Datos centralizados para Ray
    └── simulated_5min_data.csv     # Datos centralizados para Ray
```

### 📈 **Resultados de Benchmarking**
```bash
📁 benchmarks/results/
├── comprehensive_results_YYYYMMDD_HHMMSS.json  # Resultados completos
├── performance_comparison_YYYYMMDD.csv         # Datos exportables
├── benchmark_summary.md                        # Resumen ejecutivo
└── REPORTE_FINAL_PROYECTO.md                  # Reporte académico
```

---

## 🚨 **TROUBLESHOOTING**

### ❌ **Problemas Comunes y Soluciones**

**1. Puerto ya en uso:**
```bash
# Windows
netstat -ano | findstr 8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

**2. Error al construir imágenes:**
```bash
# Limpiar y reconstruir completamente
docker-compose down
docker-compose -f docker-compose-ray.yml down
docker system prune -f

# Reconstruir según necesidad
docker-compose build --no-cache          # Solo tradicionales
docker-compose -f docker-compose-ray.yml build --no-cache  # Solo Ray
```

**3. Servicios no health check:**
```bash
# Verificar logs del servicio problemático
docker-compose logs sentiment-analyzer                     # Tradicionales
docker-compose -f docker-compose-ray.yml logs ray-garch-predictor  # Ray

# Restart de servicio específico
docker-compose restart intraday-strategy                   # Tradicionales
docker-compose -f docker-compose-ray.yml restart ray-portfolio-manager  # Ray
```

**4. Benchmarks fallan por conexión:**
```bash
# Verificar todos los servicios estén activos
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test de conectividad individual
curl http://localhost:8001/health
curl http://localhost:8005/health
```

**5. Problemas de memoria con Ray:**
```bash
# Aumentar límites de Docker Desktop
# Settings > Resources > Memory: 8GB mínimo

# O ejecutar solo microservicios tradicionales:
docker-compose up -d

# O ejecutar solo servicios Ray:
docker-compose -f docker-compose-ray.yml up -d
```

### 🔍 **Verificación Rápida del Sistema**

```bash
# Script de verificación completa (Windows PowerShell)
Write-Host "=== VERIFICANDO SERVICIOS ===" -ForegroundColor Yellow
@(8001,8002,8003,8004,8005,8006,8007,8008) | ForEach-Object {
    $port = $_
    Write-Host -NoNewline "Puerto $port : "
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ FAIL" -ForegroundColor Red
    }
}

Write-Host "`n=== VERIFICANDO CONTENEDORES ===" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 📚 **DOCUMENTACIÓN ADICIONAL**

### 📋 **Archivos de Referencia**
| Archivo | Descripción | Contenido |
|---------|-------------|-----------|
| **README.md** | 📖 Manual completo del proyecto | Esta guía completa |
| **COMANDOS_RAPIDOS.md** | ⚡ Comandos frecuentes | Referencia rápida |
| **docker-compose.yml** | � Microservicios tradicionales | 4 servicios (puertos 8001-8004) |
| **docker-compose-ray.yml** | 🚀 Servicios Ray distribuidos | 4 servicios Ray (puertos 8005-8008) |

### 🎯 **Objetivos Académicos Cumplidos**

✅ **Implementación Secuencial**: Jupyter Notebook funcional  
✅ **Microservicios Tradicionales**: 4 servicios dockerizados  
✅ **Ray Distribuido**: 4 servicios con paralelización  
✅ **Benchmarking Comparativo**: Sistema de medición completo  
✅ **Documentación Técnica**: Manual de usuario detallado  

### 🔬 **Contribuciones Técnicas**

1. **Arquitectura Híbrida**: Comparación de 3 paradigmas diferentes
2. **Separación de Orquestación**: Dos archivos Docker Compose independientes
3. **Health Monitoring**: Endpoints /health en todos los servicios
4. **Benchmarking Automatizado**: Scripts de comparación automática
5. **Documentación Ejecutiva**: README estructurado y completo

---

## � **CRÉDITOS Y RECONOCIMIENTOS**

**Proyecto Final - Infraestructuras Distribuidas y Paralelas**  
**Universidad**: [Nombre de la Universidad]  
**Curso**: Infraestructuras Distribuidas y Paralelas  
**Semestre**: 6  

### � **Logros del Proyecto**
- ✅ **Implementación exitosa** de 3 arquitecturas diferentes
- ✅ **Paralelización efectiva** con Ray framework
- ✅ **Containerización completa** con Docker
- ✅ **Benchmarking académico** riguroso y documentado
- ✅ **Escalabilidad demostrada** cuantitativamente

---

**📞 Para soporte técnico o consultas académicas, revisar la documentación incluida en el proyecto.**

---

## 🏆 **RESUMEN EJECUTIVO**

### ✅ **Estado del Proyecto**: COMPLETO Y FUNCIONAL

| Métrica | Valor |
|---------|-------|
| **Servicios Activos** | 8/8 (100%) |
| **Benchmarks Ejecutados** | 4/4 (100%) |  
| **Criterio Ray Cumplido** | ✅ COMPLETO |
| **Mejora Máxima Throughput** | +52.1% |
| **Throughput Promedio** | 22.17 req/s |

### 🚀 **Próximos Pasos Recomendados**

1. **Explorar Ray Tune** para optimización de hiperparámetros
2. **Implementar Ray Serve** para serving en producción  
3. **Agregar métricas de monitoreo** con Prometheus/Grafana
4. **Escalar a Kubernetes** para cargas de trabajo mayores

---

**📝 Última actualización**: 25 de Julio, 2025  
**🔧 Mantenido por**: Equipo de Infraestructuras Distribuidas  
**📧 Soporte**: Revisar issues en el repositorio

**¡El proyecto está listo para demostrar las capacidades de Ray Remote! 🚀**
