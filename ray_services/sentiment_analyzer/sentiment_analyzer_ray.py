"""
Microservicio de Sentiment Analysis optimizado con Ray + FastAPI
Implementa paralelización para procesamiento de múltiples tickers
"""

import ray
from ray import serve
import pandas as pd
import numpy as np
import os
from typing import Dict, List
import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Ray
if not ray.is_initialized():
    ray.init(
        ignore_reinit_error=True,
        object_store_memory=100000000
    )

# Crear app FastAPI
app = FastAPI(title="Ray Sentiment Analyzer", version="1.0.0")

# Modelos Pydantic
class SentimentRequest(BaseModel):
    texts: List[str]

class TickerRequest(BaseModel):
    tickers: List[str]

# Funciones Ray remotas para paralelización
@ray.remote
def process_sentiment_batch(texts: List[str]) -> List[Dict]:
    """Procesa un lote de textos para análisis de sentimientos de forma paralela"""
    results = []
    for text in texts:
        # Simular análisis de sentimiento
        sentiment_score = np.random.uniform(-1, 1)
        confidence = np.random.uniform(0.7, 0.99)
        
        sentiment = "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral"
        
        results.append({
            "text": text,
            "sentiment": sentiment,
            "score": sentiment_score,
            "confidence": confidence
        })
    return results

@ray.remote
def load_and_process_sentiment_data():
    """Carga y procesa datos de sentiment usando Ray"""
    try:
        logger.info("Iniciando carga de datos con Ray")
        csv_file = 'sentiment_data.csv'

        if not os.path.exists(csv_file):
            logger.info("Generando datos sintéticos grandes para demostrar Ray")
            n_records = 50000
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']

            sentiment_data = {
                'Date': pd.date_range('2023-01-01', periods=n_records, freq='H'),
                'ticker': np.random.choice(tickers, n_records),
                'tweet_likes': np.random.randint(1, 1000, n_records),
                'tweet_reposts': np.random.randint(1, 500, n_records),
                'sentiment_score': np.random.uniform(-1, 1, n_records),
                'engagement_ratio': np.random.uniform(1.0, 5.0, n_records),
            }

            df = pd.DataFrame(sentiment_data)
            df.to_csv(csv_file, index=False)
            logger.info(f"Datos generados y guardados en {csv_file}")
        else:
            df = pd.read_csv(csv_file)
            logger.info(f"Datos cargados desde {csv_file}")

        return df
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return None

@ray.remote
def calculate_ticker_sentiment(ticker_data: pd.DataFrame) -> Dict:
    """Calcula métricas de sentimiento para un ticker específico"""
    try:
        metrics = {
            'avg_sentiment': ticker_data['sentiment_score'].mean(),
            'sentiment_volatility': ticker_data['sentiment_score'].std(),
            'total_engagement': ticker_data['engagement_ratio'].sum(),
            'positive_ratio': (ticker_data['sentiment_score'] > 0.1).mean(),
            'negative_ratio': (ticker_data['sentiment_score'] < -0.1).mean(),
            'total_tweets': len(ticker_data)
        }
        return metrics
    except Exception as e:
        logger.error(f"Error calculando métricas: {e}")
        return {}

# Endpoints FastAPI
@app.get("/")
def read_root():
    return {"message": "Ray Sentiment Analyzer funcionando", "service": "ray-sentiment-analyzer"}

@app.get("/status")
def read_status():
    return {
        "status": "Ray Sentiment Analyzer funcionando",
        "ray_status": "connected" if ray.is_initialized() else "disconnected",
        "available_resources": ray.available_resources() if ray.is_initialized() else {}
    }

