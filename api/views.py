from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect,get_object_or_404

from django.urls import reverse
import json
from django.http import JsonResponse
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from django.views.generic import View

from website.models import ProgramSpace, Reservation, Participant


class PaymentView(View):
    def get(self, request):
        participant_id = request.session.get('participant_id')
        selected_space_id = request.session.get('selected_space_id')
        reservation_id = request.session.get('reservation_id')
        
        if participant_id:
            participant = get_object_or_404(Participant, id=participant_id)
        
        return render(request, 'api/index.html', {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'participant_id': participant_id,
            'selected_space_id': selected_space_id,
            'reservation_id': reservation_id,
        })

    def post(self, request):
        data = json.loads(request.body)
        participant_id = data.get('participant_id')
        selected_space_id = data.get('selected_space_id')
        reservation_id = data.get('reservation_id')
        
        participant = get_object_or_404(Participant, id=participant_id)
        selected_space = get_object_or_404(ProgramSpace, id=selected_space_id, participant__isnull=True)
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        #amount = reservation.cost.price * 100  # Amount in cents
       
@method_decorator(csrf_exempt, name='dispatch')
class ProcessPaymentView(View):
    def post(self, request):
        #reservation_id = request.session.get('reservation_id')
        
        # Create a new Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Product Name',
                        },
                        'unit_amount': 5000,  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cancel')),
        )

        return redirect(session.url)

   
   
   
#doesnt return page, process payment
def charge(request):
     if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = request.POST['stripeToken']
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        reservation = get_object_or_404(Reservation, id=reservation_id)
        #amount = reservation.cost.price * 1000  # Amount in cents
        
        charge = stripe.Charge.create(
                amount=5000,
                currency='usd',
                source=token,
                description=reservation
            )
       

def successMsg(request, args):
     amount = args
     # can you add more than one argument if so can i add reservation id?
     return render(request, 'api/success.html',{'amount':amount})