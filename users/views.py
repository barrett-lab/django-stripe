from django.shortcuts import render, redirect

from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from .models import File

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        #add post data to form
        if form.is_valid():
            form.save()
            #adds form data to database
            
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()        
        #create blank form
    return render(request, 'users/register.html', {'form': form}) 

def custom_logout(request):
    logout(request)
    # You can add custom logic here if needed
    return render(request, 'users/logout.html')

@login_required # decorator
def profile(request):
    if request.method == 'POST':
        #add forms
        u_form = UserUpdateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        # add info filled into form instace=request.class
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f' Your Account was updated')
            return render(request, 'staff/index.html')
            # redirect causes browser to send get request
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
     
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'users/profile.html', context)


# files
@login_required
def accessible_folders(request):
    return render(request, 'users/accessible_folders.html')

@login_required
def shared_files(request):
    shared_files = File.objects.filter(user=None)  # Assuming shared files have no associated user
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = None  # Ensure shared files have no user associated
            file_instance.save()
            return redirect('shared_files')
    else:
        form = FileUploadForm()
    return render(request, 'users/shared_files.html', {'shared_files': shared_files, 'form': form})

@login_required
def user_files(request):
    user_files = File.objects.filter(user=request.user)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.save()
            return redirect('user_files')
    else:
        form = FileUploadForm()
    return render(request, 'users/user_files.html', {'user_files': user_files, 'form': form})