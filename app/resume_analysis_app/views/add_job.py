import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import JobDescription


@login_required
def add_job(request):
    if (request.method == "POST") and (job_id := request.POST.get('id')):
        # job_id passed through - editing an existing job
        try:
            job = JobDescription.objects.get(id=job_id)
        except:
            messages.warning(request, 'Could not find job.')
            return redirect('profile')
        else:
            # Check credentials to edit
            if job.author != request.user:
                messages.warning(request, 'Invalid credentials.')
                return redirect('profile')
            # To update
            if request.POST.get('update'):
                job.title = request.POST.get('title')
                job.salary = request.POST.get('salary')
                job.location = request.POST.get('location')
                job.description_func = request.POST.get('description_func')
                job.description_non_func = request.POST.get('description_non_func')

                url = 'https://resume-node-red.mybluemix.net/CV'
                # Get keywords for functional and non-functional separately
                response = requests.post(url, data=request.POST.get('description_func').encode('utf-8')).json()
                keywords_func = {}
                for kw in response['keywords']:
                    keywords_func[kw['text']] = kw['count']
                job.keywords_func = json.dumps(keywords_func)

                response = requests.post(url, data=request.POST.get('description_non_func').encode('utf-8')).json()
                keywords_non_func = {}
                for kw in response['keywords']:
                    keywords_non_func[kw['text']] = kw['count']
                job.keywords_non_func = json.dumps(keywords_non_func)

                # Get rest of attributes by combining functional and non-functional
                full_job_descr = request.POST.get('description_func') + '\n' + request.POST.get('description_non_func')
                response = requests.post(url, data=full_job_descr.encode('utf-8')).json()
                job.concepts = json.dumps(response['concepts'])
                job.categories = json.dumps(response['categories'])

                job.save()
                messages.success(request, 'Job updated.')
                return redirect('profile')
            # To delete
            elif request.POST.get('delete'):
                job.delete()
                messages.success(request, 'Job deleted.')
                return redirect('profile')
            # Neither update nor delete - just display the job
            else:
                return render(request, 'resume_analysis_app/add_job.html', {'job': job})
    # Method is POST but no job selected - submit job and redirect
    elif request.method == 'POST':
        title, salary, location = request.POST.get('title'), request.POST.get('salary'), request.POST.get('location')
        description_func = request.POST.get('description_func')
        description_non_func = request.POST.get('description_non_func')

        url = 'https://resume-node-red.mybluemix.net/CV'
        # Get keywords for functional and non-functional separately
        response = requests.post(url, data=request.POST.get('description_func').encode('utf-8')).json()
        keywords_func = json.dumps(response['keywords'])
        response = requests.post(url, data=request.POST.get('description_non_func').encode('utf-8')).json()
        keywords_non_func = json.dumps(response['keywords'])

        # Get rest of attributes by combining functional and non-functional
        full_job_descr = description_func + '\n' + description_non_func
        response = requests.post(url, data=full_job_descr.encode('utf-8')).json()
        concepts = json.dumps(response['concepts'])
        categories = json.dumps(response['categories'])

        job = JobDescription(title=title, salary=salary, location=location,
                             description_func=description_func, description_non_func=description_non_func,
                             keywords_func=keywords_func, keywords_non_func=keywords_non_func,
                             categories=categories, concepts=concepts)
        job.save()

        return redirect('profile')
    # Just get the page with the form on
    else:
        return render(request, 'resume_analysis_app/add_job.html')
