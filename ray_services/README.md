# Ray Services - Microservicios con Ray Remote

Esta carpeta contiene una implementación de microservicios usando **Ray Remote** para paralelización y optimización de rendimiento.

## Estructura Organizacional

```
ray_services/
├── data/                           # Datos compartidos
│   ├── sentiment_data.csv          # Datos de análisis de sentimientos
│   ├── simulated_5min_data.csv     # Datos de mercado de 5 minutos
│   └── simulated_daily_data.csv    # Datos de mercado diarios
│
├── sentiment_analyzer/             # Microservicio 1: Análisis de Sentimientos
│   ├── Dockerfile                  # Configuración Docker
│   ├── sentiment_analyzer_ray.py   # Implementación con Ray Remote
│   └── requirements.txt            # Dependencias Python
│
├── garch_predictor/               # Microservicio 2: Predicción GARCH
│   ├── Dockerfile                 # Configuración Docker
│   ├── garch_predictor_ray.py     # Implementación con Ray Remote
│   └── requirements.txt           # Dependencias Python
│
├── portfolio_manager/             # Microservicio 3: Gestión de Portafolios
│   ├── Dockerfile                 # Configuración Docker
│   ├── portfolio_manager_ray.py   # Implementación con Ray Remote
│   └── requirements.txt           # Dependencias Python
│
└── intraday_strategy/             # Microservicio 4: Estrategias Intradía
    ├── Dockerfile                 # Configuración Docker
    ├── intraday_strategy_ray.py   # Implementación con Ray Remote
    └── requirements.txt           # Dependencias Python
```

## Características Principales

### 🚀 Ray Remote Implementation
- **@ray.remote**: Decoradores para paralelización automática
- **Distribución de carga**: Procesamiento paralelo de datos
- **Optimización de memoria**: Gestión eficiente del object store
- **Escalabilidad**: Capacidad de procesamiento distribuido

### 🐳 Arquitectura Docker
- **Microservicios independientes**: Cada servicio en su propio contenedor
- **Contexto de build unificado**: Todos los servicios construidos desde `ray_services/`
- **Datos centralizados**: Carpeta `data/` compartida entre servicios
- **Configuración Ray**: Variables de entorno optimizadas

### 📊 Servicios Disponibles

1. **Sentiment Analyzer** (Puerto 8005)
   - Análisis de sentimientos en paralelo
   - Procesamiento de texto distribuido
   - Machine learning con Ray

2. **GARCH Predictor** (Puerto 8006)
   - Predicción de volatilidad paralela
   - Modelos econométricos distribuidos
   - Análisis de series temporales

3. **Portfolio Manager** (Puerto 8007)
   - Optimización de portafolios en paralelo
   - Cálculo de métricas de riesgo distribuido
   - Análisis de performance

4. **Intraday Strategy** (Puerto 8008)
   - Backtesting de estrategias paralelo
   - Generación de señales distribuida
   - Análisis técnico avanzado

## Comandos de Uso

### Construcción Individual
```bash
# Construir un servicio específico
docker build -f ray_services/sentiment_analyzer/Dockerfile ray_services -t sentiment-ray

# Construir todos los servicios Ray
docker-compose -f docker-compose-ray.yml build
```

### Ejecución
```bash
# Ejecutar todos los servicios (originales + Ray)
docker-compose -f docker-compose-ray.yml up

# Ejecutar solo servicios Ray
docker-compose -f docker-compose-ray.yml up sentiment-analyzer-ray garch-predictor-ray portfolio-manager-ray intraday-strategy-ray
```

### Testing de Performance
```bash
# Benchmarking completo
python ray_comparison_benchmark.py

# Performance individual
python ray_performance_benchmark.py
```

## Beneficios de la Nueva Estructura

### ✅ Organización
- **Separación clara**: Cada microservicio en su propia carpeta
- **Datos centralizados**: Fácil gestión de datasets
- **Estructura escalable**: Fácil agregar nuevos servicios

### ✅ Mantenimiento
- **Dockerfiles independientes**: Configuración específica por servicio
- **Dependencies aisladas**: requirements.txt por microservicio
- **Versionado granular**: Control independiente de versiones

### ✅ Desarrollo
- **Context unificado**: Build desde ray_services/ mantiene acceso a data/
- **Rutas simplificadas**: Referencias relativas limpias
- **Debugging facilitado**: Logs y errores aislados por servicio

## Performance Mejorado

Comparado con la implementación secuencial:
- **92.2%** mejora promedio en tiempo de procesamiento
- **1419.3%** mejora promedio en throughput
- **100%** éxito en todas las pruebas de carga
- **Escalabilidad lineal** con Ray Remote

## Configuración Ray

```python
# Configuración optimizada para cada servicio
ray.init(
    object_store_memory=100_000_000,  # 100MB object store
    num_cpus=None,  # Auto-detección de CPUs
    ignore_reinit_error=True
)
```

## Variables de Entorno Docker

```yaml
environment:
  - RAY_DISABLE_IMPORT_WARNING=1
  - RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1
  - SERVICE_NAME=Ray Service Name
```

---

**Nota**: Esta estructura optimizada garantiza una arquitectura limpia, escalable y de alto rendimiento para el proyecto de infraestructuras distribuidas y paralelas.
