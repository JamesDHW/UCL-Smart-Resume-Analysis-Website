from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms import RegistrationForm

from ..models import JobDescription, Organisation


def home(request):
    jobs = JobDescription.objects.all().order_by('-id')[:10]
    return render(request, 'resume_analysis_app/home.html', {'jobs': jobs})


def search_results(request):
    if (request.method == "GET") and (search := request.GET.get('search')):
        try:
            jobs = JobDescription.objects.filter(title__icontains=search)
            if len(search) > 4:
                organisations = Organisation.objects.filter(name__icontains=search)
            else:   # If small search query only look for exact matches for organisations
                organisations = Organisation.objects.filter(name=search)
        except:
            messages.warning(request, 'Error')
            return redirect('home')
        else:
            context = {'search': search, 'jobs': jobs, 'organisations': organisations}
            return render(request, 'resume_analysis_app/search_results.html', context)


def login(request):
    return render(request, 'resume_analysis_app/login.html')


def logout(request):
    return render(request, 'resume_analysis_app/logout.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if (e := request.POST.get('email')) and (org := Organisation.objects.get(email_extension=e.split('@')[-1])):
                org.employees.add(new_user)  # Add to list of employees
            messages.success(request, 'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'resume_analysis_app/register.html', {'form': form})
