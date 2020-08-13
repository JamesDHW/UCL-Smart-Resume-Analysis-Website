import json

import requests
from django.contrib import messages
from django.shortcuts import render, redirect


from ..models import Account, JobDescription, Organisation


def organisation_view(request):

    if request.method == 'GET' and (org_id := request.GET.get('id')):
        try:
            organisation = Organisation.objects.get(id=org_id)
            if search := request.GET.get('search'):
                jobs = JobDescription.objects.filter(organisation=organisation, title__icontains=search)
            else:
                jobs = JobDescription.objects.filter(organisation=organisation)
        except:
            messages.warning(request, 'No organisation found.')
            return redirect('home')
        else:
            context = {'organisation': organisation, 'jobs': jobs}
            return render(request, 'resume_analysis_app/view_organisation.html', context)
    # POST request made to organisation page (or GET with no id)
    else:
        messages.warning(request, 'No organisation selected.')
        return redirect('home')
