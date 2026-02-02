from django.contrib import admin
from django.urls import path, include  # Dodano include
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    # To dodaje gotowe ścieżki: /login/ i /logout/
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
]
