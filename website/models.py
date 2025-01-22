from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string

# Create your models here.
#from .models import MedicalWaiver
class Participant(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    SHIRT_SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
        
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    
    age = models.PositiveIntegerField(validators=[MinValueValidator(12), MaxValueValidator(21)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    grade = models.PositiveIntegerField(validators=[MinValueValidator(8), MaxValueValidator(12)])
    
   
    learning_style = models.CharField(max_length=100,blank=True, null=True)
    
    
    health_card = models.CharField(max_length=20)

    parent_guardian_name = models.CharField(max_length=100)
    parent_guardian_phone = models.CharField(max_length=15)
    
    emergency_contact_name = models.CharField(max_length=100)
    #emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=15)

    #medical_waiver = models.ForeignKey('MedicalWaiver', on_delete=models.CASCADE)

    shirt_size = models.CharField(max_length=3, choices=SHIRT_SIZE_CHOICES)
    registration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.first_name
    

class MedicalWaiver(models.Model):
    #participant  = models.ForeignKey('Participant', on_delete=models.CASCADE)
    participant = models.OneToOneField('Participant', on_delete=models.CASCADE)
    
    # ADLs
    ADL_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    bathroom = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    feeding = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    
    # Cognitive
    cognitive_comprehension = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    
    # Risk Assessment
    risk_harm_to_others = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    
    # Motor Skills
    motor_skills = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    
    # Allergies
    allergies_option = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    allergies_details = models.TextField(blank=True, null=True)
    
    # Diagnosis
    diagnosis_option = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    diagnosis_details = models.TextField(blank=True, null=True)
    
    # Medications
    medications_option = models.CharField(max_length=3, choices=ADL_CHOICES, default='no')
    medications_details = models.TextField(blank=True, null=True)
    
   
    communication = models.CharField(max_length=10, choices=ADL_CHOICES, default='no')
    communication_details = models.TextField(blank=True, null=True)
    
    
    behaviour = models.CharField(max_length=20, choices=ADL_CHOICES, default='no')
    behaviour_details = models.TextField(blank=True, null=True)
    
    #registration_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Waiver signed by {self.participant.first_name} {self.participant.last_name} "

class Program(models.Model):
    name = models.CharField(max_length=255, null=True)
    age = models.CharField(max_length=255, null=True)
    description = models.TextField()
    capacity = models.PositiveIntegerField(default=40)
    goals = models.TextField()
    requirements = models.TextField()
    includes = models.TextField()
    themes = models.TextField()
    activities = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_operation = models.TextField()
    hours_of_operation = models.TextField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    evaluation = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default="1")

    def __str__(self):
        return f"Program on {self.start_date}"
    
class ProgramSpace(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    participant = models.ForeignKey('Participant', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f" Program Date:{self.program.start_date},Space ID: {self.id}, Participant: {self.participant.first_name if self.participant else 'None'}"

    def save(self, *args, **kwargs):
        
        if self.participant is not None and self.pk is not None:
            
             # Check if the program space is already reserved
            if ProgramSpace.objects.filter(id=self.id, participant__isnull=False).exists():
                raise ValueError("This program space is already reserved.")
                #send to error page
            
            # Check if the participant has already chosen a program space for the same program ID
            if ProgramSpace.objects.filter(participant=self.participant, program_id=self.program_id).exists():
                raise ValueError("You already have a space selected.")
            
            # If all checks pass, create a reservation
            # Create a reservation

        super().save(*args, **kwargs)

class Reservation(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    program_space = models.ForeignKey(ProgramSpace, on_delete=models.CASCADE,default='100')
    reservation_date = models.DateTimeField(default=timezone.now)
    reservation_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2,blank=True, null=True)
    payment = models.BooleanField(default=False)
    
    def calculate_quantity_and_cost(self):
        # Calculate and save the quantity
        self.quantity = ProgramSpace.objects.filter(participant=self.participant, program=self.program_space.program).count()
        # Calculate and save the cost
        program = self.program_space.program
        self.cost = program.cost * self.quantity

    
    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure model validation is called on save
        if not self.reservation_code:
            self.reservation_code = self.generate_unique_reservation_code()
        self.calculate_quantity_and_cost()  # Calculate quantity and cost before saving
        super().save(*args, **kwargs)

    def clean(self):
        # Validate that the program_space belongs to the participant
        if self.program_space.participant != self.participant:
            raise ValidationError("Program space must belong to the same participant.")

    def generate_unique_reservation_code(self):
        while True:
            random_number = ''.join(random.choices(string.digits, k=7))
            new_code = f"001-CU-{random_number}"
            if not Reservation.objects.filter(reservation_code=new_code).exists():
                return new_code
        
    
    
    def __str__(self):
        return f"Reservation Cost: {self.cost},Reservation Code: {self.reservation_code},Participant: {self.participant.first_name},Reservation Quanity: {self.quantity}, Details: {self.program_space},Reservation ID: {self.id}"

# this is necessary!
class ReservationProgramSpace(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    program_space = models.ForeignKey(ProgramSpace, on_delete=models.CASCADE)

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    instagram = models.CharField(max_length=255,null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    founder = models.CharField(max_length=255)
    founder_title = models.CharField(max_length=255)
    founder_summary = models.TextField(null=True)
    founder_quote = models.TextField(null=True)

    mission = models.TextField(null=True)
    values = models.TextField(null=True)
    
    def __str__(self):
        return self.name