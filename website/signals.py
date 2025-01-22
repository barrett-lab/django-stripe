
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Program, ProgramSpace, Reservation, ReservationProgramSpace

from django.dispatch import Signal
#from .signals import space_selected

import random
import string

from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


#automatically create program spaces when program created

@receiver(post_save, sender=Program)
def create_program_spaces(sender, instance, created, **kwargs):
    if created:
        for _ in range(instance.capacity):
            ProgramSpace.objects.create(program=instance)
            
# Define a custom signal
#checkout_successful = Signal(providing_args=["request", "selected_space_ids"])

@receiver(post_save, sender=ProgramSpace)
#@receiver(checkout_successful)
def create_reservation(sender, instance, created, **kwargs):
    if not created and instance.participant_id is not None:
        # Check if participant ID is updated and is not empty
        Reservation.objects.create(program_space=instance, participant_id=instance.participant_id)
        

"""
# Store reservation ID in session
        request = kwargs.get('request')
        if request:
            request.session['reservation_id'] = reservation.id

@receiver(post_save, sender=ProgramSpace)
def create_reservation(sender, instance, created, **kwargs):
    if created and instance.participant is not None:
        # Create a reservation for each program space associated with the participant
        for program_space in ProgramSpace.objects.filter(participant=instance.participant):
            # Get or create a reservation for the participant
            Reservation.objects.create(participant=instance.participant,program_space=instance.program_space)

            
        ReservationProgramSpace.objects.create(reservation=reservation, program_space=instance)

@receiver(post_save, sender=Reservation)
def relationship(sender, instance, **kwargs):
    for program_space in instance.program_spaces.all():
        ReservationProgramSpace.objects.get_or_create(reservation=instance, program_space=program_space)


@receiver(post_save, sender=Reservation)
def relationship(sender, instance, **kwargs):
    for program_space in instance.program_spaces.all():
        ReservationProgramSpace.objects.get_or_create(reservation=instance, program_space=program_space)

@receiver(post_save, sender=Reservation)
def relationship(sender, instance, **kwargs):
    if hasattr(instance, 'program_spaces'):
        for program_space in instance.program_spaces.all():
            ReservationProgramSpace.objects.get_or_create(reservation=instance, program_space=program_space)
"""