#!/usr/bin/env python3
"""
Generador de Gráficas para Comparación Secuencial vs Paralelo
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import glob
from datetime import datetime

# Configurar el estilo de las gráficas
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_comparison_results():
    """Carga los resultados de comparación más recientes"""
    results_dir = Path('../results')
    
    # Buscar el archivo más reciente de comparación
    comparison_files = list(results_dir.glob('sequential_vs_parallel_*.json'))
    
    if not comparison_files:
        print("❌ No se encontraron archivos de comparación")
        return None
    
    # Ordenar por fecha de modificación y tomar el más reciente
    latest_file = max(comparison_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Cargando resultados desde: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def create_time_comparison_chart(data):
    """Crea gráfica de comparación de tiempos totales"""
    services = list(data.keys())
    
    # Calcular tiempos totales
    sequential_times = []
    parallel_times = []
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        if seq['successful_requests'] > 0 and par['successful_requests'] > 0:
            seq_total = sum(seq['times'])
            par_total = max(par['times']) if par['times'] else 0
            
            sequential_times.append(seq_total)
            parallel_times.append(par_total)
        else:
            sequential_times.append(0)
            parallel_times.append(0)
    
    # Configurar la gráfica
    x = np.arange(len(services))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, sequential_times, width, label='Secuencial', 
                   color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + width/2, parallel_times, width, label='Paralelo', 
                   color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Agregar valores encima de las barras
    for i, (seq_time, par_time) in enumerate(zip(sequential_times, parallel_times)):
        if seq_time > 0:
            ax.text(i - width/2, seq_time + 0.01, f'{seq_time:.2f}s', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        if par_time > 0:
            ax.text(i + width/2, par_time + 0.01, f'{par_time:.2f}s', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Configurar ejes y títulos
    ax.set_xlabel('Microservicios', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tiempo Total (segundos)', fontsize=12, fontweight='bold')
    ax.set_title('⚡ Comparación de Tiempos: Procesamiento Secuencial vs Paralelo', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in services])
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/sequential_vs_parallel_time_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_throughput_comparison_chart(data):
    """Crea gráfica de comparación de throughput"""
    services = list(data.keys())
    
    sequential_throughput = []
    parallel_throughput = []
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        sequential_throughput.append(seq['throughput'])
        parallel_throughput.append(par['throughput'])
    
    x = np.arange(len(services))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, sequential_throughput, width, label='Secuencial', 
                   color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + width/2, parallel_throughput, width, label='Paralelo', 
                   color='#f39c12', alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Agregar valores encima de las barras
    for i, (seq_tp, par_tp) in enumerate(zip(sequential_throughput, parallel_throughput)):
        if seq_tp > 0:
            ax.text(i - width/2, seq_tp + 0.2, f'{seq_tp:.1f}', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        if par_tp > 0:
            ax.text(i + width/2, par_tp + 0.2, f'{par_tp:.1f}', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_xlabel('Microservicios', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (requests/segundo)', fontsize=12, fontweight='bold')
    ax.set_title('📈 Comparación de Throughput: Secuencial vs Paralelo', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in services])
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/sequential_vs_parallel_throughput_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_improvement_analysis(data):
    """Crea análisis de mejoras"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📊 Análisis de Mejoras: Paralelo vs Secuencial', fontsize=18, fontweight='bold')
    
    services = list(data.keys())
    improvements = []
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        if seq['successful_requests'] > 0 and par['successful_requests'] > 0:
            # Tiempo total
            seq_total = sum(seq['times'])
            par_total = max(par['times']) if par['times'] else 0
            
            if par_total > 0:
                time_improvement = ((seq_total - par_total) / seq_total) * 100
                throughput_improvement = ((par['throughput'] - seq['throughput']) / seq['throughput']) * 100
                
                improvements.append({
                    'service': service,
                    'time_improvement': time_improvement,
                    'throughput_improvement': throughput_improvement
                })
    
    if not improvements:
        print("❌ No hay datos suficientes para generar análisis de mejoras")
        return
    
    # 1. Mejoras en tiempo
    services_list = [item['service'].capitalize() for item in improvements]
    time_improvements = [item['time_improvement'] for item in improvements]
    
    colors_time = ['#2ecc71' if x > 0 else '#e74c3c' for x in time_improvements]
    bars1 = ax1.bar(services_list, time_improvements, color=colors_time, alpha=0.8)
    ax1.set_title('⏱️ Mejora en Tiempo Total (%)', fontweight='bold')
    ax1.set_ylabel('Mejora (%)')
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax1.grid(axis='y', alpha=0.3)
    
    # Agregar valores
    for bar, improvement in zip(bars1, time_improvements):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -3),
                f'{improvement:.1f}%', ha='center', va='bottom' if height > 0 else 'top',
                fontweight='bold')
    
    # 2. Mejoras en throughput
    throughput_improvements = [item['throughput_improvement'] for item in improvements]
    colors_throughput = ['#2ecc71' if x > 0 else '#e74c3c' for x in throughput_improvements]
    bars2 = ax2.bar(services_list, throughput_improvements, color=colors_throughput, alpha=0.8)
    ax2.set_title('📈 Mejora en Throughput (%)', fontweight='bold')
    ax2.set_ylabel('Mejora (%)')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(axis='y', alpha=0.3)
    
    # Agregar valores
    for bar, improvement in zip(bars2, throughput_improvements):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (2 if height > 0 else -5),
                f'{improvement:.1f}%', ha='center', va='bottom' if height > 0 else 'top',
                fontweight='bold')
    
    # 3. Distribución de tiempos por servicio
    ax3.set_title('📊 Distribución de Tiempos por Enfoque', fontweight='bold')
    
    all_seq_times = []
    all_par_times = []
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        all_seq_times.extend(seq['times'])
        all_par_times.extend(par['times'])
    
    if all_seq_times and all_par_times:
        ax3.hist(all_seq_times, bins=15, alpha=0.7, label='Secuencial', color='#e74c3c')
        ax3.hist(all_par_times, bins=15, alpha=0.7, label='Paralelo', color='#2ecc71')
        ax3.set_xlabel('Tiempo (segundos)')
        ax3.set_ylabel('Frecuencia')
        ax3.legend()
        ax3.grid(alpha=0.3)
    
    # 4. Eficiencia por servicio
    ax4.set_title('⚡ Eficiencia Relativa', fontweight='bold')
    
    efficiency_ratios = []
    for item in improvements:
        # Ratio de eficiencia: cuánto más eficiente es el paralelo
        service_data = data[item['service']]
        seq_total = sum(service_data['sequential']['times'])
        par_max = max(service_data['parallel']['times']) if service_data['parallel']['times'] else 1
        
        if par_max > 0:
            efficiency_ratio = seq_total / par_max
            efficiency_ratios.append(efficiency_ratio)
        else:
            efficiency_ratios.append(1)
    
    bars4 = ax4.bar(services_list, efficiency_ratios, color='#9b59b6', alpha=0.8)
    ax4.set_ylabel('Ratio de Eficiencia')
    ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Sin mejora')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # Agregar valores
    for bar, ratio in zip(bars4, efficiency_ratios):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{ratio:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../results/sequential_vs_parallel_improvement_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_summary_dashboard(data):
    """Crea un dashboard resumen"""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    fig.suptitle('🎯 Dashboard de Comparación: Secuencial vs Paralelo', fontsize=20, fontweight='bold')
    
    services = list(data.keys())
    
    # Calcular métricas globales
    total_seq_time = 0
    total_par_time = 0
    total_seq_requests = 0
    total_par_requests = 0
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        total_seq_time += sum(seq['times'])
        total_par_time += max(par['times']) if par['times'] else 0
        total_seq_requests += seq['successful_requests']
        total_par_requests += par['successful_requests']
    
    # Métricas principales (primera fila)
    ax1 = fig.add_subplot(gs[0, :2])
    metrics = ['Tiempo Total (s)', 'Requests Exitosos', 'Eficiencia Global']
    sequential_metrics = [total_seq_time, total_seq_requests, total_seq_requests/total_seq_time if total_seq_time > 0 else 0]
    parallel_metrics = [total_par_time, total_par_requests, total_par_requests/total_par_time if total_par_time > 0 else 0]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, sequential_metrics, width, label='Secuencial', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, parallel_metrics, width, label='Paralelo', color='#2ecc71', alpha=0.8)
    
    ax1.set_title('📊 Métricas Globales', fontweight='bold', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Agregar valores
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(sequential_metrics + parallel_metrics) * 0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Gráfica de mejoras por servicio (primera fila, derecha)
    ax2 = fig.add_subplot(gs[0, 2:])
    
    improvements = []
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        if seq['successful_requests'] > 0 and par['successful_requests'] > 0:
            seq_total = sum(seq['times'])
            par_total = max(par['times']) if par['times'] else 0
            
            if par_total > 0:
                improvement = ((seq_total - par_total) / seq_total) * 100
                improvements.append(improvement)
            else:
                improvements.append(0)
        else:
            improvements.append(0)
    
    colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in improvements]
    bars = ax2.bar([s.capitalize() for s in services], improvements, color=colors, alpha=0.8)
    ax2.set_title('⚡ Mejora en Tiempo por Servicio (%)', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Mejora (%)')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(axis='y', alpha=0.3)
    
    # Segunda fila: gráficas individuales por servicio
    for i, service in enumerate(services):
        ax = fig.add_subplot(gs[1, i])
        
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        if seq['times'] and par['times']:
            ax.boxplot([seq['times'], par['times']], labels=['Seq', 'Par'])
            ax.set_title(f'{service.capitalize()}', fontweight='bold')
            ax.set_ylabel('Tiempo (s)')
            ax.grid(alpha=0.3)
    
    # Tercera fila: análisis de distribución
    ax_dist = fig.add_subplot(gs[2, :])
    
    all_seq_times = []
    all_par_times = []
    
    for service in services:
        seq = data[service]['sequential']
        par = data[service]['parallel']
        
        all_seq_times.extend(seq['times'])
        all_par_times.extend(par['times'])
    
    if all_seq_times and all_par_times:
        ax_dist.hist(all_seq_times, bins=20, alpha=0.6, label='Secuencial', color='#e74c3c', density=True)
        ax_dist.hist(all_par_times, bins=20, alpha=0.6, label='Paralelo', color='#2ecc71', density=True)
        ax_dist.set_xlabel('Tiempo de Respuesta (segundos)')
        ax_dist.set_ylabel('Densidad')
        ax_dist.set_title('📈 Distribución de Tiempos de Respuesta', fontweight='bold', fontsize=14)
        ax_dist.legend()
        ax_dist.grid(alpha=0.3)
    
    plt.savefig('../results/sequential_vs_parallel_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("🚀 Generando gráficas de comparación Secuencial vs Paralelo...")
    
    # Crear directorio de resultados si no existe
    results_dir = Path('../results')
    results_dir.mkdir(exist_ok=True)
    
    # Cargar datos
    data = load_comparison_results()
    if not data:
        return
    
    print("📊 Creando gráficas de comparación...")
    
    try:
        # Generar todas las gráficas
        create_time_comparison_chart(data)
        print("✅ Gráfica de comparación de tiempos creada")
        
        create_throughput_comparison_chart(data)
        print("✅ Gráfica de comparación de throughput creada")
        
        create_improvement_analysis(data)
        print("✅ Análisis de mejoras creado")
        
        create_summary_dashboard(data)
        print("✅ Dashboard resumen creado")
        
        print("\n🎉 ¡Todas las gráficas de comparación generadas exitosamente!")
        print(f"📁 Resultados guardados en: {results_dir.absolute()}")
        
        # Listar archivos generados
        generated_files = list(results_dir.glob('sequential_vs_parallel_*.png'))
        print(f"\n📈 Archivos de comparación generados ({len(generated_files)}):")
        for file in generated_files:
            print(f"  • {file.name}")
            
    except Exception as e:
        print(f"❌ Error generando gráficas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
