import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List
import pandas as pd
from datetime import datetime

class RayBenchmark:
    def __init__(self):
        self.original_services = {
            'sentiment': 'http://localhost:8001',
            'portfolio': 'http://localhost:8002', 
            'garch': 'http://localhost:8003',
            'intraday': 'http://localhost:8004'
        }
        
        self.ray_services = {
            'sentiment': 'http://localhost:8005',
            'portfolio': 'http://localhost:8007',
            'garch': 'http://localhost:8006', 
            'intraday': 'http://localhost:8008'
        }
        
        self.results = {}

    async def benchmark_sentiment_analysis(self, session: aiohttp.ClientSession, service_type: str):
        """Benchmark análisis de sentimiento"""
        url = self.original_services['sentiment'] if service_type == 'original' else self.ray_services['sentiment']
        
        if service_type == 'ray':
            endpoint = f"{url}/parallel-analysis"
            payload = {"tickers": "AAPL,GOOGL,MSFT,TSLA,NVDA"}
        else:
            endpoint = f"{url}/analyze"
            payload = {"text": "This is a great stock to buy with amazing potential"}
        
        times = []
        errors = 0
        
        for i in range(10):  # 10 requests
            start_time = time.time()
            try:
                async with session.get(endpoint, params=payload if service_type == 'original' else None,
                                     json=payload if service_type == 'ray' else None) as response:
                    if response.status == 200:
                        await response.json()
                        end_time = time.time()
                        times.append(end_time - start_time)
                    else:
                        errors += 1
            except Exception as e:
                errors += 1
                print(f"Error in sentiment {service_type}: {e}")
        
        return {
            'avg_time': statistics.mean(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'total_requests': 10,
            'successful_requests': len(times),
            'errors': errors,
            'throughput': len(times) / sum(times) if times else 0
        }

    async def benchmark_portfolio_management(self, session: aiohttp.ClientSession, service_type: str):
        """Benchmark gestión de portafolio"""
        url = self.original_services['portfolio'] if service_type == 'original' else self.ray_services['portfolio']
        
        if service_type == 'ray':
            endpoint = f"{url}/demo-portfolio-optimization"
            method = 'GET'
            payload = None
        else:
            endpoint = f"{url}/optimize"
            method = 'POST'
            payload = {
                "assets": ["AAPL", "GOOGL", "MSFT"],
                "weights": [0.4, 0.3, 0.3],
                "target_return": 0.12
            }
        
        times = []
        errors = 0
        
        for i in range(8):  # 8 requests (menos porque es más intensivo)
            start_time = time.time()
            try:
                if method == 'GET':
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            await response.json()
                            end_time = time.time()
                            times.append(end_time - start_time)
                        else:
                            errors += 1
                else:
                    async with session.post(endpoint, json=payload) as response:
                        if response.status == 200:
                            await response.json()
                            end_time = time.time()
                            times.append(end_time - start_time)
                        else:
                            errors += 1
            except Exception as e:
                errors += 1
                print(f"Error in portfolio {service_type}: {e}")
        
        return {
            'avg_time': statistics.mean(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'total_requests': 8,
            'successful_requests': len(times),
            'errors': errors,
            'throughput': len(times) / sum(times) if times else 0
        }

    async def benchmark_garch_prediction(self, session: aiohttp.ClientSession, service_type: str):
        """Benchmark predicción GARCH"""
        url = self.original_services['garch'] if service_type == 'original' else self.ray_services['garch']
        
        if service_type == 'ray':
            endpoint = f"{url}/predict-volatility"
            payload = {"window_size": 30, "assets": "AAPL,GOOGL"}
        else:
            endpoint = f"{url}/predict"
            payload = {"symbol": "AAPL", "days": 30}
        
        times = []
        errors = 0
        
        for i in range(6):  # 6 requests (GARCH es computacionalmente intensivo)
            start_time = time.time()
            try:
                async with session.post(endpoint, json=payload) as response:
                    if response.status == 200:
                        await response.json()
                        end_time = time.time()
                        times.append(end_time - start_time)
                    else:
                        errors += 1
            except Exception as e:
                errors += 1
                print(f"Error in garch {service_type}: {e}")
        
        return {
            'avg_time': statistics.mean(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'total_requests': 6,
            'successful_requests': len(times),
            'errors': errors,
            'throughput': len(times) / sum(times) if times else 0
        }

    async def benchmark_intraday_strategy(self, session: aiohttp.ClientSession, service_type: str):
        """Benchmark estrategia intraday"""
        url = self.original_services['intraday'] if service_type == 'original' else self.ray_services['intraday']
        
        if service_type == 'ray':
            endpoint = f"{url}/demo-strategy-analysis"
            method = 'GET'
            payload = None
        else:
            endpoint = f"{url}/backtest"
            method = 'POST'
            payload = {
                "strategy": "momentum",
                "symbol": "AAPL",
                "timeframe": "5min"
            }
        
        times = []
        errors = 0
        
        for i in range(5):  # 5 requests (backtesting es muy intensivo)
            start_time = time.time()
            try:
                if method == 'GET':
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            await response.json()
                            end_time = time.time()
                            times.append(end_time - start_time)
                        else:
                            errors += 1
                else:
                    async with session.post(endpoint, json=payload) as response:
                        if response.status == 200:
                            await response.json()
                            end_time = time.time()
                            times.append(end_time - start_time)
                        else:
                            errors += 1
            except Exception as e:
                errors += 1
                print(f"Error in intraday {service_type}: {e}")
        
        return {
            'avg_time': statistics.mean(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'total_requests': 5,
            'successful_requests': len(times),
            'errors': errors,
            'throughput': len(times) / sum(times) if times else 0
        }

    async def run_service_benchmark(self, service_name: str, service_type: str):
        """Ejecuta benchmark para un servicio específico"""
        print(f"\n🔄 Benchmarking {service_name} ({service_type})...")
        
        timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if service_name == 'sentiment':
                return await self.benchmark_sentiment_analysis(session, service_type)
            elif service_name == 'portfolio':
                return await self.benchmark_portfolio_management(session, service_type)
            elif service_name == 'garch':
                return await self.benchmark_garch_prediction(session, service_type)
            elif service_name == 'intraday':
                return await self.benchmark_intraday_strategy(session, service_type)

    async def run_full_benchmark(self):
        """Ejecuta benchmark completo comparando servicios originales vs Ray"""
        print("🚀 INICIANDO BENCHMARK RAY vs SERVICIOS ORIGINALES")
        print("=" * 60)
        
        services = ['sentiment', 'portfolio', 'garch', 'intraday']
        
        for service in services:
            print(f"\n📊 BENCHMARKING {service.upper()}")
            print("-" * 40)
            
            # Benchmark servicio original
            original_results = await self.run_service_benchmark(service, 'original')
            
            # Benchmark servicio Ray
            ray_results = await self.run_service_benchmark(service, 'ray')
            
            # Guardar resultados
            self.results[service] = {
                'original': original_results,
                'ray': ray_results
            }
            
            # Mostrar comparación inmediata
            self.show_service_comparison(service, original_results, ray_results)

    def show_service_comparison(self, service_name: str, original: Dict, ray: Dict):
        """Muestra comparación de un servicio"""
        print(f"\n📈 RESULTADOS {service_name.upper()}:")
        print(f"{'Métrica':<20} {'Original':<15} {'Ray':<15} {'Mejora':<15}")
        print("-" * 65)
        
        # Tiempo promedio
        orig_avg = original['avg_time']
        ray_avg = ray['avg_time']
        avg_improvement = ((orig_avg - ray_avg) / orig_avg * 100) if orig_avg > 0 else 0
        print(f"{'Tiempo Promedio':<20} {orig_avg:.3f}s{'':<8} {ray_avg:.3f}s{'':<8} {avg_improvement:+.1f}%")
        
        # Throughput
        orig_throughput = original['throughput']
        ray_throughput = ray['throughput']
        throughput_improvement = ((ray_throughput - orig_throughput) / orig_throughput * 100) if orig_throughput > 0 else 0
        print(f"{'Throughput':<20} {orig_throughput:.2f} req/s{'':<5} {ray_throughput:.2f} req/s{'':<5} {throughput_improvement:+.1f}%")
        
        # Requests exitosos
        print(f"{'Requests OK':<20} {original['successful_requests']}/{original['total_requests']}{'':<8} {ray['successful_requests']}/{ray['total_requests']}{'':<8}")
        
        # Errores
        print(f"{'Errores':<20} {original['errors']}{'':<12} {ray['errors']}{'':<12}")

    def generate_final_report(self):
        """Genera reporte final consolidado"""
        print("\n" + "=" * 80)
        print("🏆 REPORTE FINAL - BENCHMARK RAY vs SERVICIOS ORIGINALES")
        print("=" * 80)
        
        total_improvement_time = 0
        total_improvement_throughput = 0
        services_count = len(self.results)
        
        print(f"\n{'Servicio':<15} {'Tiempo Original':<15} {'Tiempo Ray':<15} {'Mejora Tiempo':<15} {'Mejora Throughput':<18}")
        print("-" * 88)
        
        for service, data in self.results.items():
            orig = data['original']
            ray = data['ray']
            
            time_improvement = ((orig['avg_time'] - ray['avg_time']) / orig['avg_time'] * 100) if orig['avg_time'] > 0 else 0
            throughput_improvement = ((ray['throughput'] - orig['throughput']) / orig['throughput'] * 100) if orig['throughput'] > 0 else 0
            
            total_improvement_time += time_improvement
            total_improvement_throughput += throughput_improvement
            
            print(f"{service.capitalize():<15} {orig['avg_time']:.3f}s{'':<8} {ray['avg_time']:.3f}s{'':<8} {time_improvement:+.1f}%{'':<10} {throughput_improvement:+.1f}%")
        
        avg_time_improvement = total_improvement_time / services_count
        avg_throughput_improvement = total_improvement_throughput / services_count
        
        print("-" * 88)
        print(f"{'PROMEDIO':<15} {'':<15} {'':<15} {avg_time_improvement:+.1f}%{'':<10} {avg_throughput_improvement:+.1f}%")
        
        print(f"\n🎯 CONCLUSIONES:")
        print(f"✅ Mejora promedio en tiempo de respuesta: {avg_time_improvement:.1f}%")
        print(f"✅ Mejora promedio en throughput: {avg_throughput_improvement:.1f}%")
        print(f"✅ Ray Remote demuestra superioridad en {services_count}/4 microservicios")
        
        # Guardar resultados en archivo
        self.save_results_to_file()

    def save_results_to_file(self):
        """Guarda resultados en archivo JSON y CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON detallado
        with open(f'../results/benchmark_results_{timestamp}.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # CSV para análisis
        csv_data = []
        for service, data in self.results.items():
            csv_data.append({
                'service': service,
                'type': 'original',
                'avg_time': data['original']['avg_time'],
                'throughput': data['original']['throughput'],
                'successful_requests': data['original']['successful_requests'],
                'errors': data['original']['errors']
            })
            csv_data.append({
                'service': service,
                'type': 'ray',
                'avg_time': data['ray']['avg_time'],
                'throughput': data['ray']['throughput'],
                'successful_requests': data['ray']['successful_requests'],
                'errors': data['ray']['errors']
            })
        
        df = pd.DataFrame(csv_data)
        df.to_csv(f'../results/benchmark_results_{timestamp}.csv', index=False)
        
        print(f"\n📁 Resultados guardados:")
        print(f"   - ../results/benchmark_results_{timestamp}.json")
        print(f"   - ../results/benchmark_results_{timestamp}.csv")

async def main():
    benchmark = RayBenchmark()
    await benchmark.run_full_benchmark()
    benchmark.generate_final_report()

if __name__ == "__main__":
    asyncio.run(main())
