from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import os
from typing import Dict, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Twitter Sentiment Analyzer", version="1.0.0")

@app.get("/status")
def read_status():
    return {"status": "Twitter Sentiment Analyzer funcionando"}

@app.get("/load-sentiment-data")
def load_sentiment_data():
    """Carga y procesa los datos de sentiment de Twitter"""
    try:
        logger.info("Iniciando carga de datos de sentiment")
        
        # Crear datos sintéticos si no existe el archivo
        csv_file = 'sentiment_data.csv'
        
        if not os.path.exists(csv_file):
            logger.info("Archivo CSV no encontrado, creando datos sintéticos")
            # Crear datos sintéticos
            n_records = 100
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
            
            sentiment_data = {
                'Date': pd.date_range('2024-01-01', periods=n_records, freq='D'),
                'ticker': np.random.choice(tickers, n_records),
                'tweet_likes': np.random.randint(1, 1000, n_records),  # Evitar 0
                'tweet_reposts': np.random.randint(1, 500, n_records), # Evitar 0
                'tweet_replies': np.random.randint(1, 200, n_records), # Evitar 0
                'sentiment_score': np.random.uniform(-1, 1, n_records)
            }
            
            sentiment_df = pd.DataFrame(sentiment_data)
            logger.info(f"Datos sintéticos creados: {len(sentiment_df)} registros")
        else:
            logger.info("Cargando datos desde archivo CSV")
            sentiment_df = pd.read_csv(csv_file)
            logger.info(f"Datos cargados desde CSV: {len(sentiment_df)} registros")
        
        # Verificar que el DataFrame no esté vacío
        if sentiment_df.empty:
            logger.error("DataFrame está vacío")
            raise ValueError("No hay datos para procesar")
        
        # Convertir fecha a datetime si es necesario
        if 'Date' in sentiment_df.columns:
            logger.info("Convirtiendo fechas")
            sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'], errors='coerce')
        
        # Calcular engagement ratio de forma segura
        logger.info("Calculando engagement ratio")
        if all(col in sentiment_df.columns for col in ['tweet_likes', 'tweet_reposts', 'tweet_replies']):
            # Asegurar que no hay valores 0 o negativos
            sentiment_df['tweet_likes'] = sentiment_df['tweet_likes'].clip(lower=1)
            sentiment_df['tweet_reposts'] = sentiment_df['tweet_reposts'].clip(lower=0)
            sentiment_df['tweet_replies'] = sentiment_df['tweet_replies'].clip(lower=0)
            
            sentiment_df['engagement_ratio'] = (
                sentiment_df['tweet_likes'] + 
                sentiment_df['tweet_reposts'] + 
                sentiment_df['tweet_replies']
            ) / sentiment_df['tweet_likes']
        else:
            # Datos sintéticos para engagement
            sentiment_df['engagement_ratio'] = np.random.uniform(1.2, 4.5, len(sentiment_df))
        
        logger.info("Filtrando datos por engagement")
        # Filtrar por engagement (más conservador)
        if 'engagement_ratio' in sentiment_df.columns:
            # Usar mediana en lugar de quantile para ser más seguro
            min_engagement = sentiment_df['engagement_ratio'].median()
            if pd.isna(min_engagement):
                min_engagement = 2.0
            filtered_df = sentiment_df[sentiment_df['engagement_ratio'] >= min_engagement]
        else:
            filtered_df = sentiment_df.copy()
        
        logger.info("Limpiando datos para JSON")
        # LIMPIEZA EXHAUSTIVA PARA JSON
        # 1. Reemplazar infinitos y NaN
        for col in filtered_df.select_dtypes(include=[np.number]).columns:
            filtered_df[col] = filtered_df[col].replace([np.inf, -np.inf], np.nan)
            filtered_df[col] = filtered_df[col].fillna(0)
        
        # 2. Convertir fechas a string de forma segura
        if 'Date' in filtered_df.columns:
            filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 3. Calcular estadísticas de forma segura
        avg_engagement = 0.0
        if 'engagement_ratio' in filtered_df.columns and not filtered_df['engagement_ratio'].empty:
            avg_engagement = float(filtered_df['engagement_ratio'].mean())
            if pd.isna(avg_engagement) or np.isinf(avg_engagement):
                avg_engagement = 0.0
        
        logger.info("Preparando respuesta")
        # 4. Preparar datos de muestra de forma segura
        sample_data = []
        if not filtered_df.empty:
            sample_df = filtered_df.head(5).copy()  # Solo 5 registros para evitar sobrecarga
            
            # Convertir cada registro individualmente para manejar errores
            for idx, row in sample_df.iterrows():
                try:
                    record = {}
                    for col, val in row.items():
                        if pd.isna(val):
                            record[col] = None
                        elif isinstance(val, (np.integer, int)):
                            record[col] = int(val)
                        elif isinstance(val, (np.floating, float)):
                            if np.isinf(val) or np.isnan(val):
                                record[col] = 0.0
                            else:
                                record[col] = float(val)
                        else:
                            record[col] = str(val)
                    sample_data.append(record)
                except Exception as e:
                    logger.warning(f"Error procesando registro {idx}: {e}")
                    continue
        
        response = {
            "message": "Datos de sentiment cargados exitosamente",
            "total_records": int(len(sentiment_df)),
            "filtered_records": int(len(filtered_df)),
            "columns": list(sentiment_df.columns),
            "avg_engagement_ratio": avg_engagement,
            "sample_data": sample_data
        }
        
        logger.info("Respuesta preparada exitosamente")
        return response
        
    except Exception as e:
        logger.error(f"Error en load_sentiment_data: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error cargando datos: {str(e)}")

@app.get("/calculate-engagement/{ticker}")
def calculate_engagement(ticker: str):
    """Calcula el engagement ratio para un ticker específico"""
    try:
        # Simular datos para el ticker específico
        engagement_data = {
            'ticker': ticker,
            'avg_likes': np.random.randint(50, 500),
            'avg_reposts': np.random.randint(20, 200),
            'avg_replies': np.random.randint(10, 100)
        }
        
        total_engagement = (
            engagement_data['avg_likes'] + 
            engagement_data['avg_reposts'] + 
            engagement_data['avg_replies']
        )
        
        engagement_ratio = total_engagement / engagement_data['avg_likes']
        
        return {
            "ticker": ticker,
            "engagement_data": engagement_data,
            "engagement_ratio": engagement_ratio,
            "ranking": "High" if engagement_ratio > 2.5 else "Medium" if engagement_ratio > 1.5 else "Low"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando engagement: {str(e)}")
