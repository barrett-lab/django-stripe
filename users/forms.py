"""
add additional input fields to a form

**IMPORTANT**
so when i was looking at github code snippets i noticed UserRegisterForm in place of UserCreationForm. Thats because when we first added the form to our views.py we had classname UserCreationForm, and when now when we are adding new input fields, 
**we are changing  UserCreationForm -> UserRegisterForm ; replaceall in  views.py** 
**IMPORTANT**

"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, File

# this is where we create forms
class UserRegisterForm(UserCreationForm):
    #name = forms.CharField()
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
    #class Meta - saing going to affect pre contructed structure
    
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']