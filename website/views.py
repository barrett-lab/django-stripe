from django.conf import settings
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import ProgramSpace, Program, Participant, MedicalWaiver
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.db.models import OuterRef, Subquery, Max
from .forms import MedicalForm,RegistrationForm, ProgramSpaceForm

from .models import ProgramSpace, Reservation, ReservationProgramSpace, Participant,Company
#from .signals import space_selected

from django.contrib import messages
#from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def home(request):
     return render(request, 'website/index.html')

def about(request): #templates 
    return render(request, 'website/about.html')

def program(request): #templates 
    context = {
    
        'program':Program.objects.filter(id=3),
        
    }
    return render(request, 'website/program.html',context)

def contact(request): #templates 
    context = {
    
        'company':Company.objects.filter(id=1),
        
    }
    return render(request, 'website/contact.html',context)


class RegistrationView(View):
     def get(self, request):
          if 'participant_id' in request.session:
               # If participant ID exists in session, redirect to medical website
               return redirect('website-medical')
          else:
               form = RegistrationForm()
               registration = Participant.objects.all()
               return render(request, 'website/registration.html', context={'form': form, 'registration': registration})
     
     def post(self, request):
          form = RegistrationForm(request.POST)
          if form.is_valid():
               participant = form.save()
               request.session['participant_id'] = participant.id  # Save participant ID in session
               messages.success(request, f'Participant {participant.id} Added')
               return redirect('website-medical') 
          else:
               registration = Participant.objects.all()
               return render(request, 'website/registration.html', context={'form': form, 'registration': registration})
           
class MedicalView(View):
     
     def get(self, request):
        # Retrieve the participant ID from the session
        participant_id = request.session.get('participant_id')
        
        if 'medicalwaiver_id' in request.session:
            # Both IDs exist, redirect to select seats page
            return redirect('website-select-space')
        
        
        elif participant_id:
            participant = get_object_or_404(Participant, id=participant_id)

            # Check if a medical waiver already exists for the participant
            medical_waiver, created = MedicalWaiver.objects.get_or_create(participant=participant)

            # Create a form instance with the existing or new medical waiver
            form = MedicalForm(instance=medical_waiver)
            return render(request, 'website/medical.html', context={'form': form, 'participant': participant})
        else:
            # Handle the case when participant ID is not available in session
            return redirect('website-register')  # Redirect to registration form

     def post(self, request):
          participant_id = request.session.get('participant_id')
          if participant_id:
               participant = get_object_or_404(Participant, id=participant_id)

               # Check if a medical waiver already exists for the participant
               medical_waiver, created = MedicalWaiver.objects.get_or_create(participant=participant)
               
               form = MedicalForm(request.POST, instance=medical_waiver)
               if form.is_valid():
                    request.session['medicalwaiver_id'] = medical_waiver.id  # Save participant ID in session
                    print("Form is valid. Checking for concerning answers...")
                    
                    if form.has_concerning_answers():
                         form.save()
                         print("Concerning answers found. Redirecting to medical contact.")
                         return redirect('website-medical-contact')  # Redirect to  concerning answers page

                     
                    #!!!here i need to kill sessions,and provide, contact information
                    else:
                         form.save()
                         print("No concerning answers. Redirecting to select space.")
                         return redirect('website-select-space')  # Redirect to space selection page if no concerning answers
                    
               return render(request, 'website/medical.html', context={'form': form, 'participant': participant})
          
          else:
               print("No participant ID found in session.")
               return redirect('website-register')
          
class MedicalContactView(View):

    def get(self, request):
        # info to show
        participant_id = request.session.get('participant_id')
        if participant_id:
            medical_participant_id = participant_id
            
            # Clear session data related to the reservation process
            keys_to_clear = ['selected_space_ids', 'reservations', 'participant_id', 'selected_space_id', 'reservation_id', 'reservation_code', 'reservation_quantity', 'amount']
            for key in keys_to_clear:
                if key in request.session:
                    del request.session[key]

            context= {
                'medical_participant_id':medical_participant_id,
            }
        #!! also want to send and email
        
        return render(request, 'website/medical_contact.html',context)
 
