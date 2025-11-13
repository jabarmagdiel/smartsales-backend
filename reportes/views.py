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
from io import BytesIO

# Importaciones condicionales para reportes
try:
    from openpyxl import Workbook
    from weasyprint import HTML
    HAS_REPORT_LIBS = True
    WEASYPRINT_INSTALLED = True
except (ImportError, OSError) as e:
    HAS_REPORT_LIBS = False
    WEASYPRINT_INSTALLED = False
    Workbook = None
    HTML = None
    print("ADVERTENCIA: WeasyPrint y openpyxl no están disponibles. La generación de reportes PDF/Excel puede fallar.")
    print("Sigue las instrucciones: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation")


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
        # Acepta ambos nombres: 'formato' (ES) y 'format' (EN)
        formato = request.GET.get('formato') or request.GET.get('format') or 'json'

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

            # --- (2) SOLUCIÓN PDF: Usando ReportLab ---
            elif formato == 'pdf':
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib import colors
                from io import BytesIO
                
                # Crear buffer en memoria
                buffer = BytesIO()
                
                # Crear documento PDF
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []
                
                # Título
                title = Paragraph(f"Reporte Dinámico - {reporte.prompt}", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))
                
                # Información del reporte
                info = Paragraph(f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
                elements.append(info)
                elements.append(Spacer(1, 12))
                
                if results:
                    # Crear tabla con los datos
                    headers = list(results[0].keys())
                    data = [headers]
                    
                    for row in results:
                        data.append([str(value) for value in row.values()])
                    
                    # Crear tabla
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ]))
                    elements.append(table)
                else:
                    no_data = Paragraph("No se encontraron datos para mostrar.", styles['Normal'])
                    elements.append(no_data)
                
                # Construir PDF
                doc.build(elements)
                
                # Obtener contenido del buffer
                pdf_content = buffer.getvalue()
                buffer.close()
                
                # Crear respuesta HTTP
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="reporte_{query_id}.pdf"'
                return response

            elif formato == 'xlsx':
                if not HAS_REPORT_LIBS or not Workbook:
                    return Response({
                        'error': 'Excel export not available',
                        'message': 'openpyxl library is required for Excel exports'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                # Generar Excel con openpyxl
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