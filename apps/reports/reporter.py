from reportlab.lib import colors
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter, landscape
import csv
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
from dateutil.relativedelta import relativedelta
from apps.pages.models import Income


def obtener_reporte_ingresos(periodo="semanal"):
    """
    Genera un reporte de ingresos agrupados por tipo de pago para diferentes períodos.
    """
    hoy = now().date()
    # Calcular el rango de fechas según el período seleccionado
    start_date, end_date = calcular_rango_fecha(periodo, hoy)

    # Query para obtener el reporte de ingresos
    reporte_query = (
        Income.objects.filter(date__range=[start_date, end_date])
        .values('was_paid')
        .annotate(total_amount=Sum('amount'))
        .order_by('was_paid')
    )

    # Convertir los resultados a una estructura más adecuada para tabla/CSV
    reporte = [
        {
            'Tipo de Pago': entry['was_paid'],
            'Total Ingresos': entry['total_amount']
        }
        for entry in reporte_query
    ]

   # Calcular el gran total
    gran_total = sum(entry['total_amount'] for entry in reporte_query)

    # Agregar el gran total al reporte
    reporte.append({
        'Tipo de Pago': 'Gran Total',
        'Total Ingresos': gran_total
    })

    return {
        'periodo': periodo,
        'rango': {'inicio': start_date, 'fin': end_date},
        'reporte': reporte
    }


def obtener_reporte_ingresos_por_dentista(periodo="semanal"):
    """
    Genera un reporte de ingresos totales por dentista para un período específico.
    """
    hoy = now().date()
    # Calcular el rango de fechas según el período seleccionado
    start_date, end_date = calcular_rango_fecha(periodo, hoy)

    # Query para obtener los ingresos por dentista
    reporte_query = (
        Income.objects.filter(date__range=[start_date, end_date])
        .values('dentist__id', 'dentist__first_name', 'dentist__last_name', 'dentist__percentage')
        .annotate(
            total_ingresos=Sum('amount'),
            total_honorarios=Sum(F('amount') * F('dentist__percentage'))
        )
        .order_by('dentist__last_name', 'dentist__first_name')
    )

    # Formatear los resultados para tablas/CSV
    reporte = [
        {
            'Dentista': f"{entry['dentist__first_name']} {entry['dentist__last_name']}",
            'Total Ingresos': entry['total_ingresos'],
            'Total Honorarios': entry['total_honorarios']
        }
        for entry in reporte_query
    ]

    return {
        'periodo': periodo,
        'rango': {'inicio': start_date, 'fin': end_date},
        'reporte': reporte
    }


def calcular_rango_fecha(periodo, hoy):
    """
    Calcula el rango de fechas basado en el periodo solicitado.
    """
    if periodo == "semanal":
        # Lunes de la semana actual
        start_date = hoy - timedelta(days=hoy.weekday())
        end_date = start_date + timedelta(days=6)  # Domingo
    elif periodo == "mensual":
        start_date = hoy.replace(day=1)  # Primer día del mes
        end_date = (start_date + relativedelta(months=1)) - \
            timedelta(days=1)  # Último día del mes
    elif periodo == "trimestral":
        start_month = ((hoy.month - 1) // 3) * 3 + \
            1  # Primer mes del trimestre
        # Primer día del trimestre
        start_date = hoy.replace(month=start_month, day=1)
        end_date = (start_date + relativedelta(months=3)) - \
            timedelta(days=1)  # Último día del trimestre
    elif periodo == "semestral":
        start_month = 1 if hoy.month <= 6 else 7  # Primer mes del semestre
        # Primer día del semestre
        start_date = hoy.replace(month=start_month, day=1)
        end_date = (start_date + relativedelta(months=6)) - \
            timedelta(days=1)  # Último día del semestre
    elif periodo == "anual":
        start_date = hoy.replace(month=1, day=1)  # Primer día del año
        end_date = hoy.replace(month=12, day=31)  # Último día del año
    else:
        raise ValueError(
            "Período no válido. Usa: 'semanal', 'mensual', 'trimestral', 'semestral', 'anual'.")

    return start_date, end_date


def exportar_a_csv(data, nombre_archivo):
    """
    Exporta el reporte a un archivo CSV.
    """
    if data:
        # Asumimos que todos los elementos tienen las mismas claves
        keys = data[0].keys()
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)


def generar_factura_pdf(nombre_archivo, empresa, rfc, direccion, telefono, reporte):
    """
    Genera un PDF tipo factura de gastos con información fiscal y un reporte en tabla.

    Args:
        nombre_archivo (str): Nombre del archivo PDF a generar.
        empresa (str): Nombre de la empresa.
        rfc (str): RFC de la empresa.
        direccion (str): Dirección fiscal de la empresa.
        telefono (str): Teléfono de la empresa.
        reporte (list[dict]): Lista de reportes en formato de diccionario.
    """
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Encabezado de la factura
    encabezado = f"""
    <b>{empresa}</b><br/>
    RFC: {rfc}<br/>
    Dirección: {direccion}<br/>
    Teléfono: {telefono}<br/>
    Fecha: {datetime.now().strftime('%d/%m/%Y')}<br/>
    """
    elements.append(Paragraph(encabezado, styles['Normal']))

    # Espacio
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Título del reporte
    elements.append(
        Paragraph("<b>Reporte de Ingresos</b>", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Crear tabla a partir del reporte
    # Encabezados de la tabla
    encabezados = ['Tipo de Pago', 'Total Ingresos']
    datos = [encabezados]

    # Agregar los datos del reporte a la tabla
    for fila in reporte:
        datos.append([fila['Tipo de Pago'], f"${fila['Total Ingresos']:,.2f}"])

    # Crear tabla
    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Agregar tabla al documento
    elements.append(tabla)

    # Construir el PDF
    doc.build(elements)


# Información de ejemplo
empresa = "Empresa Genérica S.A. de C.V."
rfc = "GENERIC123456XYZ"
direccion = "Calle Falsa 123, Ciudad, País"
telefono = "+52 55 1234 5678"

# Ejemplo de reporte
reporte = [
    {'Tipo de Pago': 'Efectivo', 'Total Ingresos': 1500},
    {'Tipo de Pago': 'Tarjeta', 'Total Ingresos': 2500},
    {'Tipo de Pago': 'Gran Total', 'Total Ingresos': 4000},
]

# Generar PDF
generar_factura_pdf("factura_reporte.pdf", empresa,
                    rfc, direccion, telefono, reporte)
