from django.urls import path
from . import views

urlpatterns = [
    path("", views.recherche_prots, name="recherche_prots"),
]
