"""
URL configuration for treck project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from . import web_views
from simulaciones.views import GenerarSimulacionAPIView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', web_views.register_view, name='register'),
    path('dashboard/', web_views.dashboard_view, name='dashboard'),
    path('simulaciones/', web_views.simulaciones_section_view, name='simulaciones_section'),
    path('capacitaciones/', web_views.capacitaciones_section_view, name='capacitaciones_section'),
    path('articulos/', web_views.articulo_list_view, name='articulos_list'),
    path('articulos/<int:articulo_id>/contexto/', web_views.articulo_contexto_view, name='articulo_contexto'),
    path('admin/', admin.site.urls),
    path('api/generar_simulacion/', GenerarSimulacionAPIView.as_view(), name='api_generar_simulacion'),
    path('api/simulaciones/', include('simulaciones.urls')),
    path('api/articulos/', include('articulos.urls')),
    path('api/capacitaciones/', include('capacitaciones.urls')),
]
