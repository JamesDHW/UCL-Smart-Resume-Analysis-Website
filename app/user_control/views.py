from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm


def login(request):
    context = {}
    return render(request, 'user_control/login.html', context)


def logout(request):
    context = {}
    return render(request, 'user_control/logout.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            messages.success(request, 'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'user_control/register.html', {'form': form})
