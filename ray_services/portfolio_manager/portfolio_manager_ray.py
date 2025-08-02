"""
Microservicio Portfolio Manager optimizado con Ray + FastAPI
Implementa paralelización para gestión de portafolios y optimización
"""

import ray
from ray import serve
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional
import logging
import time
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
app = FastAPI(title="Ray Portfolio Manager", version="1.0.0")

# Modelos Pydantic
class PortfolioRequest(BaseModel):
    tickers: List[str]
    weights: Optional[List[float]] = None

class OptimizationRequest(BaseModel):
    tickers: List[str]
    risk_tolerance: float = 0.5
    target_return: Optional[float] = None

# Funciones Ray remotas para paralelización
@ray.remote
def calculate_portfolio_metrics_parallel(returns: np.ndarray, weights: np.ndarray, risk_free_rate: float = 0.02) -> Dict:
    """Calcula métricas de portfolio de forma paralela"""
    try:
        # Calcular retorno esperado del portfolio
        portfolio_return = np.sum(returns * weights)
        
        # Calcular volatilidad del portfolio (simulada para este ejemplo)
        portfolio_volatility = np.sqrt(np.sum(weights ** 2) * 0.16)  # Simplified calculation
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Maximum drawdown simulado
        max_drawdown = np.random.uniform(0.05, 0.25)
        
        # Value at Risk (VaR) al 95%
        var_95 = portfolio_return - 1.645 * portfolio_volatility
        
        return {
            'portfolio_return': float(portfolio_return),
            'portfolio_volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'var_95': float(var_95),
            'weights': weights.tolist(),
            'risk_adjusted_return': float(portfolio_return / portfolio_volatility) if portfolio_volatility > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error calculando métricas de portfolio: {e}")
        return {'error': str(e)}

@ray.remote
def optimize_portfolio_weights(returns: np.ndarray, risk_tolerance: float, target_return: Optional[float] = None) -> Dict:
    """Optimiza los pesos del portfolio usando Ray"""
    try:
        n_assets = len(returns)
        
        if target_return is None:
            # Optimización de Sharpe ratio
            # Simular optimización (en la práctica usarías scipy.optimize)
            weights = np.random.dirichlet(np.ones(n_assets))  # Pesos que suman 1
            
            # Ajustar por tolerancia al riesgo
            if risk_tolerance < 0.3:  # Conservador
                weights = weights * 0.7 + np.ones(n_assets) / n_assets * 0.3
            elif risk_tolerance > 0.7:  # Agresivo
                weights = weights * 1.3
                weights = weights / np.sum(weights)  # Renormalizar
        else:
            # Optimización con retorno objetivo
            weights = np.random.dirichlet(np.ones(n_assets))
            # Ajustar para alcanzar retorno objetivo (simplificado)
            adjustment = target_return / np.sum(returns * weights)
            weights = weights * adjustment
            weights = weights / np.sum(weights)
        
        # Calcular métricas del portfolio optimizado
        portfolio_return = np.sum(returns * weights)
        portfolio_volatility = np.sqrt(np.sum(weights ** 2) * 0.16)
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'optimized_weights': weights.tolist(),
            'expected_return': float(portfolio_return),
            'expected_volatility': float(portfolio_volatility),
            'expected_sharpe': float(sharpe_ratio),
            'optimization_method': 'Max Sharpe' if target_return is None else 'Target Return'
        }
    except Exception as e:
        logger.error(f"Error optimizando portfolio: {e}")
        return {'error': str(e)}

@ray.remote
def calculate_risk_metrics(returns: np.ndarray, weights: np.ndarray) -> Dict:
    """Calcula métricas de riesgo específicas"""
    try:
        portfolio_returns = returns * weights
        
        # VaR y CVaR
        var_95 = np.percentile(portfolio_returns, 5)
        cvar_95 = np.mean(portfolio_returns[portfolio_returns <= var_95])
        
        # Beta (simulado)
        market_beta = np.random.uniform(0.8, 1.2)
        
        # Tracking error (simulado)
        tracking_error = np.random.uniform(0.02, 0.08)
        
        return {
            'var_95': float(var_95),
            'cvar_95': float(cvar_95),
            'beta': float(market_beta),
            'tracking_error': float(tracking_error),
            'correlation_to_market': float(np.random.uniform(0.7, 0.95))
        }
    except Exception as e:
        logger.error(f"Error calculando métricas de riesgo: {e}")
        return {'error': str(e)}

# Endpoints FastAPI
@app.get("/")
def read_root():
    return {"message": "Ray Portfolio Manager funcionando", "service": "ray-portfolio-manager"}

@app.get("/status")
def read_status():
    return {
        "status": "Ray Portfolio Manager funcionando",
        "ray_status": "connected" if ray.is_initialized() else "disconnected",
        "available_resources": ray.available_resources() if ray.is_initialized() else {}
    }

