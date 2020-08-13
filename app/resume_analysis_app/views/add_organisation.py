import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import Organisation


@login_required
def add_organisation(request):
    if (request.method == "POST") and (org_id := request.POST.get('id')):
        # org_id passed through - editing an existing org
        try:
            org = Organisation.objects.get(id=org_id)
        except:
            messages.warning(request, 'Could not find org.')
            return redirect('profile')
        else:
            # Check credentials to edit
            if org.author != request.user:
                messages.warning(request, 'Invalid credentials.')
                return redirect('profile')
            # To update
            if request.POST.get('update'):
                org.title = request.POST.get('title')
                org.salary = request.POST.get('salary')
                org.location = request.POST.get('location')
                org.description_func = request.POST.get('description_func')
                org.description_non_func = request.POST.get('description_non_func')

                org.save()
                messages.success(request, 'Job updated.')
                return redirect('profile')
            # To delete
            elif request.POST.get('delete'):
                org.delete()
                messages.success(request, 'Job deleted.')
                return redirect('profile')
            # Neither update nor delete - just display the org
            else:
                return render(request, 'resume_analysis_app/add_job.html', {'org': org})
    # Method is POST but no org selected - submit org and redirect
    elif request.method == 'POST':
        title, salary, location = request.POST.get('title'), request.POST.get('salary'), request.POST.get('location')
        description_func = request.POST.get('description_func')
        description_non_func = request.POST.get('description_non_func')

        org = Organisation(title=title, salary=salary, location=location,
                             description_func=description_func, description_non_func=description_non_func,
                             categories=categories, concepts=concepts)
        org.save()

        return redirect('profile')
    # Just get the page with the form on
    else:
        return render(request, 'resume_analysis_app/add_organisation.html')
