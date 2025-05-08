import csv
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
from dateutil.relativedelta import relativedelta
from apps.incomes.models import Income


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
