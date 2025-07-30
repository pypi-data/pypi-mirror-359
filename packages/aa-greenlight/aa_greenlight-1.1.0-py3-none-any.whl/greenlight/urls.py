"""App URLs"""

# Django
from django.urls import path

# AA greenlight App
from greenlight import views

app_name: str = "greenlight"

urlpatterns = [
    path("", views.status_view, name="status"),
    path("fc/", views.fc_panel, name="fc_panel"),
]
