# 📊 BENCHMARKING SUITE - MICROSERVICIOS

Este directorio contiene todas las herramientas para realizar benchmarking y análisis de rendimiento de los microservicios.

## 🗂️ Estructura

```
benchmarks/
├── 📁 results/           # Todos los resultados y gráficas
│   ├── benchmark_results.json
│   ├── benchmark_comparison_latest.png
│   ├── detailed_metrics_*.png
│   ├── benchmark_report_*.txt
│   └── REPORTE_FINAL_PROYECTO.md
├── 📁 scripts/           # Scripts de benchmarking
│   ├── benchmark_original.py
│   ├── ray_comparison_benchmark.py
│   ├── ray_benchmark.py
│   ├── compare_performance.py
│   ├── identify_bottlenecks.py
│   └── ray_performance_benchmark.py
└── 📄 requirements.txt   # Dependencias
```

## 🚀 Uso Rápido

### 1. Ejecutar Benchmark Completo
```bash
# Desde el directorio raíz del proyecto
python benchmarks/scripts/benchmark_original.py
```

### 2. Generar Gráficas de Comparación
```bash
python generate_benchmark_charts.py
```

### 3. Ver Resultados en Texto
```bash
python show_results.py
```

### 4. Ver Archivos Organizados
```bash
python show_benchmark_files.py
```

## 📈 Scripts Disponibles

### 🔧 Scripts Principales
- **benchmark_original.py**: Benchmark completo de servicios originales
- **ray_comparison_benchmark.py**: Comparación Ray vs Secuencial
- **generate_benchmark_charts.py**: Generador de gráficas
- **show_results.py**: Visualizador de resultados en texto

### 📊 Scripts de Análisis
- **ray_benchmark.py**: Benchmark específico de Ray
- **compare_performance.py**: Comparación detallada
- **identify_bottlenecks.py**: Identificación de cuellos de botella
- **ray_performance_benchmark.py**: Análisis de rendimiento Ray

## 📋 Resultados Generados

### 📄 Archivos JSON
- `benchmark_results.json`: Datos completos del benchmark original
- `ray_benchmark_results.json`: Datos del benchmark Ray (cuando esté disponible)

### 📈 Gráficas PNG
- `benchmark_comparison_latest.png`: Gráfica principal de comparación
- `detailed_metrics_*.png`: Métricas detalladas por servicio
- `benchmark_comparison_*.png`: Gráficas con timestamp

### 📝 Reportes TXT
- `benchmark_report_*.txt`: Reportes detallados con recomendaciones

## 🎯 Resultados Actuales

### Servicios Originales
| Servicio | Tiempo Promedio | Throughput | Estado |
|----------|-----------------|------------|---------|
| Portfolio Manager | 0.026s | 38.7 req/s | ✅ Más rápido |
| Sentiment Analyzer | 0.106s | 9.4 req/s | ✅ Eficiente |
| Intraday Strategy | 0.743s | 1.35 req/s | ⚠️ Mejorable |
| GARCH Predictor | 0.814s | 1.23 req/s | ⚠️ Candidato Ray |

### Análisis de Concurrencia
- **Tasa de éxito**: 75.0%
- **Throughput bajo carga**: 3.86 req/s
- **Requests exitosos**: 30/40

## 🔍 Identificación de Bottlenecks

1. **GARCH Predictor** - Más lento (0.814s)
2. **Intraday Strategy** - Segundo más lento (0.743s)
3. **Portfolio Manager** - Baja tasa de éxito en concurrencia

## 💡 Recomendaciones

1. **Priorizar Ray Remote en GARCH Predictor** - Mayor beneficio esperado
2. **Optimizar Intraday Strategy** - Segundo candidato
3. **Investigar errores 405 en Portfolio Manager**
4. **Implementar cache para Sentiment Analyzer**

## 🛠️ Requisitos

```bash
pip install -r requirements.txt
```

Dependencias principales:
- requests
- pandas
- numpy
- matplotlib
- seaborn

## 📞 Comandos de Soporte

```bash
# Ver estado de servicios Docker
docker ps

# Ver logs de un servicio específico
docker logs <container_name>

# Reiniciar servicios
docker-compose -f docker-compose-ray.yml restart

# Limpiar y reconstruir
docker-compose -f docker-compose-ray.yml down
docker-compose -f docker-compose-ray.yml up --build -d
```
