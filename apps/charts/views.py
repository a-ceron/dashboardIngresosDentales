from django.shortcuts import render
from django.core import serializers
from apps.pages.models import Income
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
# Create your views here.


def index(request):
    Incomes = serializers.serialize('json', Income.objects.all())
    context = {
        'segment': 'charts',
        'products': Incomes
    }
    return render(request, 'charts/index.html', context)


def get_income_data(request):
    daily_totals = Income.objects.values('date').annotate(total=Sum('amount'))
    procedure_counts = Income.objects.values(
        'procedure__name').annotate(count=Count('id'))
    monthly_totals = Income.objects.annotate(month=TruncMonth(
        'date')).values('month').annotate(total=Sum('amount'))
    monthly_by_type = Income.objects.values(
        'was_paid').annotate(total=Sum('amount'))
    dentist_by_type = Income.objects.values(
        'dentist__first_name', 'was_paid').annotate(total=Sum('amount'))

    data = {
        "daily_totals": list(daily_totals),
        "procedure_counts": list(procedure_counts),
        "monthly_totals": list(monthly_totals),
        "monthly_by_type": list(monthly_by_type),
        "dentist_by_type": list(dentist_by_type),
    }

    return JsonResponse(data)
