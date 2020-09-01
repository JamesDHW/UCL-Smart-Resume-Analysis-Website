import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import Organisation


@login_required
def add_organisation(request):
    if request.method == "POST":
        if org_id := request.POST.get('id'):
            try:
                org = Organisation.objects.get(id=org_id)
            except:
                messages.warning(request, 'Could not find org.')
                return redirect('profile')
            else:
                # Check credentials to edit
                if org.owner != request.user:
                    messages.warning(request, 'Invalid credentials.')
                    return redirect('profile')
                # If credentials pass and we want to delete
                elif request.POST.get('delete'):
                    org.delete()
                    messages.success(request, 'Job deleted.')
                    return redirect('profile')
                # Neither update nor delete - just display the org
                elif not request.POST.get('update'):
                    return render(request, 'resume_analysis_app/add_organisation.html', {'org': org})
                messages.success(request, 'Organisation updated.')
        # No org_id provided give a blank org description
        else:
            org = Organisation()
            org.owner = request.user
            messages.success(request, 'Organisation created.')

        # Now POST request is to save or update a org
        org.name = request.POST.get('name')
        org.email_extension = request.POST.get('email')
        org.company_description = request.POST.get('description')

        org.save()
        return redirect('profile')
    # Just get the page with the form on
    else:
        context = {}
        if org_id := request.GET.get('id'):
            try:
                org = Organisation.objects.get(id=org_id)
                if org.owner == request.user:
                    context = {'organisation': org}
            except:
                pass
        return render(request, 'resume_analysis_app/add_organisation.html', context)
