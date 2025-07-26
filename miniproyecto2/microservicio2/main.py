from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import requests
from typing import Dict, List

app = FastAPI(title="Portfolio Manager", version="1.0.0")

@app.get("/status")
def read_status():
    return {"status": "Portfolio Manager funcionando"}

@app.get("/select-top-stocks")
def select_top_stocks(limit: int = 5):
    """Selecciona los top N stocks basado en ranking de engagement"""
    try:
        # Simular datos de múltiples stocks con sus rankings
        stocks_data = []
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX']
        
        for ticker in tickers:
            engagement_ratio = np.random.uniform(1.2, 4.5)
            stocks_data.append({
                'ticker': ticker,
                'engagement_ratio': engagement_ratio,
                'monthly_avg_sentiment': np.random.uniform(0.1, 0.9)
            })
        
        # Ordenar por engagement ratio y seleccionar los top
        df = pd.DataFrame(stocks_data)
        df_ranked = df.sort_values('engagement_ratio', ascending=False)
        top_stocks = df_ranked.head(limit)
        
        return {
            "message": f"Top {limit} stocks seleccionados exitosamente",
            "top_stocks": top_stocks.to_dict('records'),
            "total_analyzed": len(stocks_data),
            "selection_criteria": "engagement_ratio"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seleccionando stocks: {str(e)}")

@app.post("/calculate-portfolio-returns")
def calculate_portfolio_returns(stock_list: List[str]):
    """Calcula los retornos del portfolio para una lista de stocks"""
    try:
        # Simular datos de precios y calcular retornos
        portfolio_data = []
        dates = pd.date_range('2022-01-01', '2023-01-01', freq='D')
        
        for ticker in stock_list:
            # Simular precios con una caminata aleatoria
            initial_price = np.random.uniform(50, 300)
            returns = np.random.normal(0.0005, 0.02, len(dates))  # ~0.05% retorno promedio diario
            prices = [initial_price]
            
            for ret in returns[1:]:
                prices.append(prices[-1] * (1 + ret))
            
            portfolio_data.append({
                'ticker': ticker,
                'initial_price': initial_price,
                'final_price': prices[-1],
                'total_return': (prices[-1] - initial_price) / initial_price,
                'avg_daily_return': np.mean(returns)
            })
        
        # Calcular métricas del portfolio
        total_return = np.mean([stock['total_return'] for stock in portfolio_data])
        avg_daily_return = np.mean([stock['avg_daily_return'] for stock in portfolio_data])
        
        return {
            "message": "Retornos del portfolio calculados exitosamente",
            "portfolio_metrics": {
                "total_return": total_return,
                "avg_daily_return": avg_daily_return,
                "annualized_return": avg_daily_return * 252,  # 252 días de trading
                "number_of_stocks": len(stock_list)
            },
            "individual_stocks": portfolio_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando retornos: {str(e)}")

@app.get("/portfolio-performance")
def get_portfolio_performance():
    """Obtiene métricas de rendimiento del portfolio actual"""
    try:
        # Obtener top stocks del otro microservicio (simulado)
        top_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        
        # Simular métricas de rendimiento
        performance_metrics = {
            "portfolio_return": np.random.uniform(0.08, 0.25),  # 8-25% anual
            "volatility": np.random.uniform(0.15, 0.35),  # 15-35% volatilidad
            "sharpe_ratio": np.random.uniform(0.5, 1.8),
            "max_drawdown": np.random.uniform(-0.05, -0.25),
            "win_rate": np.random.uniform(0.45, 0.65),
            "current_stocks": top_stocks
        }
        
        return {
            "message": "Métricas de rendimiento obtenidas exitosamente",
            "performance": performance_metrics,
            "benchmark_comparison": {
                "vs_sp500": np.random.uniform(-0.05, 0.15),  # outperformance vs S&P 500
                "vs_nasdaq": np.random.uniform(-0.03, 0.12)   # outperformance vs NASDAQ
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo rendimiento: {str(e)}")
