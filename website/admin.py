from django.contrib import admin
from .models import Program,ProgramSpace, Participant, MedicalWaiver,Reservation,Company
# Register your models here.
admin.site.register(Program)
admin.site.register(ProgramSpace)
admin.site.register(Participant)
admin.site.register(MedicalWaiver)
admin.site.register(Reservation)
#admin.site.register(ReservationProgramSpace)
admin.site.register(Company)
