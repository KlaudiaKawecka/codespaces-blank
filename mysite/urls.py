from django.contrib import admin
from django.urls import path, include  # <--- WAŻNE: dodano 'include'
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ta linijka włącza gotowe widoki logowania i wylogowania (to naprawi błąd):
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', views.home, name='home'),
    path('lek/<int:id>/', views.drug_detail, name='drug_detail'),
    path('producent/<int:id>/', views.manufacturer_detail, name='manufacturer_detail'),
]