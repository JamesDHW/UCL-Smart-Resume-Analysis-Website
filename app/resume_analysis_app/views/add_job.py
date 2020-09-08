import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import JobDescription
from .._app_functions import extract_insights, update_applicants


@login_required
def add_job(request):
    if request.method == "POST" and request.user.is_authenticated:
        if job_id := request.POST.get('id'):
            try:
                job = JobDescription.objects.get(id=job_id)
            except:
                messages.warning(request, 'Could not find job.')
                return redirect('profile')
            else:
                # Check credentials to edit
                if job.author != request.user or request.user.account.organisation == None:
                    messages.warning(request, 'Invalid credentials.')
                    return redirect('profile')
                # If credentials pass and we want to delete
                elif request.POST.get('delete'):
                    job.delete()
                    messages.success(request, 'Job deleted.')
                    return redirect('profile')
                # Neither update nor delete - just display the job
                elif not request.POST.get('update'):
                    return render(request, 'resume_analysis_app/add_job.html', {'job': job})
        # No job_id provided give a blank job description
        else:
            job = JobDescription()

        # Now POST request is to save or update a job
        job.author = request.user
        job.organisation = request.user.account.organisation
        job.title = request.POST.get('title')
        job.salary = request.POST.get('salary')
        job.location = request.POST.get('location')
        job.description_func = request.POST.get('description_func')
        job.description_non_func = request.POST.get('description_non_func')

        # Use my function to extract insights
        job_desc = request.POST.get('description_func') + '\n' + request.POST.get('description_non_func')
        extracted_kws, extracted_cats, extracted_concepts = extract_insights(job_desc)

        job.keywords = json.dumps(extracted_kws)
        job.concepts = json.dumps(extracted_concepts)
        for i, cat in enumerate(extracted_cats):
            if i == 0: job.category1 = cat
            if i == 1: job.category2 = cat
            if i == 2: job.category3 = cat

        job.save()

        job.keywords = json.loads(job.keywords)
        update_applicants(job)

        messages.success(request, 'Job updated.')
        return redirect('profile')
    elif not request.user.is_authenticated:
        return redirect('home')
    # Just get the page with the form on
    else:
        return render(request, 'resume_analysis_app/add_job.html')
