from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
import stripe
from website.models import Reservation, ProgramSpace,Company, Participant

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os 
import json

#environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

#page views
def create_checkout_session(request):
  try:
      
    # Retrieve relevant session information
    selected_space_ids = request.session.get('selected_space_ids', [])
    reservations = request.session.get('reservations', {})
    
    if reservations:
      
      selected_spaces = request.session.get('selected_spaces', {})
      # Generate line items for Stripe Checkout Session
      line_items = []
      
      for space_id in selected_space_ids:
          reservation_info = reservations.get(space_id)
          selected_spaces_info = selected_spaces.get(space_id)
          
          if reservation_info:
              line_item = {
                  'price_data': {
                      'currency': 'cad',
                      'product_data': {
                          'name': f' Week: {selected_spaces_info['program_start_date']} - {selected_spaces_info['program_end_date']}',
                          
                      },
                      'unit_amount': reservation_info['amount'],
                  },
                  'quantity': reservation_info['quantity'],
              }
              line_items.append(line_item)

      # Create Stripe Checkout Session with dynamic line items
      session = stripe.checkout.Session.create(
          payment_method_types=['card'],
          line_items=line_items,
          mode='payment',
          success_url=request.build_absolute_uri(reverse('success')),
          cancel_url=request.build_absolute_uri(reverse('cancel')),
          #error_url=request.build_absolute_uri(reverse('error')),
      )
   
    
    return redirect(session.url)
  
  except stripe.error.StripeError as e:
        # Redirect to the error page if an error occurs
        # Retrieve reservation data from session
    selected_space_ids = request.session.get('selected_space_ids', [])
    reservations = request.session.get('reservations', {})

    # Update reservations to mark them as paid
    for space_id in selected_space_ids:
        reservation_info = reservations.get(space_id)
        
        if reservation_info:
            try:
                #reservation = Reservation.objects.get(id=reservation_info['id'])
                #reservation.payment = True  # Mark reservation as paid
                #reservation.save()
                
                selected_space = ProgramSpace.objects.get(id=space_id)
                selected_space.participant = None
                selected_space.save()

                Reservation.objects.filter(program_space_id=space_id).delete()
                
                # Clear session data related to the reservation process
                keys_to_clear = ['selected_space_ids', 'reservations', 'selected_space_id' 'reservation_id', 'reservation_code', 'reservation_quantity', 'amount']
                for key in keys_to_clear:
                    if key in request.session:
                        del request.session[key]
            except ProgramSpace.DoesNotExist:
                pass  # Handle the case where the selected seat does not exist

        return redirect(reverse('website/select_space.html'))
 
def success(request):
    # Retrieve reservation data from session
    selected_space_ids = request.session.get('selected_space_ids', [])
    reservations = request.session.get('reservations', {})
    participant_id = request.session.get('participant_id')
    selected_spaces = request.session.get('selected_spaces', {})
    
    # Update reservations to mark them as paid
    for space_id in selected_space_ids:
        reservation_info = reservations.get(space_id)
        if reservation_info:
            try:
                reservation = Reservation.objects.get(id=reservation_info['id'])
                reservation.payment = True  # Mark reservation as paid
                reservation.save()
            except Reservation.DoesNotExist:
                # Log or handle the case where the reservation does not exist
                pass
            
    # Retrieve reservation information from the session
    reservation_list = []
    for space_id, reservation_info in reservations.items():
        try:
            reservation = Reservation.objects.get(id=reservation_info['id'])
            reservation_list.append(reservation)
        except Reservation.DoesNotExist:
            # Log or handle the case where the reservation does not exist
            pass

    # Retrieve participant information
    try:
        participant_info = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        # Log or handle the case where the participant does not exist
        participant_info = None
    
    # Retrieve company information
    company_info = Company.objects.filter(id=1).first()

  # Retrieve programspace information
    for space_id in selected_spaces:
            program_space_info = selected_spaces.get(space_id)
            if program_space_info:
        
                try:
                    programspace = ProgramSpace.objects.get(id=space_id)
                    
                except ProgramSpace.DoesNotExist:
                    # Log or handle the case where the program space does not exist
                    pass
    program_space_list = []
    for space_id, program_space_info in selected_spaces.items():
        try:
            programspace = ProgramSpace.objects.get(id=space_id)
            program_space_list.append(programspace)
            
        except ProgramSpace.DoesNotExist:
                # Log or handle the case where the program space does not exist
                pass
 

    # Clear session data related to the reservation process
    keys_to_clear = ['selected_space_ids', 'reservations', 'participant_id', 'amount']
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]
            
       # Render success page
    return render(request, 'payments/success.html',{
        'company': company_info,
        'reservations': reservation_list,
        'participant': participant_info,
        'selected_spaces': program_space_list,  # Include selected space ids in the context
    }
)

  





# Using Django
@csrf_exempt
def stripe_webhook(request):
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)

  # Handle the event
  if event.type == 'payment_intent.succeeded':
    payment_intent = event.data.object # contains a stripe.PaymentIntent
    print('PaymentIntent was successful!')
  elif event.type == 'payment_method.attached':
    payment_method = event.data.object # contains a stripe.PaymentMethod
    print('PaymentMethod was attached to a Customer!')
  # ... handle other event types

  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)

def error(request):
   # Retrieve reservation data from session
    selected_space_ids = request.session.get('selected_space_ids', [])
    reservations = request.session.get('reservations', {})

    # Update reservations to mark them as paid
    for space_id in selected_space_ids:
        reservation_info = reservations.get(space_id)
        
        if reservation_info:
            try:
                #reservation = Reservation.objects.get(id=reservation_info['id'])
                #reservation.payment = True  # Mark reservation as paid
                #reservation.save()
                
                selected_space = ProgramSpace.objects.get(id=space_id)
                selected_space.participant = None
                selected_space.save()

                Reservation.objects.filter(program_space_id=space_id).delete()
                
                # Clear session data related to the reservation process
                keys_to_clear = ['selected_space_ids', 'reservations', 'selected_space_id', 'reservation_id', 'reservation_code', 'reservation_quantity', 'amount']
                for key in keys_to_clear:
                    if key in request.session:
                        del request.session[key]
            except ProgramSpace.DoesNotExist:
                pass  # Handle the case where the selected seat does not exist

    
    return render(request, 'payments/error.html')


def cancel(request):
     # Retrieve reservation data from session
    selected_space_ids = request.session.get('selected_space_ids', [])
    reservations = request.session.get('reservations', {})

    # Update reservations to mark them as paid
    for space_id in selected_space_ids:
        reservation_info = reservations.get(space_id)
        
        if reservation_info:
            try:
                #reservation = Reservation.objects.get(id=reservation_info['id'])
                #reservation.payment = True  # Mark reservation as paid
                #reservation.save()
                
                selected_space = ProgramSpace.objects.get(id=space_id)
                selected_space.participant = None
                selected_space.save()

                Reservation.objects.filter(program_space_id=space_id).delete()
                
                # Clear session data related to the reservation process
                keys_to_clear = ['selected_space_ids', 'reservations', 'selected_space_id', 'reservation_id', 'reservation_code', 'reservation_quantity', 'amount']
                for key in keys_to_clear:
                    if key in request.session:
                        del request.session[key]
            except ProgramSpace.DoesNotExist:
                pass  # Handle the case where the selected seat does not exist
    return render(request, 'payments/cancel.html')
