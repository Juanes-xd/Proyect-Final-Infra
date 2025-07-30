"""
Script simple para mostrar los resultados del benchmark en formato texto
"""
import json
import os

def display_benchmark_results():
    print("🎯 RESULTADOS DEL BENCHMARK - MICROSERVICIOS")
    print("=" * 60)
    
    # Cargar resultados
    if not os.path.exists('benchmark_results.json'):
        print("❌ No se encontró el archivo benchmark_results.json")
        return
    
    with open('benchmark_results.json', 'r') as f:
        results = json.load(f)
    
    # Mostrar resultados por servicio
    print("\n📊 RENDIMIENTO POR SERVICIO:")
    print("-" * 40)
    
    services = {
        'sentiment': 'Sentiment Analyzer',
        'portfolio': 'Portfolio Manager', 
        'garch': 'GARCH Predictor',
        'intraday': 'Intraday Strategy'
    }
    
    for service_key, service_name in services.items():
        if service_key in results and 'avg_time' in results[service_key]:
            data = results[service_key]
            
            print(f"\n🔹 {service_name.upper()}:")
            print(f"   ⏱️  Tiempo promedio: {data['avg_time']:.3f}s")
            print(f"   🚀 Throughput est:   {1/data['avg_time']:.2f} req/s")
            print(f"   📈 Tiempo mínimo:    {data['min_time']:.3f}s")
            print(f"   📉 Tiempo máximo:    {data['max_time']:.3f}s")
            print(f"   📊 Desviación std:   {data['std_time']:.3f}s")
    
    # Análisis de concurrencia
    if 'concurrent' in results:
        concurrent = results['concurrent']
        print(f"\n🔄 PRUEBAS CONCURRENTES:")
        print(f"   ✅ Tasa de éxito: {concurrent['success_rate']*100:.1f}%")
        print(f"   📊 Requests totales: {concurrent['total_requests']}")
        print(f"   ✅ Requests exitosos: {concurrent['successful_requests']}")
        print(f"   ⏱️  Tiempo total: {concurrent['total_time']:.2f}s")
        print(f"   🚀 Throughput: {concurrent['successful_requests']/concurrent['total_time']:.2f} req/s")
    
    # Rankings
    print(f"\n🏆 RANKINGS:")
    print("-" * 20)
    
    # Servicio más rápido
    fastest = min(
        [(name, results[key]['avg_time']) for key, name in services.items() 
         if key in results and 'avg_time' in results[key]], 
        key=lambda x: x[1]
    )
    print(f"🥇 Más rápido: {fastest[0]} ({fastest[1]:.3f}s)")
    
    # Servicio más lento
    slowest = max(
        [(name, results[key]['avg_time']) for key, name in services.items() 
         if key in results and 'avg_time' in results[key]], 
        key=lambda x: x[1]
    )
    print(f"🐌 Más lento: {slowest[0]} ({slowest[1]:.3f}s)")
    
    # Más consistente (menor desviación)
    most_consistent = min(
        [(name, results[key]['std_time']) for key, name in services.items() 
         if key in results and 'std_time' in results[key]], 
        key=lambda x: x[1]
    )
    print(f"🎯 Más consistente: {most_consistent[0]} (std: {most_consistent[1]:.3f}s)")
    
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   • Optimizar {slowest[0]} (mayor tiempo de respuesta)")
    print(f"   • Implementar Ray Remote en servicios computacionalmente intensivos")
    print(f"   • Considerar cache para reducir latencia")
    
    print(f"\n📊 Gráficas disponibles:")
    if os.path.exists('benchmark_comparison_latest.png'):
        print(f"   ✅ benchmark_comparison_latest.png")
    else:
        print(f"   ❌ No se encontraron gráficas")

if __name__ == "__main__":
    display_benchmark_results()
