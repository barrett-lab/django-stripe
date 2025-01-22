from django.urls import path, include
from . import views
from .views import PaymentView,ProcessPaymentView

urlpatterns = [

path('', PaymentView.as_view(), name='api-home'),
path('charge/',views.charge, name='api-charge'),
path('process_payment/', ProcessPaymentView.as_view(), name='process_payment'),
path('success/', ProcessPaymentView.as_view(), name='api-success'),
path('success/<str:args>/', views.successMsg, name='payment-success'),
]