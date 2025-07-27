"""
Microservicio de Sentiment Analysis optimizado con Ray Serve
Implementa paralelización para procesamiento de múltiples tickers
"""

import ray
from ray import serve
import pandas as pd
import numpy as np
import os
from typing import Dict
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Ray y Ray Serve
ray.init()
serve.start()

@serve.deployment(route_prefix="/")
@serve.ingress
class SentimentAnalyzer:
    def __init__(self):
        self.data = None

    def load_sentiment_data(self):
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
                    'tweet_replies': np.random.randint(1, 200, n_records),
                    'sentiment_score': np.random.uniform(-1, 1, n_records)
                }

                self.data = pd.DataFrame(sentiment_data)
                logger.info(f"Datos sintéticos creados: {len(self.data)} registros")
            else:
                logger.info("Cargando datos desde archivo CSV")
                self.data = pd.read_csv(csv_file)

            if self.data.empty:
                raise ValueError("No hay datos para procesar")

            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')
            self.data['engagement_ratio'] = (
                self.data['tweet_likes'] + 
                self.data['tweet_reposts'] + 
                self.data['tweet_replies']
            ) / self.data['tweet_likes']

            return {"message": "Datos cargados exitosamente", "total_records": len(self.data)}
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            return {"error": str(e)}

    async def calculate_engagement(self, ticker: str) -> Dict:
        """Calcula el engagement ratio para un ticker específico."""
        try:
            if self.data is None:
                raise ValueError("Los datos no están cargados. Usa /load-sentiment-data primero.")

            ticker_data = self.data[self.data["ticker"] == ticker]
            if ticker_data.empty:
                raise ValueError(f"No se encontraron datos para el ticker {ticker}.")

            engagement_ratio = (
                ticker_data["tweet_likes"].sum() +
                ticker_data["tweet_reposts"].sum() +
                ticker_data["tweet_replies"].sum()
            ) / len(ticker_data)

            return {
                "ticker": ticker,
                "engagement_ratio": engagement_ratio,
                "ranking": "High" if engagement_ratio > 2.5 else "Medium" if engagement_ratio > 1.5 else "Low"
            }
        except Exception as e:
            logger.error(f"Error calculando engagement: {str(e)}")
            return {"error": str(e)}

    async def __call__(self, request):
        """Maneja las solicitudes HTTP."""
        path = request.path
        if path == "/load-sentiment-data":
            return self.load_sentiment_data()
        elif path.startswith("/calculate-engagement/"):
            ticker = path.split("/")[-1]
            return await self.calculate_engagement(ticker)
        else:
            return {"error": "Ruta no encontrada"}

# Desplegar el servicio
SentimentAnalyzer.deploy()
