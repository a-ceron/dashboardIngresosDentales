from django.forms import ModelForm
from apps.pages.models import Income


class IncomeForm(ModelForm):
    class Meta:
        model = Income
        fields = '__all__'
