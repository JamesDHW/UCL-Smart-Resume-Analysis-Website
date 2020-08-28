import datetime
from django.contrib import messages
from django.shortcuts import render, redirect

from ..models import Account, JobDescription
from .._app_functions import update_aggregate_personality


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
        if request.GET.get('position') and (since := request.GET.get('select_year')):
            account = Account.objects.get(user=request.user)
            account.job_start = since
            account.job = job
            account.save()
            update_aggregate_personality(job)
            messages.success(request, 'Your current position has been updated.')
            return redirect('profile')
    else:
        messages.warning(request, 'Error finding job details.')
        return redirect('home')

    context = {'job': job, 'years': [datetime.datetime.now().year-x for x in range(15)]}
    return render(request, 'resume_analysis_app/view_job.html', context)
