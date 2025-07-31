#!/usr/bin/env python3
"""
Benchmark de Comparación: Secuencial vs Paralelo (sin Ray)
Simulación usando concurrent.futures para demostrar paralelismo
"""

import requests
import time
import json
import statistics
from datetime import datetime
import concurrent.futures
import threading
from typing import Dict, List

class SequentialVsParallelBenchmark:
    def __init__(self):
        self.original_services = {
            'sentiment': 'http://localhost:8001',
            'portfolio': 'http://localhost:8002', 
            'garch': 'http://localhost:8003',
            'intraday': 'http://localhost:8004'
        }
        
        self.results = {}

    def make_single_request(self, service_name: str, url: str, config: dict) -> dict:
        """Hace una sola request y retorna el resultado"""
        start_time = time.time()
        try:
            if config['method'] == 'GET':
                response = requests.get(url, params=config.get('params'), timeout=30)
            else:
                response = requests.post(url, json=config.get('data'), timeout=30)
            
            end_time = time.time()
            
            return {
                'success': response.status_code == 200,
                'time': end_time - start_time,
                'status_code': response.status_code,
                'service': service_name
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'time': end_time - start_time,
                'error': str(e)[:50],
                'service': service_name
            }

    def test_service_sequential(self, service_name: str, num_requests: int = 8) -> dict:
        """Test secuencial - una request después de otra"""
        base_url = self.original_services[service_name]
        
        # Endpoints y payloads según el servicio
        endpoints = {
            'sentiment': {'endpoint': '/calculate-engagement/AAPL', 'method': 'GET'},
            'portfolio': {'endpoint': '/calculate-portfolio-returns', 'method': 'POST', 
                         'data': ['AAPL', 'GOOGL', 'MSFT']},  # Lista directa de símbolos
            'garch': {'endpoint': '/predict-volatility', 'method': 'POST', 
                     'data': {'symbol': 'AAPL', 'forecast_periods': 30}},
            'intraday': {'endpoint': '/calculate-intraday-signals', 'method': 'POST', 
                        'data': {'symbol': 'AAPL', 'lookback_window': 20}}
        }
        
        config = endpoints[service_name]
        url = f"{base_url}{config['endpoint']}"
        
        print(f"🔄 Testing {service_name} (Sequential)...")
        
        times = []
        errors = 0
        successful_requests = 0
        
        # Requests secuenciales
        for i in range(num_requests):
            result = self.make_single_request(service_name, url, config)
            
            if result['success']:
                times.append(result['time'])
                successful_requests += 1
                print(f"  ✅ Request {i+1}: {result['time']:.3f}s")
            else:
                errors += 1
                error_msg = result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
                print(f"  ❌ Request {i+1}: {error_msg}")
        
        return self._calculate_metrics(times, num_requests, successful_requests, errors)

    def test_service_parallel(self, service_name: str, num_requests: int = 8) -> dict:
        """Test paralelo - múltiples requests concurrentes"""
        base_url = self.original_services[service_name]
        
        # Endpoints y payloads según el servicio
        endpoints = {
            'sentiment': {'endpoint': '/calculate-engagement/AAPL', 'method': 'GET'},
            'portfolio': {'endpoint': '/calculate-portfolio-returns', 'method': 'POST', 
                         'data': ['AAPL', 'GOOGL', 'MSFT']},  # Lista directa de símbolos
            'garch': {'endpoint': '/predict-volatility', 'method': 'POST', 
                     'data': {'symbol': 'AAPL', 'forecast_periods': 30}},
            'intraday': {'endpoint': '/calculate-intraday-signals', 'method': 'POST', 
                        'data': {'symbol': 'AAPL', 'lookback_window': 20}}
        }
        
        config = endpoints[service_name]
        url = f"{base_url}{config['endpoint']}"
        
        print(f"🔄 Testing {service_name} (Parallel)...")
        
        times = []
        errors = 0
        successful_requests = 0
        
        # Requests paralelas usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Enviar todas las requests al mismo tiempo
            future_to_request = {
                executor.submit(self.make_single_request, service_name, url, config): i 
                for i in range(num_requests)
            }
            
            # Recoger resultados conforme van completándose
            for future in concurrent.futures.as_completed(future_to_request):
                request_num = future_to_request[future]
                try:
                    result = future.result()
                    
                    if result['success']:
                        times.append(result['time'])
                        successful_requests += 1
                        print(f"  ✅ Request {request_num+1}: {result['time']:.3f}s")
                    else:
                        errors += 1
                        error_msg = result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
                        print(f"  ❌ Request {request_num+1}: {error_msg}")
                        
                except Exception as e:
                    errors += 1
                    print(f"  ❌ Request {request_num+1}: {str(e)[:50]}")
        
        return self._calculate_metrics(times, num_requests, successful_requests, errors)

    def _calculate_metrics(self, times: List[float], total_requests: int, 
                          successful_requests: int, errors: int) -> dict:
        """Calcula métricas de rendimiento"""
        if times:
            return {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                'times': times,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'errors': errors,
                'throughput': successful_requests / sum(times) if sum(times) > 0 else 0
            }
        else:
            return {
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'std_time': 0,
                'times': [],
                'total_requests': total_requests,
                'successful_requests': 0,
                'errors': errors,
                'throughput': 0
            }

    def run_comparison_benchmark(self):
        """Ejecuta el benchmark completo de comparación"""
        print("🚀 Iniciando Benchmark de Comparación: Secuencial vs Paralelo")
        print("🔗 Usando concurrent.futures para simular paralelismo")
        print("=" * 70)
        
        services = ['sentiment', 'portfolio', 'garch', 'intraday']
        
        for service in services:
            print(f"\n📊 Benchmarking {service.upper()} service...")
            
            # Test secuencial
            sequential_results = self.test_service_sequential(service, 8)
            
            # Pausa entre tests
            time.sleep(2)
            
            # Test paralelo
            parallel_results = self.test_service_parallel(service, 8)
            
            self.results[service] = {
                'sequential': sequential_results,
                'parallel': parallel_results
            }
            
            # Mostrar comparación inmediata
            if sequential_results['successful_requests'] > 0 and parallel_results['successful_requests'] > 0:
                # Calcular total time para comparar
                seq_total_time = sum(sequential_results['times'])
                par_total_time = max(parallel_results['times']) if parallel_results['times'] else 0  # El tiempo paralelo es el máximo
                
                if par_total_time > 0:
                    time_improvement = ((seq_total_time - par_total_time) / seq_total_time) * 100
                    throughput_improvement = ((parallel_results['throughput'] - sequential_results['throughput']) / sequential_results['throughput']) * 100
                    
                    print(f"\n📈 COMPARACIÓN {service.upper()}:")
                    print(f"   Secuencial: {seq_total_time:.3f}s total, {sequential_results['throughput']:.2f} req/s")
                    print(f"   Paralelo:   {par_total_time:.3f}s total, {parallel_results['throughput']:.2f} req/s")
                    print(f"   Mejora:     {time_improvement:+.1f}% tiempo total, {throughput_improvement:+.1f}% throughput")

    def generate_comparison_report(self):
        """Genera reporte de comparación detallado"""
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL DE COMPARACIÓN: SECUENCIAL vs PARALELO")
        print("=" * 80)
        
        comparison_data = []
        
        for service, data in self.results.items():
            sequential = data['sequential']
            parallel = data['parallel']
            
            if sequential['successful_requests'] > 0 and parallel['successful_requests'] > 0:
                # Para tiempo total: secuencial suma todos, paralelo toma el máximo
                seq_total_time = sum(sequential['times'])
                par_total_time = max(parallel['times']) if parallel['times'] else 0
                
                if par_total_time > 0:
                    time_improvement = ((seq_total_time - par_total_time) / seq_total_time) * 100
                    throughput_improvement = ((parallel['throughput'] - sequential['throughput']) / sequential['throughput']) * 100
                    
                    comparison_data.append({
                        'service': service,
                        'sequential_total_time': seq_total_time,
                        'parallel_total_time': par_total_time,
                        'time_improvement': time_improvement,
                        'sequential_throughput': sequential['throughput'],
                        'parallel_throughput': parallel['throughput'],
                        'throughput_improvement': throughput_improvement,
                        'sequential_success_rate': (sequential['successful_requests'] / sequential['total_requests']) * 100,
                        'parallel_success_rate': (parallel['successful_requests'] / parallel['total_requests']) * 100
                    })
        
        # Imprimir tabla comparativa
        print(f"{'SERVICIO':<12} {'SECUENCIAL':<12} {'PARALELO':<12} {'MEJORA TIEMPO':<15} {'MEJORA THROUGHPUT':<18}")
        print("-" * 85)
        
        total_time_improvement = 0
        total_throughput_improvement = 0
        valid_services = 0
        
        for item in comparison_data:
            print(f"{item['service'].upper():<12} "
                  f"{item['sequential_total_time']:.3f}s{'':<6} "
                  f"{item['parallel_total_time']:.3f}s{'':<6} "
                  f"{item['time_improvement']:+.1f}%{'':<10} "
                  f"{item['throughput_improvement']:+.1f}%")
            
            total_time_improvement += item['time_improvement']
            total_throughput_improvement += item['throughput_improvement']
            valid_services += 1
        
        if valid_services > 0:
            avg_time_improvement = total_time_improvement / valid_services
            avg_throughput_improvement = total_throughput_improvement / valid_services
            
            print("-" * 85)
            print(f"{'PROMEDIO':<12} {'':<12} {'':<12} {avg_time_improvement:+.1f}%{'':<10} {avg_throughput_improvement:+.1f}%")
            
            print(f"\n🎯 CONCLUSIONES:")
            print(f"✅ Mejora promedio en tiempo total: {avg_time_improvement:.1f}%")
            print(f"✅ Mejora promedio en throughput: {avg_throughput_improvement:.1f}%")
            
            if avg_time_improvement > 0:
                print("🚀 El procesamiento paralelo demuestra superioridad en rendimiento")
            else:
                print("⚠️  El procesamiento secuencial mantiene ventaja en este benchmark")

    def save_comparison_results(self):
        """Guarda los resultados de comparación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar JSON detallado
        filename = f'../results/sequential_vs_parallel_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Resultados guardados en: {filename}")
        
        return filename

def main():
    print("🎯 Benchmark de Comparación: Procesamiento Secuencial vs Paralelo")
    print("🔗 Conectando a servicios en puertos 8001-8004")
    print("🧵 Usando concurrent.futures para paralelismo")
    
    benchmark = SequentialVsParallelBenchmark()
    
    try:
        benchmark.run_comparison_benchmark()
        benchmark.generate_comparison_report()
        filename = benchmark.save_comparison_results()
        
        print(f"\n✅ Benchmark completado exitosamente!")
        print(f"📊 Usa los resultados en {filename} para generar gráficas")
        
    except Exception as e:
        print(f"❌ Error durante el benchmark: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
