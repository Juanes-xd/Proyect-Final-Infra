# Benchmarks y Análisis de Performance

Esta carpeta contiene todos los scripts y resultados de benchmarking para la comparación de rendimiento entre microservicios originales y implementaciones con Ray Remote.

## Estructura

```
benchmarks/
├── scripts/                        # Scripts de benchmarking
│   ├── ray_benchmark.py            # Benchmark básico Ray vs Original
│   ├── ray_comparison_benchmark.py # Comparación comprehensiva
│   ├── ray_performance_benchmark.py # Análisis de performance detallado
│   ├── benchmark_original.py       # Benchmark servicios originales
│   ├── compare_performance.py      # Comparación de performance
│   └── identify_bottlenecks.py     # Identificación de cuellos de botella
│
├── results/                        # Resultados de benchmarks
│   ├── benchmark_results_*.csv     # Resultados en formato CSV
│   ├── benchmark_results_*.json    # Resultados en formato JSON
│   ├── ray_performance_results_*.csv # Resultados performance Ray
│   ├── ray_performance_results_*.json
│   └── comparison_benchmark_*.txt  # Comparaciones textuales
│
├── requirements.txt                # Dependencias para benchmarking
└── README.md                       # Este archivo
```

## Scripts Disponibles

### 🚀 Ray Benchmarks
- **ray_benchmark.py**: Comparación básica Ray Remote vs servicios originales
- **ray_comparison_benchmark.py**: Benchmark comprehensivo con métricas detalladas
- **ray_performance_benchmark.py**: Análisis profundo de performance y escalabilidad

### 📊 Benchmarks Originales
- **benchmark_original.py**: Benchmark de servicios originales
- **compare_performance.py**: Comparación entre diferentes implementaciones
- **identify_bottlenecks.py**: Identificación de limitaciones de performance

## Resultados Destacados

### 🏆 Performance Ray Remote vs Original
- **Tiempo de procesamiento**: 92.2% mejora promedio
- **Throughput**: 1419.3% mejora promedio
- **Tasa de éxito**: 100% en todas las pruebas
- **Escalabilidad**: Lineal con número de cores

### 📈 Métricas por Servicio
1. **Sentiment Analysis**: +93.7% tiempo, +1498.9% throughput
2. **Portfolio Optimization**: +85.7% tiempo, +598.4% throughput  
3. **GARCH Prediction**: +94.6% tiempo, +1751.8% throughput
4. **Strategy Analysis**: +94.8% tiempo, +1828.2% throughput

## Uso

### Ejecutar Benchmarks
```bash
# Desde la carpeta raíz del proyecto
cd benchmarks/scripts

# Benchmark comprehensivo
python ray_comparison_benchmark.py

# Performance detallado
python ray_performance_benchmark.py

# Benchmark básico
python ray_benchmark.py
```

### Ver Resultados
```bash
# Ver resultados más recientes (desde carpeta raíz)
ls benchmarks/results/ | sort -r | head -5

# Analizar resultados CSV
python -c "import pandas as pd; print(pd.read_csv('benchmarks/results/benchmark_results_latest.csv'))"
```

## Dependencias

Ver `requirements.txt` para las dependencias necesarias para ejecutar los benchmarks.

---

**Nota**: Los resultados demuestran que Ray Remote proporciona mejoras significativas en performance para todos los microservicios, validando la implementación paralela del proyecto.
