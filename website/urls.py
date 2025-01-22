from django.urls import path, include
from . import views

from .views import RegistrationView,MedicalView,MedicalContactView,SelectView

urlpatterns = [
    path('',views.home, name='website-home'),
    path('about/',views.about, name='website-about'),
    path('program/',views.program, name='website-program'),
    path('contact/',views.contact, name='website-contact'),
    
    #registration - class based view
    path('register/', RegistrationView.as_view(), name='website-register'),
    path('register/medical', MedicalView.as_view(), name='website-medical'),
    path('register/medical/contact', MedicalContactView.as_view(), name='website-medical-contact'),
    path('register/select', SelectView.as_view(), name='website-select-space'),
    
    #payment
    #path('register/payment', PaymentView.as_view(), name='website-payment'),
    #path('process_payment/', ProcessPaymentView.as_view(), name='process_payment'),
    
    #reservation
    #path('reservation/<int:program_space_id>/', views.select_program_space, name='select_program_space'),
]
