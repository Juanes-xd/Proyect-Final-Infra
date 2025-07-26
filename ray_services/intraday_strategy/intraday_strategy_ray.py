import ray
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import asyncio
import time
from datetime import datetime, timedelta
import uvicorn

# Inicializar Ray
if not ray.is_initialized():
    ray.init(object_store_memory=100000000)  # 100MB

app = FastAPI(title="Ray-Powered Intraday Strategy Engine", version="1.0.0")

@ray.remote
def execute_strategy_backtest(strategy_config: Dict, market_data: Dict) -> Dict:
    """
    Ejecuta backtesting de estrategia intraday usando Ray
    """
    try:
        start_time = time.time()
        
        strategy_name = strategy_config.get('name', 'Unknown Strategy')
        timeframe = strategy_config.get('timeframe', '5min')
        capital = strategy_config.get('initial_capital', 100000)
        
        # Simular backtesting
        n_trades = np.random.randint(50, 200)
        win_rate = np.random.uniform(0.45, 0.65)
        avg_win = np.random.uniform(0.01, 0.03)
        avg_loss = np.random.uniform(-0.02, -0.008)
        
        # Calcular métricas de performance
        total_return = np.random.uniform(-0.05, 0.25)
        max_drawdown = np.random.uniform(0.02, 0.15)
        sharpe_ratio = np.random.uniform(0.5, 2.5)
        profit_factor = abs(avg_win * win_rate) / abs(avg_loss * (1 - win_rate))
        
        processing_time = time.time() - start_time
        
        return {
            'strategy_name': strategy_name,
            'timeframe': timeframe,
            'backtest_results': {
                'total_trades': int(n_trades),
                'win_rate': float(win_rate),
                'total_return': float(total_return),
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'profit_factor': float(profit_factor),
                'avg_win': float(avg_win),
                'avg_loss': float(avg_loss),
                'final_capital': float(capital * (1 + total_return))
            },
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'strategy_name': strategy_config.get('name', 'Unknown'),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def calculate_technical_indicators(price_data: List[float], indicators: List[str]) -> Dict:
    """
    Calcula indicadores técnicos en paralelo usando Ray
    """
    try:
        start_time = time.time()
        
        prices = np.array(price_data)
        results = {}
        
        for indicator in indicators:
            if indicator.upper() == 'SMA':
                # Simple Moving Average
                window = 20
                sma = np.convolve(prices, np.ones(window)/window, mode='valid')
                results['SMA_20'] = sma[-1] if len(sma) > 0 else None
                
            elif indicator.upper() == 'EMA':
                # Exponential Moving Average
                alpha = 2.0 / (20 + 1)
                ema = prices[0]
                for price in prices[1:]:
                    ema = alpha * price + (1 - alpha) * ema
                results['EMA_20'] = float(ema)
                
            elif indicator.upper() == 'RSI':
                # Relative Strength Index
                if len(prices) > 14:
                    deltas = np.diff(prices)
                    gains = np.where(deltas > 0, deltas, 0)
                    losses = np.where(deltas < 0, -deltas, 0)
                    avg_gain = np.mean(gains[-14:])
                    avg_loss = np.mean(losses[-14:])
                    rs = avg_gain / avg_loss if avg_loss != 0 else 0
                    rsi = 100 - (100 / (1 + rs))
                    results['RSI_14'] = float(rsi)
                
            elif indicator.upper() == 'MACD':
                # MACD
                if len(prices) > 26:
                    ema_12 = prices[-12:].mean()  # Simplified
                    ema_26 = prices[-26:].mean()  # Simplified
                    macd = ema_12 - ema_26
                    results['MACD'] = float(macd)
                    
            elif indicator.upper() == 'BOLLINGER':
                # Bollinger Bands
                window = 20
                if len(prices) >= window:
                    sma = prices[-window:].mean()
                    std = prices[-window:].std()
                    results['BB_UPPER'] = float(sma + 2*std)
                    results['BB_LOWER'] = float(sma - 2*std)
                    results['BB_MIDDLE'] = float(sma)
        
        processing_time = time.time() - start_time
        
        return {
            'indicators': results,
            'data_points': len(prices),
            'calculated_indicators': len(results),
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def generate_trading_signals(market_data: Dict, strategy_params: Dict) -> Dict:
    """
    Genera señales de trading usando Ray para paralelización
    """
    try:
        start_time = time.time()
        
        # Simular generación de señales
        asset = market_data.get('asset', 'UNKNOWN')
        price = market_data.get('current_price', 100.0)
        
        # Diferentes tipos de señales
        signals = []
        
        # Señal de momentum
        momentum_signal = {
            'type': 'MOMENTUM',
            'action': np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.3, 0.3, 0.4]),
            'strength': np.random.uniform(0.1, 1.0),
            'price_target': price * np.random.uniform(0.98, 1.02),
            'confidence': np.random.uniform(0.6, 0.95)
        }
        signals.append(momentum_signal)
        
        # Señal de reversión
        reversal_signal = {
            'type': 'REVERSAL',
            'action': np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.25, 0.25, 0.5]),
            'strength': np.random.uniform(0.1, 1.0),
            'price_target': price * np.random.uniform(0.97, 1.03),
            'confidence': np.random.uniform(0.5, 0.9)
        }
        signals.append(reversal_signal)
        
        # Señal de breakout
        breakout_signal = {
            'type': 'BREAKOUT',
            'action': np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.2, 0.4]),
            'strength': np.random.uniform(0.2, 1.0),
            'price_target': price * np.random.uniform(0.99, 1.05),
            'confidence': np.random.uniform(0.7, 0.95)
        }
        signals.append(breakout_signal)
        
        # Señal consolidada
        buy_signals = sum(1 for s in signals if s['action'] == 'BUY')
        sell_signals = sum(1 for s in signals if s['action'] == 'SELL')
        
        if buy_signals > sell_signals:
            consolidated_action = 'BUY'
        elif sell_signals > buy_signals:
            consolidated_action = 'SELL'
        else:
            consolidated_action = 'HOLD'
        
        processing_time = time.time() - start_time
        
        return {
            'asset': asset,
            'current_price': price,
            'individual_signals': signals,
            'consolidated_signal': {
                'action': consolidated_action,
                'strength': np.mean([s['strength'] for s in signals]),
                'confidence': np.mean([s['confidence'] for s in signals])
            },
            'signal_count': len(signals),
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'asset': market_data.get('asset', 'UNKNOWN'),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@app.get("/status")
def read_status():
    """Status del servicio Ray Intraday Strategy Engine"""
    return {
        "status": "Ray-Powered Intraday Strategy Engine funcionando",
        "ray_initialized": ray.is_initialized(),
        "ray_cluster_resources": ray.cluster_resources() if ray.is_initialized() else None,
        "service_type": "Intraday Trading Strategies & Signals"
    }

@app.post("/parallel-strategy-backtesting")
async def parallel_strategy_backtesting(
    strategies: List[Dict],
    market_data: Optional[Dict] = None
):
    """
    Ejecuta backtesting de múltiples estrategias en paralelo usando Ray
    """
    start_time = time.time()
    
    if market_data is None:
        market_data = {
            'timeframe': '5min',
            'period': '1month',
            'data_points': 10000
        }
    
    try:
        # Crear tareas Ray para backtesting paralelo
        tasks = [
            execute_strategy_backtest.remote(strategy, market_data)
            for strategy in strategies
        ]
        
        # Ejecutar en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        # Ranking de estrategias por Sharpe ratio
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            sorted_strategies = sorted(
                valid_results, 
                key=lambda x: x['backtest_results']['sharpe_ratio'], 
                reverse=True
            )
        else:
            sorted_strategies = []
        
        return {
            "message": f"Backtesting paralelo completado para {len(strategies)} estrategias",
            "results": results,
            "strategy_ranking": sorted_strategies,
            "performance_metrics": {
                "total_strategies": len(strategies),
                "successful_backtests": len(valid_results),
                "total_processing_time": total_time,
                "avg_time_per_strategy": total_time / len(strategies) if strategies else 0,
                "parallel_execution": "Ray Remote enabled"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en backtesting paralelo: {str(e)}")

@app.post("/parallel-signal-generation")
async def parallel_signal_generation(
    assets_data: List[Dict],
    strategy_params: Optional[Dict] = None
):
    """
    Genera señales de trading para múltiples activos en paralelo
    """
    start_time = time.time()
    
    if strategy_params is None:
        strategy_params = {
            'timeframe': '5min',
            'risk_tolerance': 'medium',
            'strategy_type': 'momentum'
        }
    
    try:
        # Crear tareas Ray para generación de señales paralela
        tasks = [
            generate_trading_signals.remote(asset_data, strategy_params)
            for asset_data in assets_data
        ]
        
        # Ejecutar en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        # Análisis de señales
        buy_signals = sum(1 for r in results if r.get('consolidated_signal', {}).get('action') == 'BUY')
        sell_signals = sum(1 for r in results if r.get('consolidated_signal', {}).get('action') == 'SELL')
        hold_signals = sum(1 for r in results if r.get('consolidated_signal', {}).get('action') == 'HOLD')
        
        return {
            "message": f"Generación de señales paralela completada para {len(assets_data)} activos",
            "signals": results,
            "signal_summary": {
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "hold_signals": hold_signals,
                "total_assets": len(assets_data)
            },
            "performance_metrics": {
                "total_processing_time": total_time,
                "avg_time_per_asset": total_time / len(assets_data) if assets_data else 0,
                "ray_parallel_processing": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en generación de señales: {str(e)}")

@app.post("/parallel-technical-analysis")
async def parallel_technical_analysis(
    assets_price_data: List[Dict],
    indicators: List[str] = ["SMA", "EMA", "RSI", "MACD", "BOLLINGER"]
):
    """
    Calcula indicadores técnicos para múltiples activos en paralelo
    """
    start_time = time.time()
    
    try:
        # Crear tareas Ray para análisis técnico paralelo
        tasks = [
            calculate_technical_indicators.remote(
                asset_data.get('prices', []), 
                indicators
            )
            for asset_data in assets_price_data
        ]
        
        # Ejecutar en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        return {
            "message": f"Análisis técnico paralelo completado para {len(assets_price_data)} activos",
            "technical_analysis": results,
            "indicators_calculated": indicators,
            "performance_metrics": {
                "total_assets": len(assets_price_data),
                "total_indicators": len(indicators),
                "total_processing_time": total_time,
                "avg_time_per_asset": total_time / len(assets_price_data) if assets_price_data else 0,
                "parallel_processing": "Ray Remote execution"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis técnico: {str(e)}")

@app.get("/demo-strategy-analysis")
async def demo_strategy_analysis():
    """
    Demo completo de análisis de estrategias con Ray
    """
    # Estrategias demo
    demo_strategies = [
        {
            'name': 'Momentum Scalping',
            'timeframe': '1min',
            'initial_capital': 50000,
            'risk_per_trade': 0.01
        },
        {
            'name': 'Mean Reversion',
            'timeframe': '5min',
            'initial_capital': 100000,
            'risk_per_trade': 0.02
        },
        {
            'name': 'Breakout Strategy',
            'timeframe': '15min',
            'initial_capital': 150000,
            'risk_per_trade': 0.015
        },
        {
            'name': 'Grid Trading',
            'timeframe': '5min',
            'initial_capital': 75000,
            'risk_per_trade': 0.005
        }
    ]
    
    return await parallel_strategy_backtesting(demo_strategies)

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup Ray al cerrar la aplicación"""
    if ray.is_initialized():
        ray.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