@app.post("/calculate-portfolio-metrics")
def calculate_portfolio_metrics(request: PortfolioRequest):
    """Calcula métricas de portfolio usando Ray para paralelización"""
    try:
        start_time = time.time()
        
        tickers = request.tickers
        weights = request.weights
        
        # Si no se proporcionan pesos, usar pesos iguales
        if weights is None:
            weights = [1.0 / len(tickers)] * len(tickers)
        
        if len(weights) != len(tickers):
            raise HTTPException(status_code=400, detail="El número de pesos debe coincidir con el número de tickers")
        
        # Simular retornos esperados para cada ticker
        expected_returns = np.random.normal(0.08, 0.05, len(tickers))
        weights_array = np.array(weights)
        
        # Calcular métricas en paralelo con Ray
        logger.info(f"Calculando métricas para portfolio de {len(tickers)} activos con Ray")
        
        # Tarea principal de métricas
        metrics_future = calculate_portfolio_metrics_parallel.remote(expected_returns, weights_array)
        
        # Tarea paralela de métricas de riesgo
        risk_future = calculate_risk_metrics.remote(expected_returns, weights_array)
        
        # Obtener resultados en paralelo
        portfolio_metrics = ray.get(metrics_future)
        risk_metrics = ray.get(risk_future)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Métricas calculadas para portfolio de {len(tickers)} activos",
            "tickers": tickers,
            "portfolio_metrics": portfolio_metrics,
            "risk_metrics": risk_metrics,
            "processing_time": processing_time,
            "parallelization": "Métricas y riesgo calculados en paralelo con Ray"
        }
        
    except Exception as e:
        logger.error(f"Error calculando métricas de portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculando métricas: {str(e)}")

@app.post("/optimize-portfolio")
def optimize_portfolio(request: OptimizationRequest):
    """Optimiza portfolio usando Ray para paralelización"""
    try:
        start_time = time.time()
        
        tickers = request.tickers
        risk_tolerance = request.risk_tolerance
        target_return = request.target_return
        
        # Simular retornos esperados
        expected_returns = np.random.normal(0.08, 0.05, len(tickers))
        
        logger.info(f"Optimizando portfolio de {len(tickers)} activos con Ray")
        
        # Optimizar pesos en paralelo
        optimization_future = optimize_portfolio_weights.remote(expected_returns, risk_tolerance, target_return)
        
        # Calcular múltiples escenarios en paralelo
        scenario_futures = []
        scenarios = [0.3, 0.5, 0.7]  # Diferentes tolerancias al riesgo
        
        for scenario_risk in scenarios:
            if scenario_risk != risk_tolerance:
                future = optimize_portfolio_weights.remote(expected_returns, scenario_risk)
                scenario_futures.append((scenario_risk, future))
        
        # Obtener resultado principal
        optimization_result = ray.get(optimization_future)
        
        # Obtener escenarios alternativos
        alternative_scenarios = {}
        for scenario_risk, future in scenario_futures:
            alternative_scenarios[f"scenario_{scenario_risk}"] = ray.get(future)
        
        processing_time = time.time() - start_time
        
        return {
            "message": f"Portfolio optimizado para {len(tickers)} activos",
            "tickers": tickers,
            "optimization_result": optimization_result,
            "alternative_scenarios": alternative_scenarios,
            "optimization_parameters": {
                "risk_tolerance": risk_tolerance,
                "target_return": target_return,
                "method": "Parallel Multi-Scenario Optimization"
            },
            "processing_time": processing_time,
            "parallelization": f"Optimización principal + {len(scenario_futures)} escenarios en paralelo"
        }
        
    except Exception as e:
        logger.error(f"Error optimizando portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Error optimizando: {str(e)}")

@app.get("/performance-comparison")
def performance_comparison():
    """Compara rendimiento de cálculos seriales vs paralelos"""
    try:
        n_portfolios = 10
        n_assets = 20
        
        # Generar datos de prueba
        test_portfolios = []
        for i in range(n_portfolios):
            returns = np.random.normal(0.08, 0.05, n_assets)
            weights = np.random.dirichlet(np.ones(n_assets))
            test_portfolios.append((returns, weights))
        
        # Procesamiento serial (simulado)
        start_serial = time.time()
        serial_results = []
        for returns, weights in test_portfolios:
            # Simular cálculo serial
            portfolio_return = np.sum(returns * weights)
            portfolio_volatility = np.sqrt(np.sum(weights ** 2) * 0.16)
            serial_results.append({
                'return': portfolio_return,
                'volatility': portfolio_volatility
            })
        serial_time = time.time() - start_serial
        
        # Procesamiento paralelo con Ray
        start_parallel = time.time()
        parallel_futures = []
        for returns, weights in test_portfolios:
            future = calculate_portfolio_metrics_parallel.remote(returns, weights)
            parallel_futures.append(future)
        
        parallel_results = ray.get(parallel_futures)
        parallel_time = time.time() - start_parallel
        
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        
        return {
            "performance_test": {
                "portfolios_tested": n_portfolios,
                "assets_per_portfolio": n_assets,
                "serial_time": f"{serial_time:.3f}s",
                "parallel_time": f"{parallel_time:.3f}s",
                "speedup": f"{speedup:.2f}x",
                "efficiency": f"{(speedup/4)*100:.1f}%"
            },
            "ray_cluster_info": {
                "available_resources": ray.available_resources(),
                "cluster_resources": ray.cluster_resources()
            },
            "results_sample": {
                "serial_sample": serial_results[:3],
                "parallel_sample": [r for r in parallel_results[:3] if 'error' not in r]
            }
        }
        
    except Exception as e:
        logger.error(f"Error en comparación de rendimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error en test: {str(e)}")

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
