import ray
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import asyncio
import time
from datetime import datetime
import uvicorn

# Inicializar Ray
if not ray.is_initialized():
    ray.init(object_store_memory=100000000)  # 100MB

app = FastAPI(title="Ray-Powered Portfolio Manager", version="1.0.0")

@ray.remote
def calculate_portfolio_metrics(portfolio_data: Dict, risk_free_rate: float = 0.02) -> Dict:
    """
    Calcula métricas de portafolio usando Ray para paralelización
    """
    try:
        start_time = time.time()
        
        # Simular datos del portafolio
        weights = np.array(list(portfolio_data.get('weights', {}).values()))
        returns = np.random.normal(0.08, 0.15, len(weights))  # Simular retornos
        
        # Cálculos de métricas
        portfolio_return = np.sum(weights * returns)
        portfolio_risk = np.sqrt(np.sum((weights * 0.15) ** 2))  # Simplified risk calculation
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
        
        # Métricas adicionales
        max_drawdown = np.random.uniform(0.05, 0.20)
        value_at_risk = np.random.uniform(0.03, 0.10)
        
        processing_time = time.time() - start_time
        
        return {
            'portfolio_return': float(portfolio_return),
            'portfolio_risk': float(portfolio_risk),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'value_at_risk': float(value_at_risk),
            'processing_time': processing_time,
            'assets_count': len(weights),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def optimize_portfolio_allocation(assets: List[str], target_return: float = 0.10) -> Dict:
    """
    Optimiza asignación de portafolio usando Ray
    """
    try:
        start_time = time.time()
        
        n_assets = len(assets)
        
        # Simulación de optimización de portafolio (Markowitz simplificado)
        np.random.seed(42)
        expected_returns = np.random.normal(0.08, 0.04, n_assets)
        covariance_matrix = np.random.rand(n_assets, n_assets)
        covariance_matrix = np.dot(covariance_matrix, covariance_matrix.T)  # Make positive definite
        
        # Optimización simplificada (equal weight como baseline)
        equal_weights = np.ones(n_assets) / n_assets
        
        # Simular proceso de optimización
        time.sleep(0.1)  # Simular cálculo complejo
        
        # Generar pesos optimizados (con algo de randomness)
        optimized_weights = equal_weights + np.random.normal(0, 0.05, n_assets)
        optimized_weights = np.abs(optimized_weights)  # Ensure positive
        optimized_weights = optimized_weights / np.sum(optimized_weights)  # Normalize
        
        processing_time = time.time() - start_time
        
        return {
            'assets': assets,
            'optimized_weights': {asset: float(weight) for asset, weight in zip(assets, optimized_weights)},
            'expected_return': float(np.sum(optimized_weights * expected_returns)),
            'expected_risk': float(np.sqrt(np.dot(optimized_weights.T, np.dot(covariance_matrix, optimized_weights)))),
            'target_return': target_return,
            'processing_time': processing_time,
            'optimization_method': 'Mean-Variance (Simplified)',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@ray.remote
def calculate_risk_metrics(portfolio_weights: Dict, market_data: Dict) -> Dict:
    """
    Calcula métricas de riesgo en paralelo
    """
    try:
        start_time = time.time()
        
        # Simular cálculo de métricas de riesgo
        beta = np.random.uniform(0.8, 1.2)
        alpha = np.random.uniform(-0.02, 0.04)
        correlation_with_market = np.random.uniform(0.6, 0.9)
        
        # VaR y CVaR simulation
        confidence_levels = [0.95, 0.99]
        var_metrics = {}
        cvar_metrics = {}
        
        for confidence in confidence_levels:
            var_metrics[f'VaR_{int(confidence*100)}'] = np.random.uniform(0.03, 0.08)
            cvar_metrics[f'CVaR_{int(confidence*100)}'] = np.random.uniform(0.04, 0.10)
        
        processing_time = time.time() - start_time
        
        return {
            'beta': float(beta),
            'alpha': float(alpha),
            'correlation_with_market': float(correlation_with_market),
            'var_metrics': var_metrics,
            'cvar_metrics': cvar_metrics,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }

@app.get("/status")
def read_status():
    """Status del servicio Ray Portfolio Manager"""
    return {
        "status": "Ray-Powered Portfolio Manager funcionando",
        "ray_initialized": ray.is_initialized(),
        "ray_cluster_resources": ray.cluster_resources() if ray.is_initialized() else None,
        "service_type": "Portfolio Management & Optimization"
    }

@app.post("/parallel-portfolio-analysis")
async def parallel_portfolio_analysis(
    portfolios: List[Dict],
    risk_free_rate: float = 0.02
):
    """
    Analiza múltiples portafolios en paralelo usando Ray
    """
    start_time = time.time()
    
    try:
        # Crear tareas Ray para análisis paralelo
        tasks = [
            calculate_portfolio_metrics.remote(portfolio, risk_free_rate)
            for portfolio in portfolios
        ]
        
        # Ejecutar en paralelo y recopilar resultados
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        return {
            "message": f"Análisis paralelo completado para {len(portfolios)} portafolios",
            "results": results,
            "performance_metrics": {
                "total_portfolios": len(portfolios),
                "total_processing_time": total_time,
                "avg_time_per_portfolio": total_time / len(portfolios) if portfolios else 0,
                "parallel_efficiency": "Ray Remote execution"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis paralelo: {str(e)}")

@app.post("/optimize-multiple-portfolios")
async def optimize_multiple_portfolios(
    portfolio_configs: List[Dict],
    target_return: float = 0.10
):
    """
    Optimiza múltiples configuraciones de portafolio en paralelo
    """
    start_time = time.time()
    
    try:
        # Crear tareas Ray para optimización paralela
        tasks = [
            optimize_portfolio_allocation.remote(
                config.get('assets', []), 
                config.get('target_return', target_return)
            )
            for config in portfolio_configs
        ]
        
        # Ejecutar en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        return {
            "message": f"Optimización paralela completada para {len(portfolio_configs)} configuraciones",
            "optimizations": results,
            "performance_metrics": {
                "total_configs": len(portfolio_configs),
                "total_optimization_time": total_time,
                "avg_time_per_optimization": total_time / len(portfolio_configs) if portfolio_configs else 0,
                "ray_parallel_execution": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en optimización paralela: {str(e)}")

@app.post("/parallel-risk-analysis")
async def parallel_risk_analysis(
    portfolios_data: List[Dict]
):
    """
    Análisis de riesgo paralelo para múltiples portafolios
    """
    start_time = time.time()
    
    try:
        # Crear tareas Ray para análisis de riesgo paralelo
        tasks = [
            calculate_risk_metrics.remote(
                portfolio.get('weights', {}),
                portfolio.get('market_data', {})
            )
            for portfolio in portfolios_data
        ]
        
        # Ejecutar en paralelo
        results = ray.get(tasks)
        
        total_time = time.time() - start_time
        
        return {
            "message": f"Análisis de riesgo paralelo completado para {len(portfolios_data)} portafolios",
            "risk_analysis": results,
            "performance_metrics": {
                "total_portfolios": len(portfolios_data),
                "total_analysis_time": total_time,
                "avg_time_per_analysis": total_time / len(portfolios_data) if portfolios_data else 0,
                "parallel_processing": "Ray Remote enabled"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de riesgo: {str(e)}")

@app.get("/demo-portfolio-optimization")
async def demo_portfolio_optimization():
    """
    Demo de optimización de portafolio con Ray
    """
    # Portfolio demo data
    demo_portfolios = [
        {
            'assets': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
            'target_return': 0.12
        },
        {
            'assets': ['NVDA', 'AMD', 'INTC'],
            'target_return': 0.15
        },
        {
            'assets': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'target_return': 0.08
        }
    ]
    
    return await optimize_multiple_portfolios(demo_portfolios)

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup Ray al cerrar la aplicación"""
    if ray.is_initialized():
        ray.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
