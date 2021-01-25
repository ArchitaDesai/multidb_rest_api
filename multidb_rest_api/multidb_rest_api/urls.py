from django.urls import path

from core.views import CoreView

urlpatterns = [
    path('api/', CoreView.as_view())
]
