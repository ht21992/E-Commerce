from django.urls import path

from .views import start_order,success,failed

urlpatterns = [
    path('start_order/', start_order, name='start_order'),
    path("success/", success, name="success"),
    path("failed/", failed, name="failed"),
]