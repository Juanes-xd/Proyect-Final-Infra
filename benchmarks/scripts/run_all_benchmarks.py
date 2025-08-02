#!/usr/bin/env python3
"""
Script Maestro: Ejecuta todos los benchmarks y genera todas las gráficas
"""

import subprocess
import time
import sys
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el progreso"""
    print(f"\n🚀 {description}")
    print(f"📝 Ejecutando: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} - COMPLETADO")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🎯 BENCHMARK MAESTRO - Generación Completa de Resultados")
    print("=" * 60)
    
    # Cambiar al directorio de scripts
    scripts_dir = Path(__file__).parent
    results_dir = scripts_dir.parent / "results"
    
    print(f"📁 Directorio de trabajo: {scripts_dir}")
    print(f"📁 Directorio de resultados: {results_dir}")
    
    # Lista de tareas a ejecutar
    tasks = [
        {
            "command": "python sequential_vs_parallel_benchmark.py",
            "description": "Benchmark Secuencial vs Paralelo",
            "wait_time": 3
        },
        {
            "command": "python benchmark_functional.py",
            "description": "Benchmark Funcional (Métricas Individuales)",
            "wait_time": 3
        },
        {
            "command": "python generate_comparison_charts.py",
            "description": "Generar Gráficas de Comparación",
            "wait_time": 2
        },
        {
            "command": "python generate_charts.py",
            "description": "Generar Gráficas de Rendimiento Individual",
            "wait_time": 1
        }
    ]
    
    successful_tasks = 0
    
    for i, task in enumerate(tasks, 1):
        print(f"\n📊 TAREA {i}/{len(tasks)}")
        
        success = run_command(task["command"], task["description"])
        
        if success:
            successful_tasks += 1
            if task["wait_time"] > 0:
                print(f"⏱️  Esperando {task['wait_time']} segundos...")
                time.sleep(task["wait_time"])
        else:
            print(f"⚠️  Error en tarea {i}, continuando con la siguiente...")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Tareas completadas: {successful_tasks}/{len(tasks)}")
    
    if successful_tasks == len(tasks):
        print("🎉 ¡Todos los benchmarks y gráficas generados exitosamente!")
    else:
        print("⚠️  Algunas tareas no se completaron correctamente")
    
    # Listar archivos generados
    print(f"\n📁 Archivos generados en {results_dir}:")
    if results_dir.exists():
        files = list(results_dir.glob("*"))
        files = [f for f in files if f.name not in ['.gitkeep']]
        
        json_files = [f for f in files if f.suffix == '.json']
        png_files = [f for f in files if f.suffix == '.png']
        other_files = [f for f in files if f.suffix not in ['.json', '.png']]
        
        if json_files:
            print("\n📊 Archivos de datos (JSON):")
            for file in sorted(json_files):
                print(f"  • {file.name}")
        
        if png_files:
            print("\n📈 Gráficas generadas (PNG):")
            for file in sorted(png_files):
                print(f"  • {file.name}")
        
        if other_files:
            print("\n📄 Otros archivos:")
            for file in sorted(other_files):
                print(f"  • {file.name}")
        
        print(f"\n📊 Total de archivos: {len(files)}")
    else:
        print("❌ Directorio de resultados no encontrado")

if __name__ == "__main__":
    main()
