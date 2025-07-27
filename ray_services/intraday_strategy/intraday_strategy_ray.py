import ray
from ray import serve
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import time
from datetime import datetime

# Inicializar Ray y Ray Serve
if not ray.is_initialized():
    ray.init(object_store_memory=100000000)  # 100MB

serve.start()

@serve.deployment
@serve.ingress
class IntradayStrategyService:
    def __init__(self):
        pass

    async def status(self):
        return {
            "status": "Ray-Powered Intraday Strategy Engine funcionando",
            "ray_initialized": ray.is_initialized(),
            "ray_cluster_resources": ray.cluster_resources() if ray.is_initialized() else None,
            "service_type": "Intraday Trading Strategies & Signals"
        }

    async def parallel_strategy_backtesting(self, strategies: List[Dict], market_data: Optional[Dict] = None):
        start_time = time.time()

        if market_data is None:
            market_data = {
                'timeframe': '5min',
                'period': '1month',
                'data_points': 10000
            }

        try:
            tasks = [
                execute_strategy_backtest.remote(strategy, market_data)
                for strategy in strategies
            ]

            results = ray.get(tasks)
            total_time = time.time() - start_time

            valid_results = [r for r in results if 'error' not in r]
            sorted_strategies = sorted(
                valid_results,
                key=lambda x: x['backtest_results']['sharpe_ratio'],
                reverse=True
            ) if valid_results else []

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
            return {"error": f"Error en backtesting paralelo: {str(e)}"}

# Definir funciones remotas de Ray
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

# Desplegar el servicio
IntradayStrategyService.deploy()
