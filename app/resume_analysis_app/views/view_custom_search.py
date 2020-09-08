import json
from django.contrib import messages
from django.shortcuts import render, redirect

from ..models import Account, JobDescription

from .._app_functions import custom_search


def view_custom_search(request):

    if job_id := request.GET.get('job'):
        try:
            job = JobDescription.objects.get(id=job_id)
            job.keywords = json.loads(job.keywords)
        except:
            messages.warning(request, 'Position not found.')
            return redirect('profile')
        else:
            if add := request.GET.get('add'):
                try:
                    job.applicants.add(Account.objects.get(id=add).user)
                    job.keywords = json.dumps(job.keywords)
                    job.save()
                    job.keywords = json.loads(job.keywords)
                except: messages.warning(request, 'Could not add user to shortlist.')

            cat = request.GET.getlist('categories')
            for i, ele in enumerate(cat):
                cat[i] = '/'+'/'.join(ele.split(' -> '))
            cat = [x for x in cat if x not in ['/Category 1', '/Category 2', '/Category 3']]

            if kws := request.GET.get('keywords'):
                kws = kws.split(',')
                kws = [x if x[0] != " " else x[1:] for x in kws]
            else: kws = []

            candidates = custom_search(cat, kws, job=job)

            # load all available categories
            with open('./resume_analysis_app/categories.txt') as file:
                lines = file.readline()
                categories = json.loads(lines)

            # add in categories from get request
            cats, default = request.GET.getlist('categories'), ['Category 1', 'Category 2', 'Category 3']
            cats = [cats[x] if len(cats)>x else default[x] for x in range(3)]

            # get candidates
            matching = []
            job_keywords = ' '.join(job.keywords.keys()).lower().split(' ')    # Variable for ease of checking
            for usr in (all_applicants := set(job.applicants.all() | job.recommended.all())):
                all_applicants = [x for x in all_applicants if x not in job.removed.all()]
                matches = [kw for kw in json.loads(usr.account.keywords).keys() if kw.lower() in job_keywords]
                matching.append(len(matches))

            srtd_applicants = [x for _, x in sorted(zip(matching, all_applicants), key=lambda x: x[0])]
            context = {'categories': categories, 'job': job, 'candidates': candidates,
                       'cats': cats, 'kws': request.GET.get('keywords'), 'applicants': srtd_applicants}
            return render(request, 'resume_analysis_app/search_custom.html', context)
    else:
        messages.warning(request, 'No position selected.')
        return redirect('profile')
