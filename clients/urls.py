from django.urls import path
from . import views

urlpatterns = [
    # Route pour démarrer automatiquement le socket client
    path('', views.start_client_view, name='start_client'),
]
