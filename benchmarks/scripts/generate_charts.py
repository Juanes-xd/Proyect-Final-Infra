#!/usr/bin/env python3
"""
Generador de Gráficas para Resultados de Benchmark
Analiza los resultados y genera visualizaciones detalladas
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import os

# Configurar el estilo de las gráficas
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_benchmark_results():
    """Carga los resultados del benchmark"""
    results_path = Path('../results/benchmark_results.json')
    if not results_path.exists():
        print(f"❌ No se encontró el archivo de resultados en {results_path}")
        return None
    
    with open(results_path, 'r') as f:
        return json.load(f)

def create_response_time_comparison(data):
    """Crea gráfica de comparación de tiempos de respuesta"""
    services = ['sentiment', 'garch', 'portfolio', 'intraday']
    avg_times = [data[service]['avg_time'] for service in services]
    std_times = [data[service]['std_time'] for service in services]
    
    plt.figure(figsize=(12, 8))
    
    # Gráfica de barras con barras de error
    bars = plt.bar(services, avg_times, yerr=std_times, capsize=5, 
                   color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
                   alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Agregar valores encima de las barras
    for i, (service, avg_time) in enumerate(zip(services, avg_times)):
        plt.text(i, avg_time + std_times[i] + 0.01, f'{avg_time:.3f}s', 
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.title('📊 Comparación de Tiempos de Respuesta por Microservicio', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Microservicios', fontsize=12, fontweight='bold')
    plt.ylabel('Tiempo Promedio (segundos)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Agregar línea de tiempo objetivo (ejemplo: 0.5s)
    plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, 
                label='Objetivo: 0.5s')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('../results/response_time_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_distribution(data):
    """Crea gráficas de distribución de rendimiento"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('📈 Distribución de Tiempos de Respuesta por Servicio', 
                 fontsize=16, fontweight='bold')
    
    services = ['sentiment', 'garch', 'portfolio', 'intraday']
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    for i, (service, color) in enumerate(zip(services, colors)):
        row, col = i // 2, i % 2
        ax = axes[row, col]
        
        times = data[service]['times']
        
        # Histograma
        ax.hist(times, bins=8, alpha=0.7, color=color, edgecolor='black')
        ax.axvline(data[service]['avg_time'], color='red', linestyle='--', 
                   linewidth=2, label=f'Promedio: {data[service]["avg_time"]:.3f}s')
        
        ax.set_title(f'{service.capitalize()} Service', fontweight='bold')
        ax.set_xlabel('Tiempo (segundos)')
        ax.set_ylabel('Frecuencia')
        ax.legend()
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/performance_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_concurrent_analysis(data):
    """Analiza los resultados de pruebas concurrentes"""
    concurrent_data = data['concurrent']
    results = concurrent_data['results']
    
    # Crear DataFrame para análisis
    df = pd.DataFrame(results)
    
    # Gráfica 1: Success Rate por servicio
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Success rate
    plt.subplot(2, 2, 1)
    success_by_service = df.groupby('service').agg({
        'success': ['count', 'sum']
    }).round(3)
    success_by_service.columns = ['total', 'successful']
    success_by_service['success_rate'] = success_by_service['successful'] / success_by_service['total']
    
    bars = plt.bar(success_by_service.index, success_by_service['success_rate'], 
                   color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], alpha=0.8)
    
    # Agregar porcentajes
    for bar, rate in zip(bars, success_by_service['success_rate']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('🎯 Tasa de Éxito por Servicio (Concurrente)', fontweight='bold')
    plt.ylabel('Tasa de Éxito')
    plt.ylim(0, 1.1)
    plt.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Tiempo de respuesta por servicio (solo exitosos)
    plt.subplot(2, 2, 2)
    successful_df = df[df['success'] == True]
    
    if not successful_df.empty:
        services_with_success = successful_df['service'].unique()
        avg_times = [successful_df[successful_df['service'] == s]['time'].mean() 
                    for s in services_with_success]
        
        plt.bar(services_with_success, avg_times, 
                color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], alpha=0.8)
        
        for i, (service, time) in enumerate(zip(services_with_success, avg_times)):
            plt.text(i, time + 0.1, f'{time:.3f}s', 
                    ha='center', va='bottom', fontweight='bold')
    
    plt.title('⏱️ Tiempo Promedio (Requests Exitosos)', fontweight='bold')
    plt.ylabel('Tiempo (segundos)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Subplot 3: Timeline de requests
    plt.subplot(2, 1, 2)
    
    # Simular timeline (ya que no tenemos timestamps exactos)
    cumulative_time = 0
    timeline_data = []
    
    for i, result in enumerate(results):
        timeline_data.append({
            'request_id': i,
            'service': result['service'],
            'time': result['time'],
            'success': result['success'],
            'cumulative_time': cumulative_time
        })
        cumulative_time += result['time']
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Scatter plot por servicio
    services = timeline_df['service'].unique()
    colors_dict = {'sentiment': '#3498db', 'garch': '#e74c3c', 
                   'portfolio': '#2ecc71', 'intraday': '#f39c12'}
    
    for service in services:
        service_data = timeline_df[timeline_df['service'] == service]
        successful = service_data[service_data['success'] == True]
        failed = service_data[service_data['success'] == False]
        
        if not successful.empty:
            plt.scatter(successful['request_id'], successful['time'], 
                       c=colors_dict.get(service, 'gray'), label=f'{service} (exitoso)',
                       alpha=0.7, s=60)
        
        if not failed.empty:
            plt.scatter(failed['request_id'], failed['time'], 
                       c=colors_dict.get(service, 'gray'), marker='x', 
                       label=f'{service} (fallido)', s=80)
    
    plt.title('🔄 Timeline de Requests Concurrentes', fontweight='bold')
    plt.xlabel('Request ID')
    plt.ylabel('Tiempo de Respuesta (segundos)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/concurrent_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_summary_report(data):
    """Crea un reporte resumen visual"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📋 Reporte Resumen del Benchmark', fontsize=18, fontweight='bold')
    
    # 1. Ranking de servicios por velocidad
    services = ['sentiment', 'garch', 'portfolio', 'intraday']
    avg_times = [data[service]['avg_time'] for service in services]
    
    # Ordenar por velocidad (menor tiempo = mejor)
    sorted_data = sorted(zip(services, avg_times), key=lambda x: x[1])
    sorted_services, sorted_times = zip(*sorted_data)
    
    bars1 = ax1.barh(sorted_services, sorted_times, 
                     color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
    ax1.set_title('🏆 Ranking por Velocidad', fontweight='bold')
    ax1.set_xlabel('Tiempo Promedio (segundos)')
    
    # Agregar valores
    for i, (service, time) in enumerate(zip(sorted_services, sorted_times)):
        ax1.text(time + 0.01, i, f'{time:.3f}s', va='center', fontweight='bold')
    
    # 2. Métricas de rendimiento general
    throughput_data = {
        'Sentiment': 1/data['sentiment']['avg_time'],
        'GARCH': 1/data['garch']['avg_time'],
        'Portfolio': 1/data['portfolio']['avg_time'],
        'Intraday': 1/data['intraday']['avg_time']
    }
    
    ax2.bar(throughput_data.keys(), throughput_data.values(), 
            color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], alpha=0.8)
    ax2.set_title('📈 Throughput (Requests/Segundo)', fontweight='bold')
    ax2.set_ylabel('Requests por Segundo')
    ax2.tick_params(axis='x', rotation=45)
    
    # Agregar valores
    for i, (service, tps) in enumerate(throughput_data.items()):
        ax2.text(i, tps + 0.5, f'{tps:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Estabilidad (menor desviación estándar = más estable)
    std_times = [data[service]['std_time'] for service in services]
    colors_stability = ['#2ecc71' if std < 0.05 else '#f39c12' if std < 0.1 else '#e74c3c' 
                       for std in std_times]
    
    bars3 = ax3.bar(services, std_times, color=colors_stability, alpha=0.8)
    ax3.set_title('📊 Estabilidad (Desviación Estándar)', fontweight='bold')
    ax3.set_ylabel('Desviación Estándar (segundos)')
    ax3.tick_params(axis='x', rotation=45)
    
    # Agregar valores y clasificación
    for i, (service, std) in enumerate(zip(services, std_times)):
        stability = "Excelente" if std < 0.05 else "Buena" if std < 0.1 else "Mejorable"
        ax3.text(i, std + 0.005, f'{std:.3f}\n{stability}', 
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 4. Resumen de pruebas concurrentes
    concurrent = data['concurrent']
    pie_data = [concurrent['successful_requests'], 
                concurrent['total_requests'] - concurrent['successful_requests']]
    pie_labels = ['Exitosos', 'Fallidos']
    colors_pie = ['#2ecc71', '#e74c3c']
    
    wedges, texts, autotexts = ax4.pie(pie_data, labels=pie_labels, colors=colors_pie, 
                                       autopct='%1.1f%%', startangle=90)
    ax4.set_title('🎯 Resultados Pruebas Concurrentes', fontweight='bold')
    
    # Agregar información adicional
    success_rate = concurrent['success_rate'] * 100
    avg_response = concurrent['avg_response_time']
    
    ax4.text(0, -1.3, f'Tasa de Éxito: {success_rate:.1f}%\n'
                      f'Tiempo Promedio: {avg_response:.3f}s\n'
                      f'Total Requests: {concurrent["total_requests"]}',
             ha='center', va='top', fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    
    plt.tight_layout()
    plt.savefig('../results/summary_report.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_metrics_table(data):
    """Crea una tabla con métricas detalladas"""
    metrics_data = []
    
    for service in ['sentiment', 'garch', 'portfolio', 'intraday']:
        service_data = data[service]
        metrics_data.append({
            'Servicio': service.capitalize(),
            'Tiempo Promedio (s)': f"{service_data['avg_time']:.4f}",
            'Tiempo Mínimo (s)': f"{service_data['min_time']:.4f}",
            'Tiempo Máximo (s)': f"{service_data['max_time']:.4f}",
            'Desviación Estándar': f"{service_data['std_time']:.4f}",
            'Throughput (req/s)': f"{1/service_data['avg_time']:.2f}",
            'Variabilidad': f"{(service_data['std_time']/service_data['avg_time']*100):.1f}%"
        })
    
    df = pd.DataFrame(metrics_data)
    
    # Crear la tabla visual
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns, 
                     cellLoc='center', loc='center')
    
    # Estilizar la tabla
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Colorear headers
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Colorear filas alternadas
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f8f9fa')
            else:
                table[(i, j)].set_facecolor('white')
    
    plt.title('📊 Tabla Detallada de Métricas de Rendimiento', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.savefig('../results/performance_metrics_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("🚀 Generando gráficas de benchmark...")
    
    # Crear directorio de resultados si no existe
    results_dir = Path('../results')
    results_dir.mkdir(exist_ok=True)
    
    # Cargar datos
    data = load_benchmark_results()
    if not data:
        return
    
    print("📊 Creando gráficas...")
    
    try:
        # Generar todas las gráficas
        create_response_time_comparison(data)
        print("✅ Gráfica de comparación de tiempos creada")
        
        create_performance_distribution(data)
        print("✅ Gráficas de distribución creadas")
        
        create_concurrent_analysis(data)
        print("✅ Análisis de concurrencia creado")
        
        create_summary_report(data)
        print("✅ Reporte resumen creado")
        
        create_performance_metrics_table(data)
        print("✅ Tabla de métricas creada")
        
        print("\n🎉 ¡Todas las gráficas generadas exitosamente!")
        print(f"📁 Resultados guardados en: {results_dir.absolute()}")
        
        # Listar archivos generados
        generated_files = list(results_dir.glob('*.png'))
        print(f"\n📈 Archivos generados ({len(generated_files)}):")
        for file in generated_files:
            print(f"  • {file.name}")
            
    except Exception as e:
        print(f"❌ Error generando gráficas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
