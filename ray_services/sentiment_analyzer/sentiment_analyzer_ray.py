"""
Microservicio de Sentiment Analysis optimizado con Ray
Implementa paralelización para procesamiento de múltiples tickers
"""

import ray
from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import os
from typing import Dict, List
import logging
import time
import asyncio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Ray
if not ray.is_initialized():
    ray.init(
        ignore_reinit_error=True,
        include_dashboard=False,  # Deshabilitar dashboard para evitar problemas
        object_store_memory=100000000  # 100MB para object store (mínimo requerido)
    )

app = FastAPI(title="Ray-Powered Sentiment Analyzer", version="2.0.0")

@ray.remote
def process_ticker_sentiment(ticker: str, ticker_data: pd.DataFrame) -> Dict:
    """
    Procesa sentiment para un ticker específico usando Ray
    Esta función se ejecuta en paralelo para cada ticker
    """
    try:
        start_time = time.time()
        
        # Calcular engagement ratio de forma segura
        ticker_data['tweet_likes'] = ticker_data['tweet_likes'].clip(lower=1)
        ticker_data['tweet_reposts'] = ticker_data['tweet_reposts'].clip(lower=0)
        ticker_data['tweet_replies'] = ticker_data['tweet_replies'].clip(lower=0)
        
        engagement_ratio = (
            ticker_data['tweet_likes'] + 
            ticker_data['tweet_reposts'] + 
            ticker_data['tweet_replies']
        ) / ticker_data['tweet_likes']
        
        # Calcular métricas avanzadas
        metrics = {
            'ticker': ticker,
            'total_tweets': len(ticker_data),
            'avg_engagement': float(engagement_ratio.mean()),
            'max_engagement': float(engagement_ratio.max()),
            'min_engagement': float(engagement_ratio.min()),
            'std_engagement': float(engagement_ratio.std()),
            'avg_sentiment': float(ticker_data['sentiment_score'].mean()),
            'positive_sentiment_ratio': float((ticker_data['sentiment_score'] > 0).mean()),
            'negative_sentiment_ratio': float((ticker_data['sentiment_score'] < 0).mean()),
            'processing_time': time.time() - start_time
        }
        
        # Calcular métricas de rolling windows en paralelo
        for window in [7, 14, 30]:
            if len(ticker_data) >= window:
                rolling_engagement = engagement_ratio.rolling(window).mean()
                rolling_sentiment = ticker_data['sentiment_score'].rolling(window).mean()
                
                metrics[f'rolling_{window}d_engagement'] = float(rolling_engagement.mean())
                metrics[f'rolling_{window}d_sentiment'] = float(rolling_sentiment.mean())
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error procesando ticker {ticker}: {e}")
        return {
            'ticker': ticker,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def calculate_engagement_metrics(data_chunk: pd.DataFrame) -> Dict:
    """
    Calcula métricas de engagement para un chunk de datos
    Permite procesamiento paralelo de grandes datasets
    """
    try:
        start_time = time.time()
        
        # Calcular engagement básico
        engagement_ratio = (
            data_chunk['tweet_likes'] + 
            data_chunk['tweet_reposts'] + 
            data_chunk['tweet_replies']
        ) / data_chunk['tweet_likes'].clip(lower=1)
        
        # Métricas estadísticas
        metrics = {
            'chunk_size': len(data_chunk),
            'avg_engagement': float(engagement_ratio.mean()),
            'median_engagement': float(engagement_ratio.median()),
            'p75_engagement': float(engagement_ratio.quantile(0.75)),
            'p90_engagement': float(engagement_ratio.quantile(0.90)),
            'engagement_variance': float(engagement_ratio.var()),
            'processing_time': time.time() - start_time
        }
        
        return metrics
        
    except Exception as e:
        return {
            'error': str(e),
            'chunk_size': len(data_chunk) if data_chunk is not None else 0,
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@app.get("/status")
def read_status():
    """Status del servicio Ray"""
    return {
        "status": "Ray-Powered Sentiment Analyzer funcionando",
        "ray_initialized": ray.is_initialized(),
        "ray_cluster_resources": ray.cluster_resources() if ray.is_initialized() else None
    }

@app.get("/load-sentiment-data")
async def load_sentiment_data():
    """Carga y procesa datos de sentiment usando Ray para paralelización"""
    try:
        logger.info("Iniciando carga de datos con Ray")
        start_time = time.time()
        
        # Crear o cargar datos
        csv_file = 'sentiment_data.csv'
        
        if not os.path.exists(csv_file):
            logger.info("Generando datos sintéticos grandes para demostrar Ray")
            # Crear dataset más grande para mostrar beneficios de Ray
            n_records = 50000  # Incrementamos para mostrar paralelización
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
            
            sentiment_data = {
                'Date': pd.date_range('2023-01-01', periods=n_records, freq='H'),
                'ticker': np.random.choice(tickers, n_records),
                'tweet_likes': np.random.randint(1, 1000, n_records),
                'tweet_reposts': np.random.randint(1, 500, n_records),
                'tweet_replies': np.random.randint(1, 200, n_records),
                'sentiment_score': np.random.uniform(-1, 1, n_records)
            }
            
            sentiment_df = pd.DataFrame(sentiment_data)
            logger.info(f"Datos sintéticos creados: {len(sentiment_df)} registros")
        else:
            logger.info("Cargando datos desde archivo CSV")
            sentiment_df = pd.read_csv(csv_file)
        
        # Convertir fecha si es necesario
        if 'Date' in sentiment_df.columns:
            sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'], errors='coerce')
        
        # PARALELIZACIÓN CON RAY: Procesar cada ticker en paralelo
        logger.info("Iniciando procesamiento paralelo por ticker con Ray")
        
        tickers = sentiment_df['ticker'].unique()
        
        # Crear tareas Ray para cada ticker
        ticker_tasks = []
        for ticker in tickers:
            ticker_data = sentiment_df[sentiment_df['ticker'] == ticker].copy()
            task = process_ticker_sentiment.remote(ticker, ticker_data)
            ticker_tasks.append(task)
        
        # Ejecutar todas las tareas en paralelo y obtener resultados
        ticker_results = ray.get(ticker_tasks)
        
        # PARALELIZACIÓN CON RAY: Procesar chunks de datos para métricas globales
        chunk_size = len(sentiment_df) // 4  # Dividir en 4 chunks
        chunk_tasks = []
        
        for i in range(0, len(sentiment_df), chunk_size):
            chunk = sentiment_df.iloc[i:i + chunk_size].copy()
            task = calculate_engagement_metrics.remote(chunk)
            chunk_tasks.append(task)
        
        chunk_results = ray.get(chunk_tasks)
        
        # Combinar resultados
        total_processing_time = time.time() - start_time
        
        # Calcular métricas globales
        global_metrics = {
            'total_records': len(sentiment_df),
            'unique_tickers': len(tickers),
            'date_range': f"{sentiment_df['Date'].min()} to {sentiment_df['Date'].max()}" if 'Date' in sentiment_df.columns else "N/A",
            'avg_engagement_all_tickers': np.mean([r.get('avg_engagement', 0) for r in ticker_results if 'avg_engagement' in r]),
            'total_processing_time': total_processing_time,
            'parallel_processing_time': max([r.get('processing_time', 0) for r in ticker_results]),
            'speedup_factor': sum([r.get('processing_time', 0) for r in ticker_results]) / total_processing_time if total_processing_time > 0 else 1
        }
        
        response = {
            "message": "Datos procesados exitosamente con Ray",
            "ray_performance": {
                "parallel_tasks_executed": len(ticker_tasks) + len(chunk_tasks),
                "estimated_speedup": f"{global_metrics['speedup_factor']:.2f}x",
                "total_time": f"{total_processing_time:.3f}s",
                "parallel_time": f"{global_metrics['parallel_processing_time']:.3f}s"
            },
            "global_metrics": global_metrics,
            "ticker_results": ticker_results[:5],  # Mostrar solo primeros 5
            "chunk_results": chunk_results,
            "sample_data": sentiment_df.head(3).to_dict('records')
        }
        
        logger.info(f"Procesamiento completado en {total_processing_time:.3f}s con speedup estimado de {global_metrics['speedup_factor']:.2f}x")
        return response
        
    except Exception as e:
        logger.error(f"Error en load_sentiment_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cargando datos: {str(e)}")

@app.get("/calculate-engagement/{ticker}")
async def calculate_engagement(ticker: str):
    """Calcula engagement para un ticker específico usando Ray"""
    try:
        logger.info(f"Calculando engagement para {ticker} con Ray")
        
        # Simular carga de datos del ticker
        n_records = 1000
        ticker_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=n_records, freq='H'),
            'ticker': [ticker] * n_records,
            'tweet_likes': np.random.randint(50, 1000, n_records),
            'tweet_reposts': np.random.randint(20, 500, n_records),
            'tweet_replies': np.random.randint(10, 200, n_records),
            'sentiment_score': np.random.uniform(-1, 1, n_records)
        })
        
        # Usar Ray para procesar
        task = process_ticker_sentiment.remote(ticker, ticker_data)
        result = ray.get(task)
        
        # Añadir ranking y recomendación
        if 'avg_engagement' in result:
            engagement_ratio = result['avg_engagement']
            result['ranking'] = "High" if engagement_ratio > 2.5 else "Medium" if engagement_ratio > 1.5 else "Low"
            result['recommendation'] = "BUY" if engagement_ratio > 3.0 else "HOLD" if engagement_ratio > 2.0 else "SELL"
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculando engagement para {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculando engagement: {str(e)}")

@app.get("/parallel-analysis")
async def parallel_analysis(tickers: str = "AAPL,GOOGL,MSFT,TSLA,NVDA"):
    """
    Análisis paralelo de múltiples tickers
    Demuestra el poder de Ray para procesamiento concurrente
    """
    try:
        ticker_list = [t.strip() for t in tickers.split(',')]
        logger.info(f"Iniciando análisis paralelo para {len(ticker_list)} tickers: {ticker_list}")
        
        start_time = time.time()
        
        # Crear tareas paralelas para cada ticker
        tasks = []
        for ticker in ticker_list:
            # Generar datos sintéticos para cada ticker
            n_records = 2000
            ticker_data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=n_records, freq='30min'),
                'ticker': [ticker] * n_records,
                'tweet_likes': np.random.randint(50, 1000, n_records),
                'tweet_reposts': np.random.randint(20, 500, n_records),
                'tweet_replies': np.random.randint(10, 200, n_records),
                'sentiment_score': np.random.uniform(-1, 1, n_records)
            })
            
            task = process_ticker_sentiment.remote(ticker, ticker_data)
            tasks.append(task)
        
        # Ejecutar todas las tareas en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        # Calcular métricas comparativas
        avg_processing_time = np.mean([r.get('processing_time', 0) for r in results])
        sequential_estimate = sum([r.get('processing_time', 0) for r in results])
        speedup = sequential_estimate / total_time if total_time > 0 else 1
        
        # Ranking de tickers por engagement
        valid_results = [r for r in results if 'avg_engagement' in r]
        ranked_tickers = sorted(valid_results, key=lambda x: x['avg_engagement'], reverse=True)
        
        return {
            "message": f"Análisis paralelo completado para {len(ticker_list)} tickers",
            "performance_metrics": {
                "total_execution_time": f"{total_time:.3f}s",
                "avg_individual_processing_time": f"{avg_processing_time:.3f}s",
                "estimated_sequential_time": f"{sequential_estimate:.3f}s",
                "speedup_achieved": f"{speedup:.2f}x",
                "parallel_efficiency": f"{(speedup / len(ticker_list)) * 100:.1f}%"
            },
            "ticker_ranking": ranked_tickers,
            "top_recommendation": ranked_tickers[0] if ranked_tickers else None,
            "analysis_summary": {
                "tickers_analyzed": len(ticker_list),
                "successful_analyses": len(valid_results),
                "failed_analyses": len(results) - len(valid_results),
                "avg_engagement_across_all": np.mean([r['avg_engagement'] for r in valid_results]) if valid_results else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error en análisis paralelo: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis paralelo: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup cuando se cierra la aplicación"""
    if ray.is_initialized():
        ray.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
