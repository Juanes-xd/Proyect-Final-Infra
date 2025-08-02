"""
Microservicio Intraday Strategy optimizado con Ray + FastAPI
Implementa paralelización para estrategias de trading intradía
"""

import ray
from ray import serve
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional
import logging
import time
from datetime import datetime
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
app = FastAPI(title="Ray Intraday Strategy Engine", version="1.0.0")

# Modelos Pydantic
class StrategyRequest(BaseModel):
    strategies: List[str]
    symbols: Optional[List[str]] = None

class BacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SignalRequest(BaseModel):
    symbols: List[str]
    strategy_type: Optional[str] = "momentum"

# Funciones Ray remotas para paralelización
@ray.remote
def execute_strategy_parallel(strategy_name: str, market_data: pd.DataFrame, symbol: str) -> Dict:
    """Ejecuta una estrategia de trading en paralelo"""
    try:
        start_time = time.time()
        
        # Estrategias simuladas
        if strategy_name == "momentum":
            # Estrategia de momentum
            returns = market_data['Close'].pct_change()
            signals = np.where(returns > returns.rolling(10).mean(), 1, -1)
            
        elif strategy_name == "mean_reversion":
            # Estrategia de reversión a la media
            prices = market_data['Close']
            moving_avg = prices.rolling(20).mean()
            signals = np.where(prices < moving_avg * 0.98, 1, 
                             np.where(prices > moving_avg * 1.02, -1, 0))
            
        elif strategy_name == "breakout":
            # Estrategia de breakout
            high_20 = market_data['High'].rolling(20).max()
            low_20 = market_data['Low'].rolling(20).min()
            signals = np.where(market_data['Close'] > high_20.shift(1), 1,
                             np.where(market_data['Close'] < low_20.shift(1), -1, 0))
            
        else:
            # Estrategia aleatoria por defecto
            signals = np.random.choice([-1, 0, 1], size=len(market_data), p=[0.3, 0.4, 0.3])
        
        # Calcular métricas de rendimiento
        returns = market_data['Close'].pct_change()
        strategy_returns = returns * np.roll(signals, 1)  # Señales del día anterior
        
        total_return = (1 + strategy_returns).prod() - 1
        volatility = strategy_returns.std() * np.sqrt(252)
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
        max_drawdown = (strategy_returns.cumsum() - strategy_returns.cumsum().expanding().max()).min()
        
        # Contar señales
        buy_signals = np.sum(signals == 1)
        sell_signals = np.sum(signals == -1)
        hold_signals = np.sum(signals == 0)
        
        processing_time = time.time() - start_time
        
        return {
            'strategy': strategy_name,
            'symbol': symbol,
            'total_return': float(total_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'buy_signals': int(buy_signals),
            'sell_signals': int(sell_signals),
            'hold_signals': int(hold_signals),
            'win_rate': float(np.random.uniform(0.45, 0.65)),  # Simulado
            'profit_factor': float(np.random.uniform(1.1, 1.8)),  # Simulado
            'processing_time': processing_time,
            'data_points': len(market_data)
        }
        
    except Exception as e:
        logger.error(f"Error ejecutando estrategia {strategy_name} para {symbol}: {e}")
        return {
            'strategy': strategy_name,
            'symbol': symbol,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def generate_trading_signals(symbol: str, strategy_type: str = "momentum") -> Dict:
    """Genera señales de trading para un símbolo específico"""
    try:
        start_time = time.time()
        
        # Simular datos de mercado intradía
        current_time = datetime.now()
        timestamps = pd.date_range(start=current_time.replace(hour=9, minute=30), 
                                 end=current_time.replace(hour=16, minute=0), 
                                 freq='5min')
        
        # Generar precios simulados
        n_points = len(timestamps)
        base_price = np.random.uniform(50, 200)
        price_changes = np.random.normal(0, 0.001, n_points)
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1))  # Precio mínimo de $1
        
        # Generar señales según estrategia
        if strategy_type == "momentum":
            # Señales basadas en momentum
            short_ma = pd.Series(prices).rolling(5).mean()
            long_ma = pd.Series(prices).rolling(15).mean()
            current_signal = 1 if short_ma.iloc[-1] > long_ma.iloc[-1] else -1
            signal_strength = abs(short_ma.iloc[-1] - long_ma.iloc[-1]) / long_ma.iloc[-1]
            
        elif strategy_type == "volatility":
            # Señales basadas en volatilidad
            returns = pd.Series(prices).pct_change()
            volatility = returns.rolling(10).std()
            current_signal = -1 if volatility.iloc[-1] > volatility.quantile(0.8) else 1
            signal_strength = volatility.iloc[-1] / volatility.mean() - 1
            
        else:  # mean_reversion
            # Señales de reversión a la media
            mean_price = np.mean(prices[-20:])
            current_price = prices[-1]
            deviation = (current_price - mean_price) / mean_price
            current_signal = -1 if deviation > 0.02 else 1 if deviation < -0.02 else 0
            signal_strength = abs(deviation)
        
        processing_time = time.time() - start_time
        
        return {
            'symbol': symbol,
            'strategy_type': strategy_type,
            'current_signal': int(current_signal),
            'signal_strength': float(signal_strength),
            'current_price': float(prices[-1]),
            'price_change_pct': float((prices[-1] - prices[0]) / prices[0] * 100),
            'volume_profile': 'HIGH' if np.random.random() > 0.5 else 'NORMAL',
            'confidence': float(np.random.uniform(0.6, 0.95)),
            'timestamp': current_time.isoformat(),
            'processing_time': processing_time,
            'data_points': n_points
        }
        
    except Exception as e:
        logger.error(f"Error generando señales para {symbol}: {e}")
        return {
            'symbol': symbol,
            'strategy_type': strategy_type,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def backtest_strategy(strategy_name: str, symbol: str, days: int = 30) -> Dict:
    """Ejecuta backtest de una estrategia para un período específico"""
    try:
        start_time = time.time()
        
        # Generar datos históricos simulados
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = np.random.uniform(50, 200)
        
        # Simular serie de precios con tendencia y volatilidad
        prices = [base_price]
        for i in range(days - 1):
            trend = np.random.normal(0.0005, 0.02)  # Pequeña tendencia alcista
            new_price = prices[-1] * (1 + trend)
            prices.append(max(new_price, 1))
        
        # Crear DataFrame de mercado
        market_data = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': [p * np.random.uniform(1.0, 1.05) for p in prices],
            'Low': [p * np.random.uniform(0.95, 1.0) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(100000, 1000000, days)
        })
        
        # Ejecutar estrategia
        strategy_result = ray.get(execute_strategy_parallel.remote(strategy_name, market_data, symbol))
        
        # Añadir métricas adicionales de backtest
        strategy_result.update({
            'backtest_period': f"{days} days",
            'start_date': dates[0].strftime('%Y-%m-%d'),
            'end_date': dates[-1].strftime('%Y-%m-%d'),
            'initial_price': float(prices[0]),
            'final_price': float(prices[-1]),
            'buy_and_hold_return': float((prices[-1] - prices[0]) / prices[0])
        })
        
        return strategy_result
        
    except Exception as e:
        logger.error(f"Error en backtest de {strategy_name} para {symbol}: {e}")
        return {
            'strategy': strategy_name,
            'symbol': symbol,
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

# Endpoints FastAPI
@app.get("/")
def read_root():
    return {"message": "Ray Intraday Strategy Engine funcionando", "service": "ray-intraday-strategy"}

@app.get("/status")
def read_status():
    return {
        "status": "Ray Intraday Strategy Engine funcionando",
        "ray_status": "connected" if ray.is_initialized() else "disconnected",
        "available_resources": ray.available_resources() if ray.is_initialized() else {},
        "available_strategies": ["momentum", "mean_reversion", "breakout", "volatility"]
    }

@app.post("/execute-strategies")
def execute_strategies(request: StrategyRequest):
    """Ejecuta múltiples estrategias en paralelo usando Ray"""
    try:
        start_time = time.time()
        
        strategies = request.strategies
        symbols = request.symbols or ['AAPL', 'GOOGL', 'MSFT']
        
        logger.info(f"Ejecutando {len(strategies)} estrategias para {len(symbols)} símbolos con Ray")
        
        # Generar datos de mercado simulados para cada símbolo
        market_data = {}
        for symbol in symbols:
            dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
            base_price = np.random.uniform(50, 200)
            prices = [base_price]
            
            for i in range(99):
                change = np.random.normal(0.001, 0.02)
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1))
            
            market_data[symbol] = pd.DataFrame({
                'Date': dates,
                'Open': prices,
                'High': [p * np.random.uniform(1.0, 1.05) for p in prices],
                'Low': [p * np.random.uniform(0.95, 1.0) for p in prices],
                'Close': prices,
                'Volume': np.random.randint(100000, 1000000, 100)
            })
        
        # Ejecutar todas las combinaciones en paralelo
        strategy_futures = []
        for strategy in strategies:
            for symbol in symbols:
                future = execute_strategy_parallel.remote(strategy, market_data[symbol], symbol)
                strategy_futures.append(future)
        
        # Obtener todos los resultados
        strategy_results = ray.get(strategy_futures)
        
        # Organizar resultados por estrategia
        results_by_strategy = {}
        for result in strategy_results:
            strategy_name = result['strategy']
            if strategy_name not in results_by_strategy:
                results_by_strategy[strategy_name] = []
            results_by_strategy[strategy_name].append(result)
        
        # Calcular métricas agregadas
        best_strategy = max(strategy_results, 
                          key=lambda x: x.get('sharpe_ratio', -999) if 'error' not in x else -999)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Ejecutadas {len(strategies)} estrategias para {len(symbols)} símbolos",
            "execution_summary": {
                "strategies_executed": len(strategies),
                "symbols_analyzed": len(symbols),
                "total_combinations": len(strategy_futures),
                "successful_executions": len([r for r in strategy_results if 'error' not in r]),
                "failed_executions": len([r for r in strategy_results if 'error' in r])
            },
            "results_by_strategy": results_by_strategy,
            "best_performer": best_strategy,
            "performance_metrics": {
                "total_processing_time": processing_time,
                "avg_execution_time": np.mean([r.get('processing_time', 0) for r in strategy_results]),
                "parallelization_benefit": f"{len(strategy_futures)}x parallel execution"
            }
        }
        
    except Exception as e:
        logger.error(f"Error ejecutando estrategias: {e}")
        raise HTTPException(status_code=500, detail=f"Error ejecutando estrategias: {str(e)}")

