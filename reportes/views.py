from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .query_builder import parse_prompt, build_query
from .models import ReporteDinamico
from permissions import IsAdmin
import json
import datetime
from openpyxl import Workbook
from io import BytesIO

# --- (1) SOLUCIÓN PDF: Importar WeasyPrint ---
# WeasyPrint es la librería para generar PDF desde HTML.
try:
    from weasyprint import HTML
    WEASYPRINT_INSTALLED = True
except ImportError:
    WEASYPRINT_INSTALLED = False
    print("ADVERTENCIA: WeasyPrint no está instalado. La generación de PDF fallará.")
    print("Instálalo con: pip install weasyprint")


class QueryReportView(APIView):
    """
    Endpoint POST /api/v1/reportes/query/
    Recibe un prompt de texto y genera un reporte dinámico.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parsear el prompt
            parsed_data = parse_prompt(prompt)

            # Construir la consulta
            queryset, select_fields = build_query(parsed_data)

            # Ejecutar la consulta (limitada para preview)
            results = list(queryset.values(*select_fields)[:100])  # Limitar a 100 registros

            # --- Corrección de Serialización (Decimal y Datetime) ---
            for result in results:
                for key, value in result.items():
                    if hasattr(value, '__float__'):
                        result[key] = float(value)
                    elif isinstance(value, (datetime.date, datetime.datetime)):
                        result[key] = value.isoformat()

            # Guardar en ReporteDinamico (los 'results' ya están limpios)
            consulta_str = str(queryset.query)
            reporte = ReporteDinamico.objects.create(
                prompt_original=prompt,
                consulta_resultante=consulta_str,
                results=results 
            )

            # Preparar respuesta
            response_data = {
                'query_id': reporte.id, 
                'parsed_data': parsed_data,
                'query': consulta_str,
                'results': results, 
                'total_records': len(results),
                'format': parsed_data.get('format', 'json')
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateReportView(APIView):
    """
    Endpoint GET /api/v1/reportes/generate/
    Recibe query_id y formato (pdf, xlsx, json) y genera el archivo correspondiente.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        query_id = request.GET.get('query_id')
        formato = request.GET.get('formato', 'json')

        if not query_id:
            return Response({'error': 'query_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reporte = ReporteDinamico.objects.get(id=query_id)
            
            if isinstance(reporte.results, str):
                results = json.loads(reporte.results)
            else:
                results = reporte.results

            if formato == 'json':
                # Paginación para JSON
                paginator = PageNumberPagination()
                paginator.page_size = 20
                page = paginator.paginate_queryset(results, request)
                return paginator.get_paginated_response(page)

            # --- (2) SOLUCIÓN PDF: Lógica de Generación Real ---
            elif formato == 'pdf':
                
                if not WEASYPRINT_INSTALLED:
                    # Si WeasyPrint no está instalado, devuelve un error claro.
                    return Response(
                        {'error': 'La generación de PDF no está configurada en el servidor (WeasyPrint no encontrado).'}, 
                        status=status.HTTP_501_NOT_IMPLEMENTED
                    )
                
                # Generar el contenido HTML de la tabla
                html_content = self.generate_html_table(results)
                
                # Convertir HTML a PDF en memoria
                pdf_file = HTML(string=html_content).write_pdf()
                
                # Crear la respuesta HTTP con el archivo PDF real
                response = HttpResponse(pdf_file, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="reporte_{query_id}.pdf"'
                return response

            elif formato == 'xlsx':
                # Generar Excel con openpyxl (Esto ya funciona)
                wb = Workbook()
                ws = wb.active
                ws.title = "Reporte"

                if results:
                    headers = list(results[0].keys())
                    ws.append(headers)
                    for row in results:
                        ws.append(list(row.values()))

                excel_buffer = BytesIO()
                wb.save(excel_buffer)
                excel_buffer.seek(0)

                response = HttpResponse(excel_buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="reporte_{query_id}.xlsx"'
                return response

            else:
                return Response({'error': 'Formato no soportado. Use pdf, xlsx o json.'}, status=status.HTTP_400_BAD_REQUEST)

        except ReporteDinamico.DoesNotExist:
            return Response({'error': 'Reporte no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_html_table(self, results):
        """Genera HTML simple para el PDF. (Tu función original estaba bien)"""
        html = "<html><head><style>"
        html += "table { border-collapse: collapse; width: 100%; } "
        html += "th, td { border: 1px solid black; padding: 8px; text-align: left; } "
        html += "th { background-color: #f2f2f2; } "
        html += "</style></head><body><h1>Reporte Dinámico</h1><table><tr>"

        if results:
            headers = list(results[0].keys())
            for header in headers:
                html += f"<th>{header}</th>"
            html += "</tr>"

            for row in results:
                html += "<tr>"
                for value in row.values():
                    html += f"<td>{value}</td>"
                html += "</tr>"

        html += "</table></body></html>"
        return html