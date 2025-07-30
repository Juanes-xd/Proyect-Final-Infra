"""
Script para hacer profiling de los microservicios actuales
e identificar cuellos de botella computacionales
"""

import time
import cProfile
import pstats
import requests
import concurrent.futures
import pandas as pd
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

class MicroserviceBenchmark:
    def __init__(self):
        self.base_urls = {
            'sentiment': 'http://localhost:8001',
            'portfolio': 'http://localhost:8002', 
            'garch': 'http://localhost:8003',
            'intraday': 'http://localhost:8004'
        }
        self.results = {}
        
    def benchmark_sentiment_analyzer(self, iterations=10):
        """Benchmark del analizador de sentiment"""
        print("🔍 Benchmarking Sentiment Analyzer...")
        
        times = []
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Probar carga de datos
                response1 = requests.get(f"{self.base_urls['sentiment']}/load-sentiment-data")
                
                # Probar cálculo de engagement para múltiples tickers
                tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
                for ticker in tickers:
                    response2 = requests.get(f"{self.base_urls['sentiment']}/calculate-engagement/{ticker}")
                
                end_time = time.time()
                times.append(end_time - start_time)
                print(f"  Iteración {i+1}: {end_time - start_time:.3f}s")
                
            except Exception as e:
                print(f"  Error en iteración {i+1}: {e}")
                times.append(float('inf'))
        
        self.results['sentiment'] = {
            'avg_time': np.mean([t for t in times if t != float('inf')]),
            'min_time': np.min([t for t in times if t != float('inf')]),
            'max_time': np.max([t for t in times if t != float('inf')]),
            'std_time': np.std([t for t in times if t != float('inf')]),
            'times': times
        }
        
    def benchmark_garch_predictor(self, iterations=10):
        """Benchmark del predictor GARCH"""
        print("🔍 Benchmarking GARCH Predictor...")
        
        times = []
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Probar carga de datos
                response1 = requests.get(f"{self.base_urls['garch']}/load-market-data")
                
                # Probar predicción de volatilidad
                response2 = requests.post(f"{self.base_urls['garch']}/predict-volatility")
                
                # Probar cálculo de varianza
                response3 = requests.get(f"{self.base_urls['garch']}/calculate-rolling-variance")
                
                end_time = time.time()
                times.append(end_time - start_time)
                print(f"  Iteración {i+1}: {end_time - start_time:.3f}s")
                
            except Exception as e:
                print(f"  Error en iteración {i+1}: {e}")
                times.append(float('inf'))
        
        self.results['garch'] = {
            'avg_time': np.mean([t for t in times if t != float('inf')]),
            'min_time': np.min([t for t in times if t != float('inf')]),
            'max_time': np.max([t for t in times if t != float('inf')]),
            'std_time': np.std([t for t in times if t != float('inf')]),
            'times': times
        }
    
    def benchmark_portfolio_manager(self, iterations=10):
        """Benchmark del portfolio manager"""
        print("🔍 Benchmarking Portfolio Manager...")
        
        times = []
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Probar selección de stocks
                response1 = requests.get(f"{self.base_urls['portfolio']}/select-top-stocks?limit=5")
                
                # Probar cálculo de retornos
                response2 = requests.get(f"{self.base_urls['portfolio']}/calculate-portfolio-returns")
                
                # Probar métricas de performance
                response3 = requests.get(f"{self.base_urls['portfolio']}/portfolio-performance")
                
                end_time = time.time()
                times.append(end_time - start_time)
                print(f"  Iteración {i+1}: {end_time - start_time:.3f}s")
                
            except Exception as e:
                print(f"  Error en iteración {i+1}: {e}")
                times.append(float('inf'))
        
        self.results['portfolio'] = {
            'avg_time': np.mean([t for t in times if t != float('inf')]),
            'min_time': np.min([t for t in times if t != float('inf')]),
            'max_time': np.max([t for t in times if t != float('inf')]),
            'std_time': np.std([t for t in times if t != float('inf')]),
            'times': times
        }
    
    def benchmark_intraday_strategy(self, iterations=10):
        """Benchmark de la estrategia intraday"""
        print("🔍 Benchmarking Intraday Strategy...")
        
        times = []
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Probar cálculo de señales
                data = {"daily_signal": 1}
                response1 = requests.post(f"{self.base_urls['intraday']}/calculate-intraday-signals", json=data)
                
                # Probar ejecución de estrategia
                data = {"position_size": "1000"}
                response2 = requests.post(f"{self.base_urls['intraday']}/execute-strategy", json=data)
                
                # Probar métricas de performance
                response3 = requests.get(f"{self.base_urls['intraday']}/strategy-performance")
                
                end_time = time.time()
                times.append(end_time - start_time)
                print(f"  Iteración {i+1}: {end_time - start_time:.3f}s")
                
            except Exception as e:
                print(f"  Error en iteración {i+1}: {e}")
                times.append(float('inf'))
        
        self.results['intraday'] = {
            'avg_time': np.mean([t for t in times if t != float('inf')]),
            'min_time': np.min([t for t in times if t != float('inf')]),
            'max_time': np.max([t for t in times if t != float('inf')]),
            'std_time': np.std([t for t in times if t != float('inf')]),
            'times': times
        }
    
    def test_concurrent_load(self, concurrent_requests=10):
        """Prueba carga concurrente en todos los servicios"""
        print(f"🔍 Testing concurrent load with {concurrent_requests} requests...")
        
        def make_request(service, endpoint):
            start_time = time.time()
            try:
                if service == 'sentiment':
                    response = requests.get(f"{self.base_urls[service]}/load-sentiment-data")
                elif service == 'garch':
                    response = requests.post(f"{self.base_urls[service]}/predict-volatility")
                elif service == 'portfolio':
                    response = requests.get(f"{self.base_urls[service]}/calculate-portfolio-returns")
                elif service == 'intraday':
                    data = {"daily_signal": 1}
                    response = requests.post(f"{self.base_urls[service]}/calculate-intraday-signals", json=data)
                
                end_time = time.time()
                return {
                    'service': service,
                    'time': end_time - start_time,
                    'status': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'service': service,
                    'time': end_time - start_time,
                    'status': 500,
                    'success': False,
                    'error': str(e)
                }
        
        # Crear lista de requests concurrentes
        requests_list = []
        services = ['sentiment', 'garch', 'portfolio', 'intraday']
        
        for _ in range(concurrent_requests):
            for service in services:
                requests_list.append((service, ''))
        
        # Ejecutar requests concurrentes
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request, service, endpoint) for service, endpoint in requests_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # Analizar resultados
        total_time = end_time - start_time
        success_rate = sum(1 for r in results if r['success']) / len(results)
        avg_response_time = np.mean([r['time'] for r in results])
        
        self.results['concurrent'] = {
            'total_time': total_time,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'total_requests': len(results),
            'successful_requests': sum(1 for r in results if r['success']),
            'results': results
        }
        
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Avg response time: {avg_response_time:.3f}s")
    
    def generate_report(self):
        """Genera reporte de benchmark"""
        print("\n📊 BENCHMARK REPORT")
        print("=" * 50)
        
        # Comparar servicios por tiempo promedio
        service_times = {}
        for service, data in self.results.items():
            if service != 'concurrent' and 'avg_time' in data:
                service_times[service] = data['avg_time']
        
        # Ordenar por tiempo (más lento primero)
        sorted_services = sorted(service_times.items(), key=lambda x: x[1], reverse=True)
        
        print("\n🐌 SERVICIOS ORDENADOS POR TIEMPO DE RESPUESTA:")
        for i, (service, avg_time) in enumerate(sorted_services, 1):
            print(f"  {i}. {service.upper()}: {avg_time:.3f}s (±{self.results[service]['std_time']:.3f}s)")
        
        # Identificar bottlenecks
        print("\n🔍 BOTTLENECKS IDENTIFICADOS:")
        if sorted_services:
            slowest_service = sorted_services[0][0]
            slowest_time = sorted_services[0][1]
            
            print(f"  - PRINCIPAL: {slowest_service.upper()} es el más lento ({slowest_time:.3f}s)")
            
            if len(sorted_services) > 1:
                second_slowest = sorted_services[1][0]
                second_time = sorted_services[1][1]
                ratio = slowest_time / second_time
                
                if ratio > 1.5:
                    print(f"  - {slowest_service.upper()} es {ratio:.1f}x más lento que {second_slowest}")
                    print(f"  - RECOMENDACIÓN: Priorizar optimización de {slowest_service.upper()}")
        
        # Análisis de concurrencia
        if 'concurrent' in self.results:
            concurrent_data = self.results['concurrent']
            print(f"\n⚡ ANÁLISIS DE CONCURRENCIA:")
            print(f"  - Tasa de éxito: {concurrent_data['success_rate']:.2%}")
            print(f"  - Tiempo promedio bajo carga: {concurrent_data['avg_response_time']:.3f}s")
            
            if concurrent_data['success_rate'] < 0.95:
                print("  - ⚠️  PROBLEMA: Baja tasa de éxito bajo carga concurrente")
            
            if concurrent_data['avg_response_time'] > 2.0:
                print("  - ⚠️  PROBLEMA: Tiempo de respuesta alto bajo carga")
    
    def save_results(self, filename='benchmark_results.json'):
        """Guarda resultados en archivo JSON"""
        # Crear directorio results si no existe
        results_dir = '../results'
        os.makedirs(results_dir, exist_ok=True)
        
        # Guardar en la carpeta results
        results_file = os.path.join(results_dir, filename)
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # También guardar en directorio actual para compatibilidad
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        print(f"\n💾 Resultados guardados en {results_file}")
        print(f"💾 También guardados en {filename} (compatibilidad)")
    
    def run_full_benchmark(self):
        """Ejecuta benchmark completo"""
        print("🚀 INICIANDO BENCHMARK COMPLETO")
        print("=" * 50)
        
        try:
            self.benchmark_sentiment_analyzer()
            self.benchmark_garch_predictor()
            self.benchmark_portfolio_manager()
            self.benchmark_intraday_strategy()
            self.test_concurrent_load()
            
            self.generate_report()
            self.save_results()
            
        except KeyboardInterrupt:
            print("\n❌ Benchmark interrumpido por usuario")
        except Exception as e:
            print(f"\n❌ Error durante benchmark: {e}")

def main():
    """Función principal"""
    print("🔬 PROFILING DE MICROSERVICIOS")
    print("Asegúrate de que todos los microservicios estén ejecutándose:")
    print("  docker-compose up -d")
    print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
    
    try:
        input()
        
        benchmark = MicroserviceBenchmark()
        benchmark.run_full_benchmark()
        
        print("\n✅ Profiling completado!")
        print("📈 Los resultados te ayudarán a identificar qué optimizar con Ray")
        
    except KeyboardInterrupt:
        print("\n❌ Profiling cancelado")

if __name__ == "__main__":
    main()