@app.post("/analyze-sentiment")
def analyze_sentiment(request: SentimentRequest):
    """Analiza el sentimiento de múltiples textos usando Ray para paralelización"""
    try:
        start_time = time.time()
        
        # Dividir textos en lotes para procesamiento paralelo
        batch_size = max(1, len(request.texts) // 4)  # 4 workers
        text_batches = [request.texts[i:i + batch_size] for i in range(0, len(request.texts), batch_size)]
        
        # Procesar lotes en paralelo con Ray
        logger.info(f"Procesando {len(request.texts)} textos en {len(text_batches)} lotes")
        futures = [process_sentiment_batch.remote(batch) for batch in text_batches]
        results = ray.get(futures)
        
        # Combinar resultados
        all_results = []
        for batch_result in results:
            all_results.extend(batch_result)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Análisis de sentimiento completado para {len(request.texts)} textos",
            "results": all_results,
            "processing_time": processing_time,
            "parallelization": f"Procesado en {len(text_batches)} lotes paralelos"
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de sentimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando sentimientos: {str(e)}")

@app.post("/analyze-tickers")
def analyze_tickers(request: TickerRequest):
    """Analiza métricas de sentimiento para múltiples tickers usando Ray"""
    try:
        start_time = time.time()
        
        # Cargar datos usando Ray
        logger.info("Cargando datos de sentiment con Ray")
        data_future = load_and_process_sentiment_data.remote()
        df = ray.get(data_future)
        
        if df is None:
            raise HTTPException(status_code=500, detail="Error cargando datos de sentiment")
        
        # Procesar cada ticker en paralelo
        ticker_futures = []
        for ticker in request.tickers:
            ticker_data = df[df['ticker'] == ticker]
            if not ticker_data.empty:
                future = calculate_ticker_sentiment.remote(ticker_data)
                ticker_futures.append((ticker, future))
        
        # Obtener resultados
        ticker_results = {}
        for ticker, future in ticker_futures:
            ticker_results[ticker] = ray.get(future)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Análisis completado para {len(request.tickers)} tickers",
            "ticker_analysis": ticker_results,
            "processing_time": processing_time,
            "total_records_processed": len(df),
            "parallelization": f"Procesado {len(ticker_futures)} tickers en paralelo"
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de tickers: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando tickers: {str(e)}")

@app.get("/performance-test")
def performance_test():
    """Test de rendimiento comparando procesamiento serial vs paralelo"""
    try:
        # Generar datos de prueba
        test_texts = [f"Test sentiment analysis text {i}" for i in range(100)]
        
        # Procesamiento serial (simulado)
        start_serial = time.time()
        serial_results = []
        for text in test_texts:
            sentiment_score = np.random.uniform(-1, 1)
            serial_results.append({"text": text, "score": sentiment_score})
        serial_time = time.time() - start_serial
        
        # Procesamiento paralelo con Ray
        start_parallel = time.time()
        batch_size = 25
        text_batches = [test_texts[i:i + batch_size] for i in range(0, len(test_texts), batch_size)]
        futures = [process_sentiment_batch.remote(batch) for batch in text_batches]
        parallel_results = ray.get(futures)
        parallel_time = time.time() - start_parallel
        
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        
        return {
            "test_results": {
                "texts_processed": len(test_texts),
                "serial_time": serial_time,
                "parallel_time": parallel_time,
                "speedup": f"{speedup:.2f}x",
                "efficiency": f"{(speedup/4)*100:.1f}%" if speedup > 0 else "0%"
            },
            "ray_cluster_info": {
                "available_resources": ray.available_resources(),
                "cluster_resources": ray.cluster_resources()
            }
        }
        
    except Exception as e:
        logger.error(f"Error en test de rendimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error en test: {str(e)}")

# Ray Serve Deployment
@serve.deployment
class FastAPIDeployment:
    def __init__(self):
        self.app = app

    def __call__(self, request):
        return self.app

# Para Ray Serve
deployment = FastAPIDeployment.bind()

# Ejecutar con Ray Serve
if __name__ == "__main__":
    import uvicorn
    
    # Iniciar con uvicorn para desarrollo local
    uvicorn.run(app, host="0.0.0.0", port=8000)
