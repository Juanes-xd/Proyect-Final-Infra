"""
Microservicio GARCH optimizado con Ray
Implementa paralelización para predicción de volatilidad en múltiples assets
"""

import ray
from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional
import logging
import time

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

app = FastAPI(title="Ray-Powered GARCH Predictor", version="2.0.0")

@ray.remote
def calculate_garch_volatility(returns: np.ndarray, window_size: int = 180, asset_name: str = "Asset") -> Dict:
    """
    Calcula volatilidad GARCH para un asset específico usando Ray
    Esta función se ejecuta en paralelo para cada asset
    """
    try:
        start_time = time.time()
        
        if len(returns) < window_size:
            window_size = len(returns) // 2
        
        if window_size < 10:
            raise ValueError(f"Insuficientes datos para {asset_name}: {len(returns)} returns")
        
        # Calcular varianza histórica móvil
        rolling_variance = pd.Series(returns).rolling(window_size).var()
        
        # Modelo GARCH simplificado pero realista
        # Parámetros GARCH típicos
        alpha = 0.1  # Peso de los shocks recientes
        beta = 0.85  # Peso de la varianza condicional anterior
        omega = 0.05  # Término constante
        
        # Calcular varianza condicional GARCH
        garch_variance = []
        current_var = rolling_variance.dropna().iloc[0] if len(rolling_variance.dropna()) > 0 else 0.01
        
        for i, ret in enumerate(returns):
            if i >= window_size:
                # GARCH(1,1): σ²t = ω + α*ε²t-1 + β*σ²t-1
                new_var = omega + alpha * (ret ** 2) + beta * current_var
                garch_variance.append(new_var)
                current_var = new_var
        
        if not garch_variance:
            garch_variance = [current_var]
        
        # Predicción de volatilidad (siguiente período)
        next_var_prediction = omega + alpha * (returns[-1] ** 2) + beta * garch_variance[-1]
        next_vol_prediction = np.sqrt(next_var_prediction * 252)  # Anualizada
        
        # Calcular métricas adicionales
        historical_vol = np.std(returns) * np.sqrt(252)
        current_vol = np.sqrt(garch_variance[-1] * 252) if garch_variance else historical_vol
        
        # Generar señal de trading basada en volatilidad
        vol_percentile = np.percentile([np.sqrt(v * 252) for v in garch_variance], 50) if garch_variance else historical_vol
        
        if next_vol_prediction > vol_percentile * 1.2:
            signal = -1  # Alta volatilidad -> señal bajista
            signal_strength = min((next_vol_prediction / vol_percentile - 1) * 2, 1.0)
        elif next_vol_prediction < vol_percentile * 0.8:
            signal = 1   # Baja volatilidad -> señal alcista
            signal_strength = min((1 - next_vol_prediction / vol_percentile) * 2, 1.0)
        else:
            signal = 0   # Volatilidad normal
            signal_strength = 0.0
        
        result = {
            'asset': asset_name,
            'observations_used': len(returns),
            'window_size': window_size,
            'historical_volatility': float(historical_vol),
            'current_volatility': float(current_vol),
            'predicted_volatility': float(next_vol_prediction),
            'volatility_percentile': float(vol_percentile),
            'trading_signal': int(signal),
            'signal_strength': float(signal_strength),
            'signal_interpretation': 'BULLISH' if signal == 1 else 'BEARISH' if signal == -1 else 'NEUTRAL',
            'volatility_regime': 'HIGH' if current_vol > vol_percentile * 1.2 else 'LOW' if current_vol < vol_percentile * 0.8 else 'NORMAL',
            'processing_time': time.time() - start_time
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculando GARCH para {asset_name}: {e}")
        return {
            'asset': asset_name,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def process_market_data_chunk(data_chunk: pd.DataFrame, chunk_id: int) -> Dict:
    """
    Procesa un chunk de datos de mercado en paralelo
    """
    try:
        start_time = time.time()
        
        # Calcular retornos si no existen
        if 'log_ret' not in data_chunk.columns:
            if 'Adj Close' in data_chunk.columns:
                data_chunk['log_ret'] = np.log(data_chunk['Adj Close']).diff()
            elif 'Close' in data_chunk.columns:
                data_chunk['log_ret'] = np.log(data_chunk['Close']).diff()
        
        valid_returns = data_chunk['log_ret'].dropna()
        
        if len(valid_returns) < 10:
            return {
                'chunk_id': chunk_id,
                'error': 'Insuficientes datos válidos',
                'processing_time': time.time() - start_time
            }
        
        # Calcular estadísticas del chunk
        metrics = {
            'chunk_id': chunk_id,
            'chunk_size': len(data_chunk),
            'valid_returns': len(valid_returns),
            'mean_return': float(valid_returns.mean()),
            'volatility': float(valid_returns.std() * np.sqrt(252)),
            'min_return': float(valid_returns.min()),
            'max_return': float(valid_returns.max()),
            'skewness': float(valid_returns.skew()) if len(valid_returns) > 2 else 0,
            'kurtosis': float(valid_returns.kurtosis()) if len(valid_returns) > 3 else 0,
            'processing_time': time.time() - start_time
        }
        
        return metrics
        
    except Exception as e:
        return {
            'chunk_id': chunk_id,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def generate_multiple_volatility_forecasts(returns: np.ndarray, horizons: List[int] = [1, 5, 10, 22]) -> Dict:
    """
    Genera pronósticos de volatilidad para múltiples horizontes temporales
    """
    try:
        start_time = time.time()
        
        forecasts = {}
        
        for horizon in horizons:
            # Parámetros GARCH
            alpha, beta, omega = 0.1, 0.85, 0.05
            
            # Calcular pronóstico para cada horizonte
            if horizon == 1:
                # Un período adelante
                forecast_var = omega + alpha * (returns[-1] ** 2) + beta * np.var(returns[-30:]) if len(returns) >= 30 else np.var(returns)
            else:
                # Múltiples períodos adelante (converge a varianza incondicional)
                unconditional_var = omega / (1 - alpha - beta)
                current_var = np.var(returns[-30:]) if len(returns) >= 30 else np.var(returns)
                
                # Decaimiento exponencial hacia varianza incondicional
                decay_factor = (alpha + beta) ** (horizon - 1)
                forecast_var = unconditional_var + decay_factor * (current_var - unconditional_var)
            
            forecast_vol = np.sqrt(forecast_var * 252)  # Anualizada
            
            forecasts[f'horizon_{horizon}d'] = {
                'volatility': float(forecast_vol),
                'variance': float(forecast_var),
                'confidence_level': max(0.5, 1.0 - (horizon - 1) * 0.1)  # Menor confianza para horizontes más largos
            }
        
        return {
            'forecasts': forecasts,
            'base_volatility': float(np.std(returns) * np.sqrt(252)),
            'processing_time': time.time() - start_time
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@app.get("/status")
def read_status():
    """Status del servicio Ray GARCH"""
    return {
        "status": "Ray-Powered GARCH Predictor funcionando",
        "ray_initialized": ray.is_initialized(),
        "ray_cluster_resources": ray.cluster_resources() if ray.is_initialized() else None
    }

@app.get("/load-market-data")
async def load_market_data():
    """Carga datos de mercado usando Ray para procesamiento paralelo"""
    try:
        logger.info("Cargando datos de mercado con Ray")
        start_time = time.time()
        
        # Cargar datos reales si existen
        daily_file = 'simulated_daily_data.csv'
        intraday_file = 'simulated_5min_data.csv'
        
        daily_df = None
        intraday_df = None
        
        if os.path.exists(daily_file):
            daily_df = pd.read_csv(daily_file)
            if 'Unnamed: 7' in daily_df.columns:
                daily_df = daily_df.drop('Unnamed: 7', axis=1)
            if 'Date' in daily_df.columns:
                daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        
        if os.path.exists(intraday_file):
            intraday_df = pd.read_csv(intraday_file)
            if 'Unnamed: 6' in intraday_df.columns:
                intraday_df = intraday_df.drop('Unnamed: 6', axis=1)
            if 'datetime' in intraday_df.columns:
                intraday_df['datetime'] = pd.to_datetime(intraday_df['datetime'])
        
        # Si no hay datos reales, crear sintéticos más grandes
        if daily_df is None:
            logger.info("Generando datos diarios sintéticos para demostrar Ray")
            n_days = 2000
            dates = pd.date_range('2020-01-01', periods=n_days, freq='D')
            
            # Simular precios con random walk
            prices = [100]
            for _ in range(n_days - 1):
                change = np.random.normal(0.0005, 0.02)  # Drift y volatilidad realistas
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            daily_df = pd.DataFrame({
                'Date': dates,
                'Open': prices,
                'High': [p * np.random.uniform(1.0, 1.05) for p in prices],
                'Low': [p * np.random.uniform(0.95, 1.0) for p in prices],
                'Close': prices,
                'Adj Close': prices,
                'Volume': np.random.randint(1000000, 10000000, n_days)
            })
        
        # PARALELIZACIÓN CON RAY: Procesar datos en chunks
        chunk_size = len(daily_df) // 4
        chunk_tasks = []
        
        for i in range(0, len(daily_df), chunk_size):
            chunk = daily_df.iloc[i:i + chunk_size].copy()
            task = process_market_data_chunk.remote(chunk, i // chunk_size)
            chunk_tasks.append(task)
        
        chunk_results = ray.get(chunk_tasks)
        
        total_time = time.time() - start_time
        
        return {
            "message": "Datos de mercado procesados con Ray",
            "ray_performance": {
                "chunks_processed": len(chunk_tasks),
                "total_processing_time": f"{total_time:.3f}s",
                "average_chunk_time": f"{np.mean([r.get('processing_time', 0) for r in chunk_results]):.3f}s"
            },
            "daily_data": {
                "records": len(daily_df),
                "columns": daily_df.columns.tolist(),
                "date_range": f"{daily_df['Date'].min()} to {daily_df['Date'].max()}" if 'Date' in daily_df.columns else "N/A",
                "sample": daily_df.head(3).to_dict('records')
            },
            "intraday_data": {
                "records": len(intraday_df) if intraday_df is not None else 0,
                "available": intraday_df is not None
            },
            "chunk_analysis": chunk_results
        }
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error cargando datos: {str(e)}")

@app.post("/predict-volatility")
async def predict_volatility(window_size: int = 180, assets: Optional[str] = None):
    """Predice volatilidad usando modelo GARCH paralelo con Ray"""
    try:
        logger.info("Iniciando predicción de volatilidad con Ray")
        start_time = time.time()
        
        # Cargar datos
        daily_file = 'simulated_daily_data.csv'
        
        if os.path.exists(daily_file):
            daily_df = pd.read_csv(daily_file)
            if 'Unnamed: 7' in daily_df.columns:
                daily_df = daily_df.drop('Unnamed: 7', axis=1)
            if 'Date' in daily_df.columns:
                daily_df['Date'] = pd.to_datetime(daily_df['Date'])
                daily_df = daily_df.set_index('Date')
        else:
            # Generar múltiples assets sintéticos para demostrar paralelización
            n_days = 1000
            asset_names = assets.split(',') if assets else ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
            
            # Simular múltiples series de precios
            all_data = {}
            dates = pd.date_range('2021-01-01', periods=n_days, freq='D')
            
            for asset in asset_names:
                # Cada asset tiene características diferentes
                drift = np.random.uniform(-0.0005, 0.001)
                vol = np.random.uniform(0.15, 0.4)
                
                prices = [100]
                for _ in range(n_days - 1):
                    change = np.random.normal(drift, vol / np.sqrt(252))
                    new_price = prices[-1] * (1 + change)
                    prices.append(new_price)
                
                all_data[asset] = prices
            
            daily_df = pd.DataFrame(all_data, index=dates)
        
        # Preparar datos para Ray
        if isinstance(daily_df.columns, pd.RangeIndex) or 'Close' in daily_df.columns:
            # Si es un solo asset
            price_column = 'Adj Close' if 'Adj Close' in daily_df.columns else 'Close' if 'Close' in daily_df.columns else daily_df.columns[0]
            returns = np.log(daily_df[price_column]).diff().dropna().values
            
            # Usar Ray para una sola predicción
            task = calculate_garch_volatility.remote(returns, window_size, "Single_Asset")
            result = ray.get(task)
            
            # Generar pronósticos múltiples horizons
            forecast_task = generate_multiple_volatility_forecasts.remote(returns)
            forecast_result = ray.get(forecast_task)
            
            total_time = time.time() - start_time
            
            return {
                "message": "Predicción GARCH completada con Ray",
                "single_asset_prediction": result,
                "multi_horizon_forecasts": forecast_result,
                "performance": {
                    "total_time": f"{total_time:.3f}s",
                    "processing_time": f"{result.get('processing_time', 0):.3f}s"
                }
            }
        
        else:
            # Múltiples assets - PARALELIZACIÓN COMPLETA
            logger.info(f"Procesando {len(daily_df.columns)} assets en paralelo")
            
            tasks = []
            asset_names = daily_df.columns.tolist()
            
            for asset in asset_names:
                returns = np.log(daily_df[asset]).diff().dropna().values
                if len(returns) >= 50:  # Mínimo para GARCH
                    task = calculate_garch_volatility.remote(returns, window_size, asset)
                    tasks.append(task)
            
            # Ejecutar todas las predicciones en paralelo
            results = ray.get(tasks)
            
            # Generar pronósticos multi-horizonte para el primer asset
            first_asset_returns = np.log(daily_df.iloc[:, 0]).diff().dropna().values
            forecast_task = generate_multiple_volatility_forecasts.remote(first_asset_returns)
            forecast_result = ray.get(forecast_task)
            
            total_time = time.time() - start_time
            
            # Calcular métricas agregadas
            valid_results = [r for r in results if 'error' not in r]
            avg_vol = np.mean([r['predicted_volatility'] for r in valid_results]) if valid_results else 0
            
            # Ranking por volatilidad
            volatility_ranking = sorted(valid_results, key=lambda x: x['predicted_volatility'], reverse=True)
            
            return {
                "message": f"Predicción GARCH paralela completada para {len(tasks)} assets",
                "ray_performance": {
                    "assets_processed": len(tasks),
                    "successful_predictions": len(valid_results),
                    "failed_predictions": len(results) - len(valid_results),
                    "total_time": f"{total_time:.3f}s",
                    "avg_processing_time": f"{np.mean([r.get('processing_time', 0) for r in results]):.3f}s",
                    "estimated_sequential_time": f"{sum([r.get('processing_time', 0) for r in results]):.3f}s",
                    "speedup": f"{sum([r.get('processing_time', 0) for r in results]) / total_time:.2f}x"
                },
                "market_analysis": {
                    "average_predicted_volatility": float(avg_vol),
                    "highest_volatility_asset": volatility_ranking[0] if volatility_ranking else None,
                    "lowest_volatility_asset": volatility_ranking[-1] if volatility_ranking else None,
                    "high_vol_assets": [r['asset'] for r in volatility_ranking[:3]],
                    "low_vol_assets": [r['asset'] for r in volatility_ranking[-3:]]
                },
                "multi_horizon_forecast": forecast_result,
                "detailed_results": valid_results[:5]  # Mostrar solo los primeros 5
            }
        
    except Exception as e:
        logger.error(f"Error en predicción GARCH: {e}")
        raise HTTPException(status_code=500, detail=f"Error prediciendo volatilidad: {str(e)}")

@app.get("/calculate-rolling-variance")
async def calculate_rolling_variance(window: int = 180, n_simulations: int = 5):
    """Calcula varianza móvil para múltiples simulaciones usando Ray"""
    try:
        logger.info(f"Calculando varianza móvil para {n_simulations} simulaciones con Ray")
        
        # PARALELIZACIÓN: Crear múltiples simulaciones en paralelo
        @ray.remote
        def simulate_price_series(simulation_id: int, n_periods: int = 500) -> Dict:
            start_time = time.time()
            
            # Simular serie de precios única para cada simulación
            prices = [100]
            drift = np.random.uniform(-0.0005, 0.001)
            vol = np.random.uniform(0.15, 0.35)
            
            for _ in range(n_periods):
                change = np.random.normal(drift, vol / np.sqrt(252))
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 10))  # Precio mínimo
            
            # Calcular retornos y varianza móvil
            log_returns = np.diff(np.log(prices))
            rolling_var = pd.Series(log_returns).rolling(window=min(window, len(log_returns))).var()
            
            return {
                'simulation_id': simulation_id,
                'final_price': prices[-1],
                'total_return': (prices[-1] - prices[0]) / prices[0],
                'current_variance': float(rolling_var.iloc[-1]) if not rolling_var.empty else 0,
                'avg_variance': float(rolling_var.mean()) if not rolling_var.empty else 0,
                'max_variance': float(rolling_var.max()) if not rolling_var.empty else 0,
                'min_variance': float(rolling_var.min()) if not rolling_var.empty else 0,
                'volatility_regime': 'HIGH' if rolling_var.iloc[-1] > rolling_var.quantile(0.75) else 'LOW' if rolling_var.iloc[-1] < rolling_var.quantile(0.25) else 'NORMAL',
                'processing_time': time.time() - start_time
            }
        
        start_time = time.time()
        
        # Crear tareas paralelas
        simulation_tasks = []
        for i in range(n_simulations):
            task = simulate_price_series.remote(i, 500 + i * 100)  # Diferentes longitudes
            simulation_tasks.append(task)
        
        # Ejecutar simulaciones en paralelo
        simulation_results = ray.get(simulation_tasks)
        
        total_time = time.time() - start_time
        
        # Analizar resultados agregados
        avg_variance = np.mean([r['current_variance'] for r in simulation_results])
        avg_return = np.mean([r['total_return'] for r in simulation_results])
        
        return {
            "message": f"Varianza móvil calculada para {n_simulations} simulaciones",
            "ray_performance": {
                "simulations_completed": len(simulation_results),
                "total_time": f"{total_time:.3f}s",
                "avg_simulation_time": f"{np.mean([r['processing_time'] for r in simulation_results]):.3f}s",
                "estimated_sequential_time": f"{sum([r['processing_time'] for r in simulation_results]):.3f}s",
                "speedup": f"{sum([r['processing_time'] for r in simulation_results]) / total_time:.2f}x"
            },
            "aggregate_metrics": {
                "window_size": window,
                "average_variance": float(avg_variance),
                "average_return": float(avg_return),
                "variance_std": float(np.std([r['current_variance'] for r in simulation_results])),
                "return_std": float(np.std([r['total_return'] for r in simulation_results]))
            },
            "simulation_results": simulation_results,
            "risk_assessment": {
                "high_variance_simulations": len([r for r in simulation_results if r['volatility_regime'] == 'HIGH']),
                "normal_variance_simulations": len([r for r in simulation_results if r['volatility_regime'] == 'NORMAL']),
                "low_variance_simulations": len([r for r in simulation_results if r['volatility_regime'] == 'LOW']),
                "overall_risk_level": "HIGH" if avg_variance > 0.0004 else "LOW" if avg_variance < 0.0001 else "MEDIUM"
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculando varianza: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculando varianza: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup Ray al cerrar"""
    if ray.is_initialized():
        ray.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
