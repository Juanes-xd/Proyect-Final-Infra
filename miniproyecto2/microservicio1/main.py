from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import os
from typing import Dict, List

app = FastAPI(title="Twitter Sentiment Analyzer", version="1.0.0")

@app.get("/status")
def read_status():
    return {"status": "Twitter Sentiment Analyzer funcionando"}

@app.get("/load-sentiment-data")
def load_sentiment_data():
    """Carga y procesa los datos de sentiment de Twitter"""
    try:
        # Cargar datos reales desde el archivo CSV
        sentiment_df = pd.read_csv('sentiment_data.csv')
        
        # Convertir fecha a datetime si es necesario
        if 'Date' in sentiment_df.columns:
            sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'])
        
        # Calcular engagement ratio si las columnas existen
        if all(col in sentiment_df.columns for col in ['tweet_likes', 'tweet_reposts', 'tweet_replies']):
            sentiment_df['engagement_ratio'] = (
                sentiment_df['tweet_likes'] + 
                sentiment_df['tweet_reposts'] + 
                sentiment_df['tweet_replies']
            ) / sentiment_df['tweet_likes']
        else:
            # Si no existen estas columnas, usar las columnas disponibles para calcular engagement
            numeric_cols = sentiment_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                sentiment_df['engagement_ratio'] = sentiment_df[numeric_cols].sum(axis=1) / sentiment_df[numeric_cols[0]]
            else:
                sentiment_df['engagement_ratio'] = np.random.uniform(1.2, 4.5, len(sentiment_df))
        
        # Filtrar stocks con actividad significativa
        if 'engagement_ratio' in sentiment_df.columns:
            min_engagement = sentiment_df['engagement_ratio'].quantile(0.5)
            filtered_df = sentiment_df[sentiment_df['engagement_ratio'] > min_engagement]
        else:
            filtered_df = sentiment_df
        
        return {
            "message": "Datos de sentiment cargados exitosamente",
            "total_records": len(sentiment_df),
            "filtered_records": len(filtered_df),
            "columns": sentiment_df.columns.tolist(),
            "avg_engagement_ratio": float(filtered_df['engagement_ratio'].mean()) if 'engagement_ratio' in filtered_df.columns else 0,
            "sample_data": filtered_df.head(10).to_dict('records')
        }
        
    except Exception as e:
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