class SelectView(View):
    def get(self, request):
        participant_id = request.session.get('participant_id')
        selected_space_ids = request.session.get('selected_space_ids')

        if participant_id:
            participant = get_object_or_404(Participant, id=participant_id)

            # Subquery to get the latest (max ID) available program space for each program
            latest_available_spaces = ProgramSpace.objects.filter(participant__isnull=True,
                program_id=OuterRef('program_id')) \
                .order_by('-id') \
                .values('id')[:1]

            # Fetch all program spaces with the latest available for each program
            available_spaces = ProgramSpace.objects.filter(id__in=Subquery(latest_available_spaces)) \
                                                    .select_related('program')\
                                                    .order_by('id')

            if selected_space_ids:
                # Redirect to create checkout session if selected_space_ids exist
                return redirect('create_checkout_session')
            else:
                return render(request, 'website/select_space.html', context={'available_spaces': available_spaces, 'participant': participant})
        else:
            return redirect('website-register')

    def post(self, request):
        participant_id = request.session.get('participant_id')
        
        if participant_id:
            participant = get_object_or_404(Participant, id=participant_id)
            selected_space_ids = request.POST.getlist('program_space_ids')
           
            
            for space_id in selected_space_ids:
                try:
                    selected_space = ProgramSpace.objects.get(id=space_id, participant__isnull=True)
                    selected_space.participant = participant
                    selected_space.save()
                    
            
                except ProgramSpace.DoesNotExist:
                    error_message = "One or more selected program spaces are no longer available."
                    latest_available_spaces = ProgramSpace.objects.filter(participant__isnull=True,
                        program_id=OuterRef('program_id')) \
                        .order_by('-id') \
                        .values('id')[:1]
                    available_spaces = ProgramSpace.objects.filter(id__in=Subquery(latest_available_spaces)) \
                                                             .select_related('program')
                    return render(request, 'website/select_space.html', context={'available_spaces': available_spaces, 'participant': participant, 'error_message': error_message})

            # Save selected space IDs,dates to the session
            request.session['selected_space_ids'] = selected_space_ids
            #request.session['selected_programs'] = selected_programs 
            
        
            
            # Retrieve the reservation associated with each selected space
            reservations = {}
            selected_spaces = {}
            
            for space_id in selected_space_ids:
                try:
                    reservation = Reservation.objects.get(program_space_id=space_id)
                    reservations[space_id] = {
                        'id': reservation.id,
                        'reservation_code': reservation.reservation_code,
                        'quantity': reservation.quantity,
                        #'program_date':reservation.program_space.program_date,
                        'amount': int(reservation.cost * 100)  # Convert cost to cents for Stripe
                    }
                    #create
                  
                     # Get the selected space and its program details
                    selected_space = ProgramSpace.objects.select_related('program').get(id=space_id)
                    selected_spaces[space_id] = {
                        'program_name': selected_space.program.name,
                        'program_requirements': selected_space.program.requirements,
                        'program_includes': selected_space.program.includes,
                       
                        'program_start_date': selected_space.program.start_date.isoformat(), 
                        # Convert Dates to string
                        'program_end_date': selected_space.program.end_date.isoformat(),
                        'program_days_of_operation': selected_space.program.days_of_operation,
                        'program_hours_of_operation': selected_space.program.hours_of_operation,
                        'program_cost': str(selected_space.program.cost), # Convert Decimal to string
                    }
                   
                        
                except Reservation.DoesNotExist:
                    pass  # Handle the case where no reservation is found for the space
                
             
            # i think reservation is JSON, i think selected programs has to be also?
            
            # Save reservation data to the session
            request.session['reservations'] = reservations
            #request.session['programs'] = programs
            request.session['selected_spaces'] = selected_spaces  
           # program_start = Program.objects.filter(programspace__in=selected_space_ids).order_by('start_date')
            
            messages.success(request, f'Selected Spaces: {", ".join(selected_space_ids)} Reserved')
           
            return redirect('create_checkout_session')  # Redirect to checkout or any other page after selecting spaces
        else:
            return redirect('website-register')

#class ReservationView(View):
