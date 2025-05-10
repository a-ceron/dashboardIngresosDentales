from django.urls import path

from apps.charts import views

urlpatterns = [
    path("", views.index, name="charts"),
    path("income-data/", views.get_income_data, name='income-data'),
]
