from apps.pages.forms import IncomeForm
from django.shortcuts import render


def index(request):
    context = {
        'segment': 'dashboard',
        'form': IncomeForm(),
    }
    return render(request, "pages/index.html", context)

# Components


def color(request):
    context = {
        'segment': 'color'
    }
    return render(request, "pages/color.html", context)


def typography(request):
    context = {
        'segment': 'typography'
    }
    return render(request, "pages/typography.html", context)


def icon_feather(request):
    context = {
        'segment': 'feather_icon'
    }
    return render(request, "pages/icon-feather.html", context)


def sample_page(request):
    context = {
        'segment': 'sample_page',
    }
    return render(request, 'pages/sample-page.html', context)
