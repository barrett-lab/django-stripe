from django import forms
from .models import MedicalWaiver, Participant,ProgramSpace
#from django.contrib.auth.models import User


# create a form
class MedicalForm(forms.ModelForm):
    #user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = MedicalWaiver
        exclude = ['participant',]
        labels = {
            'bathroom': 'Do you have any difficulty going to the bathroom on your own?',
            'feeding': 'Do you have any difficulty feeding yourself?',
            'cognitive_comprehension': 'Do you have any difficulty understanding instructions?',
            'risk_harm_to_others': 'Have you acted aggressively towards anyone in the past month?',
            'motor_skills': 'Do you require any physical assitance to complete activities?',
            'allergies_option': 'Do you have any allergies?',
            
            'diagnosis_option': 'Do you have any medical conditions?',
            'diagnosis_details': 'Please explain?',
            
            'medications_option': 'Do you take any medication(s)?',
            'medications_details': 'Please Explain?',
            
            'communication': 'Do you have any difficulty communicating?',
            'communication_details': 'Please Explain?',
            
            'behaviour': 'Have you had any difficulty controlling your behavour in the past month?',
            'behaviour_details': 'Please Explain?',
        }
    
    def has_concerning_answers(self):
        # Check if any of the answers are 'Yes' (assuming 'Yes' is stored as True)
        print("Cleaned Data:", self.cleaned_data)
        
        return any([
            self.cleaned_data.get('bathroom') == 'yes',
            self.cleaned_data.get('feeding') == 'yes',
            self.cleaned_data.get('cognitive_comprehension') == 'yes',
            self.cleaned_data.get('risk_harm_to_others') == 'yes',
            self.cleaned_data.get('motor_skills') == 'yes',
            self.cleaned_data.get('behaviour') == 'yes'
        ])
        
class RegistrationForm(forms.ModelForm):
    
    class Meta:
        model = Participant
        exclude = ['registration_date']
        
        # may have to get this info first. remove, medical and add it after i receive this info.
       
class ProgramSpaceForm(forms.ModelForm):
    
    class Meta:
        model = ProgramSpace
        exclude = ['participant']
        
 