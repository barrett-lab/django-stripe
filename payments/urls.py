from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('error/', views.error, name='error'),
    path('cancel/', views.cancel, name='cancel'),
    
    #stripe webhook
    #path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
]