#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from reportes.models import ReporteDinamico
from reportes.query_builder import parse_prompt, build_query
import json

def test_report_generation():
    print("=== PRUEBA DE GENERACION DE REPORTES ===")
    
    # Crear un reporte de prueba
    prompt = "ventas del mes de noviembre"
    print(f"Prompt de prueba: {prompt}")
    
    try:
        # Parsear el prompt
        parsed_data = parse_prompt(prompt)
        print(f"Datos parseados: {parsed_data}")
        
        # Construir la consulta
        results = build_query(parsed_data)
        print(f"Resultados obtenidos: {len(results) if isinstance(results, list) else 'No es lista'}")
        
        # Crear el reporte en la base de datos
        reporte = ReporteDinamico.objects.create(
            prompt=prompt,
            results=json.dumps(results) if isinstance(results, list) else results
        )
        
        print(f"Reporte creado con ID: {reporte.id}")
        print(f"Prompt: {reporte.prompt}")
        print(f"Resultados: {reporte.results[:100]}..." if len(str(reporte.results)) > 100 else f"Resultados: {reporte.results}")
        
        return reporte.id
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_existing_reports():
    print("\n=== REPORTES EXISTENTES ===")
    reportes = ReporteDinamico.objects.all()
    
    if reportes.exists():
        print(f"Se encontraron {reportes.count()} reportes:")
        for reporte in reportes:
            print(f"  ID: {reporte.id} - Prompt: {reporte.prompt}")
    else:
        print("No hay reportes en la base de datos")
    
    return reportes.first().id if reportes.exists() else None

if __name__ == '__main__':
    # Probar reportes existentes
    existing_id = test_existing_reports()
    
    # Generar nuevo reporte
    new_id = test_report_generation()
    
    print(f"\n=== RESUMEN ===")
    print(f"ID de reporte existente: {existing_id}")
    print(f"ID de nuevo reporte: {new_id}")
    
    test_id = new_id or existing_id
    if test_id:
        print(f"\nPuedes probar la descarga con:")
        print(f"GET /api/v1/reportes/generate/?query_id={test_id}&formato=pdf")
        print(f"GET /api/v1/reportes/generate/?query_id={test_id}&formato=xlsx")
