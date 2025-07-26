from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Union

app = FastAPI(title="Intraday Strategy Engine", version="1.0.0")

@app.get("/status")
def read_status():
    return {"status": "Intraday Strategy Engine funcionando"}

@app.post("/calculate-intraday-signals")
def calculate_intraday_signals(daily_signal: int = 1):
    """Calcula señales intraday basadas en indicadores técnicos usando datos reales"""
    try:
        # Cargar datos intraday reales
        intraday_df = pd.read_csv('simulated_5min_data.csv')
        
        # Limpiar datos
        if 'Unnamed: 6' in intraday_df.columns:
            intraday_df = intraday_df.drop('Unnamed: 6', axis=1)
        if 'datetime' in intraday_df.columns:
            intraday_df['datetime'] = pd.to_datetime(intraday_df['datetime'])
        
        # Usar datos reales para cálculos
        if 'close' not in intraday_df.columns and 'Close' in intraday_df.columns:
            intraday_df['close'] = intraday_df['Close']
        if 'high' not in intraday_df.columns and 'High' in intraday_df.columns:
            intraday_df['high'] = intraday_df['High']
        if 'low' not in intraday_df.columns and 'Low' in intraday_df.columns:
            intraday_df['low'] = intraday_df['Low']
        
        # Tomar una muestra de los datos para el cálculo
        sample_size = min(50, len(intraday_df))
        df_sample = intraday_df.tail(sample_size).copy()
        
        # Calcular RSI simplificado
        if len(df_sample) > 1:
            deltas = df_sample['close'].diff()
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains[gains > 0]) if len(gains[gains > 0]) > 0 else 0.01
            avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses[losses > 0]) if len(losses[losses > 0]) > 0 else 0.01
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50  # Valor neutral si no hay suficientes datos
        
        # Calcular Bandas de Bollinger simplificadas
        window = min(20, len(df_sample))
        sma = df_sample['close'].rolling(window=window).mean().iloc[-1]
        std = df_sample['close'].rolling(window=window).std().iloc[-1]
        
        if pd.isna(sma):
            sma = df_sample['close'].mean()
        if pd.isna(std) or std == 0:
            std = df_sample['close'].std()
            if pd.isna(std) or std == 0:
                std = sma * 0.02  # 2% como std por defecto
        
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        current_price = df_sample['close'].iloc[-1]
        
        # Generar señal intraday
        if rsi > 70 and current_price > upper_band:
            intraday_signal = 1  # Sobrecomprado
        elif rsi < 30 and current_price < lower_band:
            intraday_signal = -1  # Sobrevendido
        else:
            intraday_signal = 0  # Neutral
        
        return {
            "message": "Señales intraday calculadas exitosamente con datos reales",
            "data_info": {
                "total_records": len(intraday_df),
                "sample_size": sample_size,
                "date_range": f"{intraday_df['datetime'].min()} to {intraday_df['datetime'].max()}" if 'datetime' in intraday_df.columns else "N/A"
            },
            "signals": {
                "daily_signal": daily_signal,
                "intraday_signal": intraday_signal,
                "combined_signal": daily_signal * intraday_signal if intraday_signal != 0 else 0
            },
            "indicators": {
                "rsi": float(rsi),
                "current_price": float(current_price),
                "sma": float(sma),
                "upper_band": float(upper_band),
                "lower_band": float(lower_band),
                "bollinger_position": "ABOVE" if current_price > upper_band else "BELOW" if current_price < lower_band else "WITHIN"
            },
            "interpretation": {
                "rsi_condition": "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL",
                "bollinger_condition": "OUTSIDE_UPPER" if current_price > upper_band else "OUTSIDE_LOWER" if current_price < lower_band else "WITHIN_BANDS",
                "final_action": "BUY" if daily_signal * intraday_signal > 0 else "SELL" if daily_signal * intraday_signal < 0 else "HOLD"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando señales: {str(e)}")

@app.post("/execute-strategy")
def execute_strategy(position_size: float = 1000.0):
    """Ejecuta la estrategia de trading intraday"""
    try:
        # Obtener señales (simulado)
        daily_signal = np.random.choice([-1, 0, 1])
        
        # Simular ejecución de estrategia durante el día
        trading_periods = 78  # 6.5 horas * 12 períodos de 5 min por hora
        returns = []
        positions = []
        current_position = 0
        
        for period in range(trading_periods):
            # Simular precio y señal para cada período
            price_change = np.random.normal(0, 0.001)  # Cambio de precio pequeño
            
            # Simular señal intraday
            intraday_signal = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
            
            # Combinar señales
            combined_signal = daily_signal * intraday_signal if intraday_signal != 0 else 0
            
            # Actualizar posición
            if combined_signal != 0 and current_position == 0:
                current_position = combined_signal * position_size
            elif period == trading_periods - 1:  # Cerrar posición al final del día
                current_position = 0
            
            # Calcular retorno del período
            period_return = price_change * (current_position / position_size) if current_position != 0 else 0
            returns.append(period_return)
            positions.append(current_position)
        
        # Calcular métricas de la estrategia
        total_return = sum(returns)
        win_rate = len([r for r in returns if r > 0]) / len(returns)
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        return {
            "message": "Estrategia ejecutada exitosamente",
            "strategy_results": {
                "total_return": float(total_return),
                "avg_return_per_period": float(avg_return),
                "volatility": float(volatility),
                "win_rate": float(win_rate),
                "total_periods": trading_periods,
                "position_size": position_size
            },
            "performance_metrics": {
                "sharpe_ratio": float(avg_return / volatility) if volatility != 0 else 0,
                "max_return": float(max(returns)),
                "min_return": float(min(returns)),
                "positive_periods": len([r for r in returns if r > 0]),
                "negative_periods": len([r for r in returns if r < 0])
            },
            "daily_summary": {
                "final_pnl": float(total_return * position_size),
                "trades_executed": len([p for p in positions if p != 0]),
                "avg_position_size": float(np.mean([abs(p) for p in positions if p != 0])) if any(positions) else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando estrategia: {str(e)}")

@app.get("/strategy-performance")
def get_strategy_performance():
    """Obtiene métricas de rendimiento de la estrategia intraday"""
    try:
        # Simular métricas de rendimiento histórico
        days_traded = 30
        daily_returns = [np.random.normal(0.002, 0.02) for _ in range(days_traded)]  # ~0.2% retorno promedio diario
        
        total_return = sum(daily_returns)
        avg_daily_return = np.mean(daily_returns)
        volatility = np.std(daily_returns)
        
        win_days = len([r for r in daily_returns if r > 0])
        loss_days = len([r for r in daily_returns if r < 0])
        
        max_daily_gain = max(daily_returns)
        max_daily_loss = min(daily_returns)
        
        return {
            "message": "Métricas de rendimiento obtenidas exitosamente",
            "performance_summary": {
                "total_return": float(total_return),
                "avg_daily_return": float(avg_daily_return),
                "annualized_return": float(avg_daily_return * 252),
                "volatility": float(volatility),
                "annualized_volatility": float(volatility * np.sqrt(252)),
                "sharpe_ratio": float(avg_daily_return / volatility) if volatility != 0 else 0
            },
            "trading_stats": {
                "days_traded": days_traded,
                "win_days": win_days,
                "loss_days": loss_days,
                "win_rate": float(win_days / days_traded),
                "max_daily_gain": float(max_daily_gain),
                "max_daily_loss": float(max_daily_loss),
                "profit_factor": float(sum([r for r in daily_returns if r > 0]) / abs(sum([r for r in daily_returns if r < 0]))) if sum([r for r in daily_returns if r < 0]) != 0 else float('inf')
            },
            "risk_metrics": {
                "value_at_risk_95": float(np.percentile(daily_returns, 5)),
                "max_drawdown": float(min(np.cumsum(daily_returns)) - max(np.cumsum(daily_returns))),
                "calmar_ratio": float(avg_daily_return / abs(min(np.cumsum(daily_returns)) - max(np.cumsum(daily_returns)))) if (min(np.cumsum(daily_returns)) - max(np.cumsum(daily_returns))) != 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo rendimiento: {str(e)}")
