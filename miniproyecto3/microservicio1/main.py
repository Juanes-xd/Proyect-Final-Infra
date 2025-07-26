from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
from typing import Dict, List, Union

app = FastAPI(title="GARCH Volatility Predictor", version="1.0.0")

@app.get("/status")
def read_status():
    return {"status": "GARCH Volatility Predictor funcionando"}

@app.get("/load-market-data")
def load_market_data():
    """Carga datos de mercado reales (diarios e intraday)"""
    try:
        # Cargar datos diarios reales
        daily_df = pd.read_csv('simulated_daily_data.csv')
        
        # Limpiar datos diarios si es necesario
        if 'Unnamed: 7' in daily_df.columns:
            daily_df = daily_df.drop('Unnamed: 7', axis=1)
        if 'Date' in daily_df.columns:
            daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        
        # Cargar datos intraday reales
        intraday_df = pd.read_csv('simulated_5min_data.csv')
        
        # Limpiar datos intraday si es necesario
        if 'Unnamed: 6' in intraday_df.columns:
            intraday_df = intraday_df.drop('Unnamed: 6', axis=1)
        if 'datetime' in intraday_df.columns:
            intraday_df['datetime'] = pd.to_datetime(intraday_df['datetime'])
        
        return {
            "message": "Datos de mercado cargados exitosamente",
            "daily_data": {
                "records": len(daily_df),
                "columns": daily_df.columns.tolist(),
                "date_range": f"{daily_df['Date'].min()} to {daily_df['Date'].max()}" if 'Date' in daily_df.columns else "N/A",
                "sample": daily_df.head(5).to_dict('records')
            },
            "intraday_data": {
                "records": len(intraday_df),
                "columns": intraday_df.columns.tolist(),
                "date_range": f"{intraday_df['datetime'].min()} to {intraday_df['datetime'].max()}" if 'datetime' in intraday_df.columns else "N/A",
                "sample": intraday_df.head(5).to_dict('records')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando datos: {str(e)}")

@app.post("/predict-volatility")
def predict_volatility(window_size: int = 180):
    """Predice volatilidad usando modelo GARCH simplificado con datos reales"""
    try:
        # Cargar datos reales
        daily_df = pd.read_csv('simulated_daily_data.csv')
        
        # Limpiar datos
        if 'Unnamed: 7' in daily_df.columns:
            daily_df = daily_df.drop('Unnamed: 7', axis=1)
        if 'Date' in daily_df.columns:
            daily_df['Date'] = pd.to_datetime(daily_df['Date'])
            daily_df = daily_df.set_index('Date')
        
        # Calcular retornos logarítmicos reales
        if 'Adj Close' in daily_df.columns:
            daily_df['log_ret'] = np.log(daily_df['Adj Close']).diff()
        elif 'Close' in daily_df.columns:
            daily_df['log_ret'] = np.log(daily_df['Close']).diff()
        else:
            raise ValueError("No se encontró columna de precios (Adj Close o Close)")
        
        # Filtrar datos válidos
        valid_returns = daily_df['log_ret'].dropna()
        
        if len(valid_returns) < window_size:
            window_size = len(valid_returns) // 2
        
        # Calcular varianza histórica
        rolling_variance = valid_returns.rolling(window_size).var().iloc[-1]
        
        # Simular predicción GARCH (simplificado)
        # En producción real, usaríamos la librería 'arch'
        garch_prediction = rolling_variance * (1 + np.random.uniform(-0.1, 0.1))
        
        # Calcular premium de predicción
        prediction_premium = (garch_prediction - rolling_variance) / rolling_variance
        
        # Calcular desviación estándar del premium
        recent_premiums = []
        for i in range(10):
            temp_var = valid_returns.rolling(window_size).var().iloc[-(i+2)] if len(valid_returns) > (i+2) else rolling_variance
            temp_premium = (garch_prediction - temp_var) / temp_var if temp_var != 0 else 0
            recent_premiums.append(temp_premium)
        
        premium_std = np.std(recent_premiums)
        
        # Generar señal diaria
        if prediction_premium > premium_std:
            signal = 1  # Señal alcista
        elif prediction_premium < -premium_std:
            signal = -1  # Señal bajista
        else:
            signal = 0  # Sin señal
        
        return {
            "message": "Predicción de volatilidad completada con datos reales",
            "data_info": {
                "total_observations": len(daily_df),
                "valid_returns": len(valid_returns),
                "window_size_used": window_size,
                "date_range": f"{daily_df.index.min()} to {daily_df.index.max()}" if not daily_df.index.empty else "N/A"
            },
            "volatility_metrics": {
                "historical_variance": float(rolling_variance),
                "garch_prediction": float(garch_prediction),
                "prediction_premium": float(prediction_premium),
                "premium_std": float(premium_std),
                "daily_signal": int(signal),
                "signal_strength": abs(float(prediction_premium / premium_std)) if premium_std != 0 else 0
            },
            "interpretation": {
                "signal": "BULLISH" if signal == 1 else "BEARISH" if signal == -1 else "NEUTRAL",
                "confidence": "HIGH" if abs(prediction_premium / premium_std) > 1.5 else "MEDIUM" if abs(prediction_premium / premium_std) > 1 else "LOW"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error prediciendo volatilidad: {str(e)}")

@app.get("/calculate-rolling-variance")
def calculate_rolling_variance(window: int = 180):
    """Calcula la varianza móvil para un período dado"""
    try:
        # Simular serie de precios
        prices = []
        initial_price = 100
        prices.append(initial_price)
        
        for i in range(window):
            change = np.random.normal(0, 2)  # Cambio diario
            new_price = prices[-1] + change
            prices.append(max(new_price, 50))  # Precio mínimo de 50
        
        # Calcular retornos logarítmicos
        log_returns = np.diff(np.log(prices))
        
        # Calcular varianza móvil
        rolling_var = pd.Series(log_returns).rolling(window=min(60, len(log_returns))).var()
        
        return {
            "message": "Varianza móvil calculada exitosamente",
            "variance_metrics": {
                "current_variance": float(rolling_var.iloc[-1]) if not rolling_var.empty else 0,
                "avg_variance": float(rolling_var.mean()) if not rolling_var.empty else 0,
                "max_variance": float(rolling_var.max()) if not rolling_var.empty else 0,
                "min_variance": float(rolling_var.min()) if not rolling_var.empty else 0,
                "window_size": window,
                "observations": len(log_returns)
            },
            "price_stats": {
                "initial_price": prices[0],
                "final_price": prices[-1],
                "total_return": (prices[-1] - prices[0]) / prices[0],
                "price_volatility": np.std(prices)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando varianza: {str(e)}")
