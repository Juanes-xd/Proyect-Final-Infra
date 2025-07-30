"""
Script para mostrar resumen de archivos de benchmark organizados
"""
import os
from datetime import datetime

def show_benchmark_files():
    print("📁 ARCHIVOS DE BENCHMARK ORGANIZADOS")
    print("=" * 50)
    
    results_dir = "benchmarks/results"
    
    if not os.path.exists(results_dir):
        print(f"❌ Directorio {results_dir} no encontrado")
        return
    
    files = os.listdir(results_dir)
    files.sort()
    
    # Categorizar archivos
    json_files = [f for f in files if f.endswith('.json')]
    png_files = [f for f in files if f.endswith('.png')]
    txt_files = [f for f in files if f.endswith('.txt')]
    md_files = [f for f in files if f.endswith('.md')]
    
    print(f"\n📊 DATOS DE BENCHMARK ({len(json_files)} archivos):")
    for file in json_files:
        file_path = os.path.join(results_dir, file)
        size = os.path.getsize(file_path)
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   📄 {file} ({size:,} bytes) - {mod_time_str}")
    
    print(f"\n📈 GRÁFICAS ({len(png_files)} archivos):")
    for file in png_files:
        file_path = os.path.join(results_dir, file)
        size = os.path.getsize(file_path)
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        
        if "comparison" in file:
            icon = "🔄"
            desc = "Comparación secuencial vs Ray"
        elif "detailed" in file:
            icon = "📊"
            desc = "Métricas detalladas"
        elif "latest" in file:
            icon = "🆕"
            desc = "Última comparación generada"
        else:
            icon = "📈"
            desc = "Gráfica de benchmark"
            
        print(f"   {icon} {file} ({size:,} bytes) - {desc}")
        print(f"      📅 {mod_time_str}")
    
    print(f"\n📝 REPORTES ({len(txt_files)} archivos):")
    for file in txt_files:
        file_path = os.path.join(results_dir, file)
        size = os.path.getsize(file_path)
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   📄 {file} ({size:,} bytes) - {mod_time_str}")
    
    print(f"\n📋 DOCUMENTACIÓN ({len(md_files)} archivos):")
    for file in md_files:
        file_path = os.path.join(results_dir, file)
        size = os.path.getsize(file_path)
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   📖 {file} ({size:,} bytes) - {mod_time_str}")
    
    # Mostrar estructura recomendada
    print(f"\n🗂️  ESTRUCTURA ORGANIZADA:")
    print(f"   📁 benchmarks/")
    print(f"   ├── 📁 results/")
    print(f"   │   ├── 📄 benchmark_results.json (datos originales)")
    print(f"   │   ├── 📄 ray_benchmark_results.json (datos Ray - pendiente)")
    print(f"   │   ├── 📈 benchmark_comparison_latest.png (gráfica principal)")
    print(f"   │   ├── 📊 detailed_metrics_*.png (métricas detalladas)")
    print(f"   │   ├── 📝 benchmark_report_*.txt (reportes)")
    print(f"   │   └── 📖 REPORTE_FINAL_PROYECTO.md (documentación)")
    print(f"   ├── 📁 scripts/")
    print(f"   │   ├── 🐍 benchmark_original.py")
    print(f"   │   ├── 🐍 ray_comparison_benchmark.py")
    print(f"   │   └── 🐍 otros scripts...")
    print(f"   └── 📄 requirements.txt")
    
    print(f"\n🎯 ARCHIVOS PRINCIPALES PARA REPORTE:")
    print(f"   📊 {results_dir}/benchmark_comparison_latest.png")
    print(f"   📄 {results_dir}/benchmark_results.json")
    print(f"   📖 {results_dir}/REPORTE_FINAL_PROYECTO.md")
    
    print(f"\n💡 COMANDOS ÚTILES:")
    print(f"   📊 Ver resultados: python show_results.py")
    print(f"   📈 Generar gráficas: python generate_benchmark_charts.py")
    print(f"   🔄 Ejecutar benchmark: python benchmarks/scripts/benchmark_original.py")

if __name__ == "__main__":
    show_benchmark_files()
