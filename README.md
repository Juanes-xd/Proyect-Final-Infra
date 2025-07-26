# Microservicios de Trading - FastAPI

Este proyecto divide los últimos dos miniproyectos del notebook de trading en microservicios usando FastAPI y Docker.

## Estructura del Proyecto

```
microservicios-proyecto/
├── miniproyecto2/                    # Twitter Sentiment Strategy
│   ├── microservicio1/               # Sentiment Analyzer
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── microservicio2/               # Portfolio Manager
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── miniproyecto3/                    # Intraday Strategy Using GARCH Model
│   ├── microservicio1/               # GARCH Volatility Predictor
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── microservicio2/               # Intraday Strategy Engine
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Microservicios

### Miniproyecto 2: Twitter Sentiment Strategy

#### 1. Twitter Sentiment Analyzer (Puerto 8001)
- **Endpoint principal**: `http://localhost:8001`
- **Funcionalidades**:
  - `/status` - Estado del servicio - bien
  - `/load-sentiment-data` - Carga y procesa datos de sentiment - bien
  - `/calculate-engagement/{ticker}` - Calcula engagement ratio para un ticker - bien

#### 2. Portfolio Manager (Puerto 8002)
- **Endpoint principal**: `http://localhost:8002`
- **Funcionalidades**:
  - `/status` - Estado del servicio - bien
  - `/select-top-stocks?limit=5` - Selecciona top stocks basado en engagement - bien
  - `/calculate-portfolio-returns` - Calcula retornos del portfolio - bien -["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
  - `/portfolio-performance` - Métricas de rendimiento - bien

### Miniproyecto 3: Intraday Strategy Using GARCH Model

#### 3. GARCH Volatility Predictor (Puerto 8003)
- **Endpoint principal**: `http://localhost:8003`
- **Funcionalidades**:
  - `/status` - Estado del servicio - bien
  - `/load-market-data` - Carga datos de mercado (diarios e intraday)- bien
  - `/predict-volatility` - Predice volatilidad usando modelo GARCH - bien
  {
  "ticker": "AAPL",
  "periods": 30}
  - `/calculate-rolling-variance` - Calcula varianza móvil- bien

#### 4. Intraday Strategy Engine (Puerto 8004)
- **Endpoint principal**: `http://localhost:8004`
- **Funcionalidades**:
  - `/status` - Estado del servicio - bien
  - `/calculate-intraday-signals` - Calcula señales intraday - bein
  {"daily_signal":1}
  - `/execute-strategy` - Ejecuta estrategia de trading - bien
  {
"position_size":"1000"}
  - `/strategy-performance` - Métricas de rendimiento - bien

## Cómo Ejecutar

### Prerequisitos
- Docker
- Docker Compose

### Pasos de Ejecución

1. **Clonar/Navegar al directorio del proyecto**:
   ```bash
   cd microservicios-proyecto
   ```

2. **Construir y ejecutar todos los microservicios**:
   ```bash
   docker-compose up --build
   ```

3. **Verificar que todos los servicios estén funcionando**:
   - Sentiment Analyzer: http://localhost:8001/docs
   - Portfolio Manager: http://localhost:8002/docs
   - GARCH Predictor: http://localhost:8003/docs
   - Intraday Strategy: http://localhost:8004/docs

### Comandos Útiles

- **Ejecutar en segundo plano**:
  ```bash
  docker-compose up -d --build
  ```

- **Ver logs de un servicio específico**:
  ```bash
  docker-compose logs sentiment-analyzer
  ```

- **Detener todos los servicios**:
  ```bash
  docker-compose down
  ```

- **Reconstruir un servicio específico**:
  ```bash
  docker-compose build sentiment-analyzer
  ```

## Ejemplos de Uso

### 1. Probar Twitter Sentiment Strategy

```bash
# Cargar datos de sentiment
curl http://localhost:8001/load-sentiment-data

# Calcular engagement para AAPL
curl http://localhost:8001/calculate-engagement/AAPL

# Seleccionar top 5 stocks
curl http://localhost:8002/select-top-stocks?limit=5

# Ver rendimiento del portfolio
curl http://localhost:8002/portfolio-performance
```

### 2. Probar GARCH Strategy

```bash
# Cargar datos de mercado
curl http://localhost:8003/load-market-data

# Predecir volatilidad
curl -X POST http://localhost:8003/predict-volatility

# Calcular señales intraday
curl -X POST http://localhost:8004/calculate-intraday-signals

# Ejecutar estrategia
curl -X POST http://localhost:8004/execute-strategy
```

## Documentación API

Cada microservicio incluye documentación interactiva de Swagger UI:

- Sentiment Analyzer: http://localhost:8001/docs
- Portfolio Manager: http://localhost:8002/docs
- GARCH Predictor: http://localhost:8003/docs
- Intraday Strategy: http://localhost:8004/docs

## Archivos de Datos Incluidos

El proyecto incluye los archivos CSV reales del notebook original:

- **miniproyecto2/** (ambos microservicios):
  - `sentiment_data.csv` - Datos de sentiment de Twitter para análisis de engagement

- **miniproyecto3/** (ambos microservicios):
  - `simulated_daily_data.csv` - Datos diarios para el modelo GARCH
  - `simulated_5min_data.csv` - Datos intraday de 5 minutos para señales de trading

## Características Técnicas

- **Framework**: FastAPI
- **Containerización**: Docker
- **Orquestación**: Docker Compose
- **Datos**: CSV reales del proyecto original
- **APIs**: RESTful con documentación automática
- **Puertos**: 8001-8004

## Notas Importantes

1. **Datos Reales**: Los microservicios ahora usan los archivos CSV reales del proyecto original:
   - `sentiment_data.csv` - Para los microservicios del miniproyecto 2
   - `simulated_daily_data.csv` - Para el análisis GARCH
   - `simulated_5min_data.csv` - Para las señales intraday

2. **Funcionalidades Implementadas**: Las implementaciones mantienen las funcionalidades core de cada miniproyecto, procesando los datos reales del notebook original.

3. **Escalabilidad**: Cada microservicio puede escalarse independientemente según las necesidades.

4. **Monitoreo**: Para producción, se recomienda agregar logging, métricas y monitoreo.

## Troubleshooting

- **Puerto ocupado**: Si algún puerto está ocupado, cambiar los puertos en `docker-compose.yml`
- **Problemas de construcción**: Ejecutar `docker-compose down` y luego `docker-compose up --build`
- **Logs**: Usar `docker-compose logs [servicio]` para ver logs específicos
