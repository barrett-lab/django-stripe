from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView,UpdateView, CreateView
from website.models import Participant, MedicalWaiver, Reservation, Program
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from website.models import ProgramSpace, Reservation,Participant,Company,Program
from datetime import datetime

# Create your views here.
@login_required
def home(request):
    # Get the current date
    current_date = datetime.now()

    # Format the date as "day of the week, month day, year"
    formatted_date = current_date.strftime("%A, %B %d, %Y")
    context = {
    
        'company':Company.objects.filter(id=1),
        'programs':Program.objects.all(),
        'reservations':Reservation.objects.all(),
        'participants':Participant.objects.all(),   
        'date':formatted_date,
    }
    return render(request, 'staff/index.html', context)

@login_required
def participants(request):
     return render(request, 'staff/participants.html')

class ParticipantListView(LoginRequiredMixin,ListView):
    model = Participant
    template_name = 'staff/participant_list.html'
    context_object_name = 'participants'
    ordering = ['registration_date'] 
    
@login_required    
def Participant_detail(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    medical_waiver = get_object_or_404(MedicalWaiver, participant=participant)
    reservations = Reservation.objects.filter(participant=participant)
    available_spaces = 100
    
    context = {
        'participant': participant,
        'medical_waiver': medical_waiver,
        'reservations': reservations,
        'available_spaces': available_spaces,
    }
    
    return render(request, 'staff/participant_detail.html', context)

# Programs

class ProgramListView(LoginRequiredMixin,ListView):
    model = Program
    template_name = 'staff/program_list.html'
    context_object_name = 'programs'
    #ordering = ['registration_date'] 
    
class ProgramDetailView(LoginRequiredMixin,DetailView):
    model = Program
    template_name = 'staff/program_detail.html'
    
class ProgramCreateView(LoginRequiredMixin, CreateView):
    model = Program
    template_name = 'staff/program_form.html'
    fields = ['name','age','description', 'capacity','goals','requirements','includes', 'themes','activities','start_date','end_date', 'days_of_operation','hours_of_operation','cost','evaluation',]
    # add a form to create an order
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)  
    
class ProgramUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Program
    template_name = 'staff/program_form.html'
    fields = ['name','age','description', 'capacity','goals','requirements','includes', 'themes','activities','start_date','end_date', 'days_of_operation','hours_of_operation','cost','evaluation',]
    # add a form to create an order
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)  

    def test_func(self):
        program = self.get_object()
        if self.request.user == program.author:
            return True
        return False