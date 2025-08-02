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
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

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
    """Carga y procesa datos de sentiment de forma paralela"""
    try:
        start_time = time.time()
        
        # Verificar si existe el archivo
        data_file = 'data/sentiment_data.csv'
        
        if os.path.exists(data_file):
            logger.info(f"Cargando datos desde archivo: {data_file}")
            df = pd.read_csv(data_file)
        else:
            # Generar datos sintéticos
            logger.info("Generando datos sintéticos")
            n_records = 10000
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
            
            # IMPORTANTE: Usar nombres de columnas correctos
            df = pd.DataFrame({
                'ticker': np.random.choice(tickers, n_records),  # ✅ Nombre correcto
                'text': [f"Sentiment text for analysis {i}" for i in range(n_records)],
                'sentiment_score': np.random.uniform(-1, 1, n_records),
                'timestamp': pd.date_range('2024-01-01', periods=n_records, freq='1min'),
                'engagement': np.random.randint(1, 1000, n_records),
                'source': np.random.choice(['twitter', 'reddit', 'news'], n_records)
            })
            
            # Guardar para uso futuro
            os.makedirs('data', exist_ok=True)
            df.to_csv(data_file, index=False)
            logger.info(f"Datos guardados en: {data_file}")
        
        logger.info(f"Datos cargados: {len(df)} registros, columnas: {df.columns.tolist()}")
        logger.info(f"Tickers únicos: {df['ticker'].unique().tolist() if 'ticker' in df.columns else 'NO TICKER COLUMN'}")
        return df
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

@ray.remote
def calculate_ticker_sentiment(ticker_data: pd.DataFrame) -> Dict:
    """Calcula métricas de sentimiento para un ticker específico usando las columnas reales del dataset"""
    try:
        metrics = {
            'avg_sentiment': ticker_data['twitterSentiment'].mean(),
            'sentiment_volatility': ticker_data['twitterSentiment'].std(),
            'total_engagement': ticker_data['twitterLikes'].sum() + ticker_data['twitterComments'].sum(),
            'total_posts': ticker_data['twitterPosts'].sum(),
            'total_impressions': ticker_data['twitterImpressions'].sum(),
            'positive_ratio': (ticker_data['twitterSentiment'] > 0.1).mean(),
            'negative_ratio': (ticker_data['twitterSentiment'] < -0.1).mean(),
            'total_records': len(ticker_data)
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

@app.get("/available-tickers")
def get_available_tickers():
    """Obtiene lista de tickers disponibles usando la columna symbol"""
    try:
        data_future = load_and_process_sentiment_data.remote()
        df = ray.get(data_future)
        
        if df is not None:
            if 'symbol' in df.columns:
                available_tickers = df['symbol'].unique().tolist()
                return {
                    "available_tickers": available_tickers,
                    "total_records": len(df),
                    "columns": df.columns.tolist(),
                    "note": "Usando columna 'symbol' como tickers"
                }
            elif 'platform' in df.columns:
                available_platforms = df['platform'].unique().tolist()
                return {
                    "available_platforms": available_platforms,
                    "total_records": len(df),
                    "columns": df.columns.tolist(),
                    "note": "Usando plataformas en lugar de tickers"
                }
            else:
                return {
                    "available_tickers": [],
                    "total_records": len(df),
                    "columns": df.columns.tolist(),
                    "note": "No hay columna ticker o platform disponible"
                }
        else:
            return {"error": "No se pudieron cargar los datos"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug-data")
def debug_data():
    """Debug: Ver estructura de los datos"""
    try:
        data_future = load_and_process_sentiment_data.remote()
        df = ray.get(data_future)
        
        if df is not None:
            # Convertir dtypes a strings para evitar problemas de serialización JSON
            dtypes_dict = {}
            for col in df.columns:
                dtypes_dict[col] = str(df[col].dtype)
            
            # Obtener sample data y manejar valores NaN
            sample_data = df.head(3).fillna("NULL").to_dict('records')
            
            return {
                "columns": df.columns.tolist(),
                "shape": list(df.shape),  # Convertir tuple a list
                "dtypes": dtypes_dict,
                "sample_data": sample_data,
                "unique_tickers": df['ticker'].unique().tolist() if 'ticker' in df.columns else [],
                "has_ticker_column": 'ticker' in df.columns,
                "all_columns": df.columns.tolist()
            }
        else:
            return {"error": "DataFrame es None"}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

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
    """Analiza métricas de sentimiento para múltiples tickers usando la columna symbol"""
    try:
        start_time = time.time()
        
        # Cargar datos usando Ray
        logger.info("Cargando datos de sentiment con Ray")
        data_future = load_and_process_sentiment_data.remote()
        df = ray.get(data_future)
        
        if df is None:
            raise HTTPException(status_code=500, detail="Error cargando datos de sentiment")
        
        # Debug: verificar estructura de datos
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        logger.info(f"DataFrame shape: {df.shape}")
        
        # Verificar que existe la columna symbol
        if 'symbol' not in df.columns:
            raise HTTPException(status_code=500, detail=f"Columna 'symbol' no encontrada. Columnas disponibles: {df.columns.tolist()}")
        
        # Procesar cada ticker usando la columna symbol
        ticker_futures = []
        for ticker in request.tickers:
            try:
                ticker_data = df[df['symbol'] == ticker]
                logger.info(f"Ticker {ticker}: {len(ticker_data)} registros encontrados")
                if not ticker_data.empty:
                    future = calculate_ticker_sentiment.remote(ticker_data)
                    ticker_futures.append((ticker, future))
                else:
                    logger.warning(f"No se encontraron datos para ticker: {ticker}")
            except Exception as ticker_error:
                logger.error(f"Error procesando ticker {ticker}: {ticker_error}")
        
        # Obtener resultados
        ticker_results = {}
        for ticker, future in ticker_futures:
            try:
                ticker_results[ticker] = ray.get(future)
            except Exception as result_error:
                logger.error(f"Error obteniendo resultado para {ticker}: {result_error}")
                ticker_results[ticker] = {"error": str(result_error)}
        
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
    # Iniciar con uvicorn - Ray Remote + FastAPI + Ray Serve
    uvicorn.run(app, host="0.0.0.0", port=8005)
