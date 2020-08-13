from django.contrib import messages
from django.shortcuts import render, redirect

from ..models import Account, JobDescription


def job_view(request):

    if (request.method == "GET") and (job_id := request.GET.get('id')):
        try:
            job = JobDescription.objects.get(id=job_id)
        except:
            messages.warning(request, 'Could not find job details.')
            return redirect('home')
        # Apply to a job
        if request.GET.get('apply'):
            job.applicants.add(request.user)
            messages.success(request, 'Applied for position.')
        # Identified this job as user's current position
        if request.GET.get('position'):
            account = Account.objects.get(user=request.user)
            account.job = job
            account.save()
            messages.success(request, 'Your current position has been updated.')
            return redirect('profile')
    else:
        messages.warning(request, 'Error finding job details.')
        return redirect('home')

    return render(request, 'resume_analysis_app/view_job.html', {'job': job})
