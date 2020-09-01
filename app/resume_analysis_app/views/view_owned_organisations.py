from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Organisation


def owned_oragnisations(request):
    try:
        orgs = Organisation.objects.filter(owner=request.user)
    except:
        messages.warning(request, "Couldn't find your organisations.")
        return redirect('profile')

    return render(request, 'resume_analysis_app/view_owned_organisations.html', {'orgs': orgs})
