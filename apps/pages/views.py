from apps.pages.forms import IncomeForm
from django.shortcuts import render
from datetime import date

from apps.pages.models import Dentist, Income  # Ajusta el import a tu estructura
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone


def get_days_until_birthday(birthday):
    if birthday:
        today = date.today()
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days
    return None


def get_meta_incomes():
    incomes = Income.objects.all()

    # Suma de ingresos de esta semana
    weekly_income = incomes.filter(
        date__gte=timezone.now() - timedelta(days=7)
    ).aggregate(total=Sum('amount'))['total'] or 0
    weekly_transactions = incomes.filter(
        date__gte=timezone.now() - timedelta(days=7)
    ).count()
    weekly_average = weekly_income / \
        weekly_transactions if weekly_transactions > 0 else 0

    # Suma de ingresos de este mes
    monthly_income = incomes.filter(
        date__gte=timezone.now() - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    monthly_transactions = incomes.filter(
        date__gte=timezone.now() - timedelta(days=30)
    ).count()
    monthly_average = monthly_income / \
        monthly_transactions if monthly_transactions > 0 else 0

    # Suma de ingresos de este año
    yearly_income = incomes.filter(
        date__gte=timezone.now() - timedelta(days=365)
    ).aggregate(total=Sum('amount'))['total'] or 0
    yearly_transactions = incomes.filter(
        date__gte=timezone.now() - timedelta(days=365)
    ).count()
    yearly_average = yearly_income / \
        yearly_transactions if yearly_transactions > 0 else 0

    # Cálculo de proporciones
    weekly_ratio = (weekly_income / monthly_income *
                    100) if monthly_income > 0 else 0
    monthly_ratio = (monthly_income / yearly_income *
                     100) if yearly_income > 0 else 0
    # Proporción anual (por ejemplo, si la meta es 1 millón)
    yearly_ratio = (yearly_income / 1000000 * 100)

    return {
        'weekly_income': weekly_income,
        'monthly_income': monthly_income,
        'yearly_income': yearly_income,
        'weekly_transactions': weekly_transactions,
        'monthly_transactions': monthly_transactions,
        'yearly_transactions': yearly_transactions,
        'weekly_average': weekly_average,
        'monthly_average': monthly_average,
        'yearly_average': yearly_average,
        'weekly_ratio': weekly_ratio,
        'monthly_ratio': monthly_ratio,
        'yearly_ratio': yearly_ratio,
    }


def index(request):
    active_dentists = Dentist.objects.filter(is_active=True)
    dentists_data = [
        {
            "name": f"{dentist.first_name} {dentist.last_name}",
            "level": dentist.level,
            "birthday": dentist.birdth,
            "days_until_birthday": get_days_until_birthday(dentist.birdth),
            "avatar": "assets/images/user/avatar-1.jpg",  # Cambiar según la lógica de tu app
        }
        for dentist in active_dentists
    ]

    context = {
        'segment': 'dashboard',
        'form': IncomeForm(),
        'dentists': dentists_data,
        'incomes': get_meta_incomes()
    }
    return render(request, "pages/index.html", context)


def perfil(request):
    context = {
        'segment': 'perfil',
    }
    return render(request, "pages/perfil.html", context)


# Ganancias Semanales
def obtener_ganancias_semanales():
    hoy = timezone.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    fin_semana = inicio_semana + timedelta(days=6)  # Domingo de esta semana

    ingresos_semanales = Income.objects.filter(
        date__range=[inicio_semana.date(), fin_semana.date()]
    ).aggregate(total=Sum('amount'))

    return ingresos_semanales['total'] or 0

# Ganancias Mensuales


def obtener_ganancias_mensuales():
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1)
    fin_mes = (inicio_mes.replace(month=hoy.month + 1) - timedelta(days=1)
               ) if hoy.month != 12 else (inicio_mes.replace(year=hoy.year + 1, month=1) - timedelta(days=1))

    ingresos_mensuales = Income.objects.filter(
        date__range=[inicio_mes.date(), fin_mes.date()]
    ).aggregate(total=Sum('amount'))

    return ingresos_mensuales['total'] or 0

# Número de Procedimientos por Día


def obtener_procedimientos_por_dia():
    hoy = timezone.now().date()
    procedimientos_dia = Income.objects.filter(date=hoy).count()
    return procedimientos_dia


def dashboard_view(request):
    ganancias_semanales = obtener_ganancias_semanales()
    ganancias_mensuales = obtener_ganancias_mensuales()
    procedimientos_dia = obtener_procedimientos_por_dia()

    return render(request, 'dashboard.html', {
        'ganancias_semanales': ganancias_semanales,
        'ganancias_mensuales': ganancias_mensuales,
        'procedimientos_dia': procedimientos_dia
    })
