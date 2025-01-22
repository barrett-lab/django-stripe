from django.urls import path, include
from . import views
from .views import ParticipantListView, ProgramListView,ProgramDetailView, ProgramUpdateView,ProgramCreateView

urlpatterns = [
    path('',views.home, name='staff-home'),
    path('participants/',views.participants, name='staff-participants'),
    path('participants/list/',ParticipantListView.as_view(), name='staff-participant-list'),
    path('participant/<int:participant_id>/', views.Participant_detail, name='participant-detail'),
   # path('participant/<int:participant_id>/medical', views.Participant_detail, name='participant-medical'),
    #programs
    path('programs/',ProgramListView.as_view(), name='staff-program-list'),
    path('program/<int:pk>', ProgramDetailView.as_view(), name='staff-program-detail'),
    path('program/<int:pk>/update/', ProgramUpdateView.as_view(), name='staff-program-update'),
    path('program/create/', ProgramCreateView.as_view(), name='staff-program-create'),
]