@app.post("/generate-signals")
def generate_signals(request: SignalRequest):
    """Genera señales de trading para múltiples símbolos en paralelo"""
    try:
        start_time = time.time()
        
        symbols = request.symbols
        strategy_type = request.strategy_type
        
        logger.info(f"Generando señales {strategy_type} para {len(symbols)} símbolos con Ray")
        
        # Generar señales en paralelo
        signal_futures = []
        for symbol in symbols:
            future = generate_trading_signals.remote(symbol, strategy_type)
            signal_futures.append(future)
        
        # Obtener resultados
        signal_results = ray.get(signal_futures)
        
        # Clasificar señales
        buy_signals = [r for r in signal_results if r.get('current_signal') == 1 and 'error' not in r]
        sell_signals = [r for r in signal_results if r.get('current_signal') == -1 and 'error' not in r]
        hold_signals = [r for r in signal_results if r.get('current_signal') == 0 and 'error' not in r]
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Señales generadas para {len(symbols)} símbolos",
            "strategy_type": strategy_type,
            "signal_summary": {
                "total_symbols": len(symbols),
                "buy_signals": len(buy_signals),
                "sell_signals": len(sell_signals),
                "hold_signals": len(hold_signals),
                "strong_signals": len([r for r in signal_results if r.get('signal_strength', 0) > 0.5])
            },
            "signals": {
                "buy": buy_signals,
                "sell": sell_signals,
                "hold": hold_signals
            },
            "processing_time": processing_time,
            "parallelization": f"Señales generadas en {len(signal_futures)} procesos paralelos"
        }
        
    except Exception as e:
        logger.error(f"Error generando señales: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando señales: {str(e)}")

@app.post("/backtest-strategy")
def backtest_strategy_endpoint(request: BacktestRequest):
    """Ejecuta backtest de una estrategia específica"""
    try:
        start_time = time.time()
        
        strategy_name = request.strategy_name
        symbol = request.symbol
        
        logger.info(f"Ejecutando backtest de {strategy_name} para {symbol}")
        
        # Ejecutar backtest en Ray
        backtest_future = backtest_strategy.remote(strategy_name, symbol, 60)  # 60 días
        backtest_result = ray.get(backtest_future)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Backtest completado para {strategy_name} en {symbol}",
            "backtest_result": backtest_result,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error en backtest: {e}")
        raise HTTPException(status_code=500, detail=f"Error en backtest: {str(e)}")

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
