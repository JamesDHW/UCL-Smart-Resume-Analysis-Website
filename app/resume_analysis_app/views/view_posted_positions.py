from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import JobDescription


def posted_positions(request):
    try:
        jobs = JobDescription.objects.filter(author=request.user)
    except:
        messages.warning(request, "Couldn't find your posted positions")
        return redirect('profile')

    return render(request, 'resume_analysis_app/view_posted_positions.html', {'jobs': jobs})
