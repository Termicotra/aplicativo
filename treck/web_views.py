from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from articulos.models import Articulo
from simulaciones.models import Simulacion
from .forms import UserRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    simulaciones = (
        Simulacion.objects.filter(usuario=request.user)
        .select_related('articulo')
        .order_by('-fecha')[:20]
    )
    return render(request, 'dashboard.html', {'simulaciones': simulaciones})


@login_required
def articulo_list_view(request):
    articulos = Articulo.objects.order_by('-fecha')
    return render(request, 'articulos/list.html', {'articulos': articulos})
