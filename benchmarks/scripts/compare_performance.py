"""
Script para comparar el rendimiento entre servicios originales y servicios con Ray
"""

import requests
import time
import concurrent.futures
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from typing import Dict, List

class PerformanceComparison:
    def __init__(self):
        self.original_services = {
            'sentiment': 'http://localhost:8001',
            'garch': 'http://localhost:8003'
        }
        
        self.ray_services = {
            'sentiment': 'http://localhost:8005',
            'garch': 'http://localhost:8006'
        }
        
        self.results = {}
    
    def benchmark_service(self, service_url: str, endpoint: str, iterations: int = 5, service_type: str = "sentiment") -> Dict:
        """Benchmark un servicio específico"""
        times = []
        responses = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if service_type == "sentiment":
                    if "parallel-analysis" in endpoint:
                        response = requests.get(f"{service_url}{endpoint}")
                    else:
                        response = requests.get(f"{service_url}{endpoint}")
                elif service_type == "garch":
                    if endpoint.startswith("/predict-volatility"):
                        response = requests.post(f"{service_url}{endpoint}")
                    else:
                        response = requests.get(f"{service_url}{endpoint}")
                
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
                    responses.append(response.json())
                    print(f"  ✅ Iteración {i+1}: {end_time - start_time:.3f}s")
                else:
                    print(f"  ❌ Iteración {i+1}: Error {response.status_code}")
                    times.append(float('inf'))
                    
            except Exception as e:
                print(f"  ❌ Iteración {i+1}: {e}")
                times.append(float('inf'))
                end_time = time.time()
        
        valid_times = [t for t in times if t != float('inf')]
        
        return {
            'avg_time': np.mean(valid_times) if valid_times else float('inf'),
            'min_time': np.min(valid_times) if valid_times else float('inf'),
            'max_time': np.max(valid_times) if valid_times else float('inf'),
            'std_time': np.std(valid_times) if valid_times else 0,
            'success_rate': len(valid_times) / iterations,
            'times': times,
            'sample_response': responses[0] if responses else None
        }
    
    def compare_sentiment_services(self):
        """Compara servicios de sentiment analysis"""
        print("🔍 COMPARANDO SERVICIOS DE SENTIMENT ANALYSIS")
        print("=" * 60)
        
        # Test 1: Carga básica de datos
        print("\n📊 Test 1: Carga de datos básica")
        
        print("  🔹 Servicio Original:")
        original_basic = self.benchmark_service(
            self.original_services['sentiment'], 
            "/load-sentiment-data", 
            iterations=3,
            service_type="sentiment"
        )
        
        print("  🔹 Servicio Ray:")
        ray_basic = self.benchmark_service(
            self.ray_services['sentiment'], 
            "/load-sentiment-data", 
            iterations=3,
            service_type="sentiment"
        )
        
        # Test 2: Análisis paralelo (solo Ray)
        print("\n📊 Test 2: Análisis paralelo (solo disponible en Ray)")
        
        print("  🔹 Servicio Ray - Análisis Paralelo:")
        ray_parallel = self.benchmark_service(
            self.ray_services['sentiment'], 
            "/parallel-analysis?tickers=AAPL,GOOGL,MSFT,TSLA,NVDA,META,NFLX,AMZN", 
            iterations=3,
            service_type="sentiment"
        )
        
        # Almacenar resultados
        self.results['sentiment'] = {
            'original_basic': original_basic,
            'ray_basic': ray_basic,
            'ray_parallel': ray_parallel
        }
        
        # Mostrar comparación
        print("\n📈 RESULTADOS SENTIMENT ANALYSIS:")
        print(f"  Original (básico): {original_basic['avg_time']:.3f}s ± {original_basic['std_time']:.3f}s")
        print(f"  Ray (básico): {ray_basic['avg_time']:.3f}s ± {ray_basic['std_time']:.3f}s")
        print(f"  Ray (paralelo): {ray_parallel['avg_time']:.3f}s ± {ray_parallel['std_time']:.3f}s")
        
        if ray_basic['avg_time'] < original_basic['avg_time']:
            improvement = (original_basic['avg_time'] - ray_basic['avg_time']) / original_basic['avg_time'] * 100
            print(f"  🚀 Mejora con Ray: {improvement:.1f}% más rápido")
        else:
            degradation = (ray_basic['avg_time'] - original_basic['avg_time']) / original_basic['avg_time'] * 100
            print(f"  ⚠️  Ray básico es {degradation:.1f}% más lento (overhead de inicialización)")
    
    def compare_garch_services(self):
        """Compara servicios GARCH"""
        print("\n🔍 COMPARANDO SERVICIOS GARCH")
        print("=" * 60)
        
        # Test 1: Predicción básica
        print("\n📊 Test 1: Predicción básica de volatilidad")
        
        print("  🔹 Servicio Original:")
        original_predict = self.benchmark_service(
            self.original_services['garch'], 
            "/predict-volatility", 
            iterations=3,
            service_type="garch"
        )
        
        print("  🔹 Servicio Ray:")
        ray_predict = self.benchmark_service(
            self.ray_services['garch'], 
            "/predict-volatility", 
            iterations=3,
            service_type="garch"
        )
        
        # Test 2: Varianza móvil
        print("\n📊 Test 2: Cálculo de varianza móvil")
        
        print("  🔹 Servicio Original:")
        original_variance = self.benchmark_service(
            self.original_services['garch'], 
            "/calculate-rolling-variance", 
            iterations=3,
            service_type="garch"
        )
        
        print("  🔹 Servicio Ray:")
        ray_variance = self.benchmark_service(
            self.ray_services['garch'], 
            "/calculate-rolling-variance?n_simulations=10", 
            iterations=3,
            service_type="garch"
        )
        
        # Almacenar resultados
        self.results['garch'] = {
            'original_predict': original_predict,
            'ray_predict': ray_predict,
            'original_variance': original_variance,
            'ray_variance': ray_variance
        }
        
        # Mostrar comparación
        print("\n📈 RESULTADOS GARCH:")
        print(f"  Original (predicción): {original_predict['avg_time']:.3f}s ± {original_predict['std_time']:.3f}s")
        print(f"  Ray (predicción): {ray_predict['avg_time']:.3f}s ± {ray_predict['std_time']:.3f}s")
        print(f"  Original (varianza): {original_variance['avg_time']:.3f}s ± {original_variance['std_time']:.3f}s")
        print(f"  Ray (varianza paralela): {ray_variance['avg_time']:.3f}s ± {ray_variance['std_time']:.3f}s")
    
    def test_concurrent_load(self, max_workers: int = 10):
        """Prueba carga concurrente en ambos tipos de servicios"""
        print(f"\n🔍 PRUEBA DE CARGA CONCURRENTE ({max_workers} workers)")
        print("=" * 60)
        
        def make_request(service_url, endpoint, service_type):
            start_time = time.time()
            try:
                if service_type == "sentiment":
                    response = requests.get(f"{service_url}{endpoint}")
                elif service_type == "garch":
                    response = requests.post(f"{service_url}{endpoint}")
                
                end_time = time.time()
                return {
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'service': service_url
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'success': False,
                    'time': end_time - start_time,
                    'error': str(e),
                    'service': service_url
                }
        
        # Preparar requests concurrentes
        requests_list = []
        
        # Sentiment services
        for _ in range(max_workers // 2):
            requests_list.append((self.original_services['sentiment'], '/load-sentiment-data', 'sentiment'))
            requests_list.append((self.ray_services['sentiment'], '/load-sentiment-data', 'sentiment'))
        
        # GARCH services
        for _ in range(max_workers // 2):
            requests_list.append((self.original_services['garch'], '/predict-volatility', 'garch'))
            requests_list.append((self.ray_services['garch'], '/predict-volatility', 'garch'))
        
        # Ejecutar requests concurrentes
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, url, endpoint, stype) for url, endpoint, stype in requests_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Analizar resultados por tipo de servicio
        original_results = [r for r in results if ':8001' in r['service'] or ':8003' in r['service']]
        ray_results = [r for r in results if ':8005' in r['service'] or ':8006' in r['service']]
        
        original_success_rate = sum(1 for r in original_results if r['success']) / len(original_results)
        ray_success_rate = sum(1 for r in ray_results if r['success']) / len(ray_results)
        
        original_avg_time = np.mean([r['time'] for r in original_results if r['success']])
        ray_avg_time = np.mean([r['time'] for r in ray_results if r['success']])
        
        print(f"\n📊 RESULTADOS CARGA CONCURRENTE:")
        print(f"  Servicios Originales:")
        print(f"    - Tasa de éxito: {original_success_rate:.2%}")
        print(f"    - Tiempo promedio: {original_avg_time:.3f}s")
        print(f"  Servicios Ray:")
        print(f"    - Tasa de éxito: {ray_success_rate:.2%}")
        print(f"    - Tiempo promedio: {ray_avg_time:.3f}s")
        print(f"  Tiempo total: {total_time:.3f}s")
        
        self.results['concurrent'] = {
            'original_success_rate': original_success_rate,
            'ray_success_rate': ray_success_rate,
            'original_avg_time': original_avg_time,
            'ray_avg_time': ray_avg_time,
            'total_time': total_time
        }
    
    def generate_performance_report(self):
        """Genera reporte de rendimiento completo"""
        print("\n📊 REPORTE DE RENDIMIENTO FINAL")
        print("=" * 60)
        
        print("\n🎯 RESUMEN DE MEJORAS CON RAY:")
        
        # Sentiment Analysis
        if 'sentiment' in self.results:
            sentiment = self.results['sentiment']
            if sentiment['ray_basic']['avg_time'] < sentiment['original_basic']['avg_time']:
                improvement = (sentiment['original_basic']['avg_time'] - sentiment['ray_basic']['avg_time']) / sentiment['original_basic']['avg_time'] * 100
                print(f"  ✅ Sentiment Analysis: {improvement:.1f}% más rápido")
            else:
                overhead = (sentiment['ray_basic']['avg_time'] - sentiment['original_basic']['avg_time']) / sentiment['original_basic']['avg_time'] * 100
                print(f"  ⚠️  Sentiment Analysis: {overhead:.1f}% overhead (normal para cargas pequeñas)")
        
        # GARCH
        if 'garch' in self.results:
            garch = self.results['garch']
            if garch['ray_predict']['avg_time'] < garch['original_predict']['avg_time']:
                improvement = (garch['original_predict']['avg_time'] - garch['ray_predict']['avg_time']) / garch['original_predict']['avg_time'] * 100
                print(f"  ✅ GARCH Prediction: {improvement:.1f}% más rápido")
        
        print("\n🚀 NUEVAS CAPACIDADES CON RAY:")
        if 'sentiment' in self.results and 'ray_parallel' in self.results['sentiment']:
            parallel_time = self.results['sentiment']['ray_parallel']['avg_time']
            print(f"  📈 Análisis paralelo de múltiples tickers: {parallel_time:.3f}s")
        
        if 'garch' in self.results:
            print(f"  📈 Simulaciones paralelas de volatilidad disponibles")
        
        print("\n💡 RECOMENDACIONES:")
        print("  1. Ray muestra ventajas significativas para:")
        print("     - Procesamiento de múltiples assets en paralelo")
        print("     - Análisis de grandes volúmenes de datos")
        print("     - Simulaciones Monte Carlo")
        print("  2. Para cargas pequeñas, el overhead de Ray puede ser mayor")
        print("  3. Los beneficios de Ray se maximizan con:")
        print("     - Múltiples CPUs disponibles")
        print("     - Tareas computacionalmente intensivas")
        print("     - Procesamiento de lotes grandes")
    
    def save_results(self, filename='performance_comparison.json'):
        """Guarda resultados en archivo JSON"""
        # Convertir resultados para JSON (manejar tipos no serializables)
        json_results = {}
        for service, data in self.results.items():
            json_results[service] = {}
            for test, metrics in data.items():
                json_results[service][test] = {}
                for key, value in metrics.items():
                    if isinstance(value, (np.ndarray, list)):
                        json_results[service][test][key] = [float(v) if not np.isinf(v) else None for v in value]
                    elif isinstance(value, (np.floating, float)):
                        json_results[service][test][key] = float(value) if not np.isinf(value) else None
                    elif isinstance(value, (np.integer, int)):
                        json_results[service][test][key] = int(value)
                    else:
                        json_results[service][test][key] = value
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en {filename}")
    
    def run_complete_comparison(self):
        """Ejecuta comparación completa"""
        print("🚀 INICIANDO COMPARACIÓN DE RENDIMIENTO")
        print("Asegúrate de que todos los servicios estén ejecutándose:")
        print("  docker-compose -f docker-compose-ray.yml up -d")
        print("\nPresiona Enter para continuar...")
        
        try:
            input()
            
            self.compare_sentiment_services()
            self.compare_garch_services()
            self.test_concurrent_load()
            self.generate_performance_report()
            self.save_results()
            
            print("\n✅ Comparación completada!")
            
        except KeyboardInterrupt:
            print("\n❌ Comparación cancelada")
        except Exception as e:
            print(f"\n❌ Error durante comparación: {e}")

def main():
    """Función principal"""
    comparison = PerformanceComparison()
    comparison.run_complete_comparison()

if __name__ == "__main__":
    main()
