import json

import plotly.graph_objects as go
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from plotly.offline import plot

from ..models import JobDescription


@login_required
def applicant_dash(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.warning(request, 'No job selected.')
        return redirect('profile')

    try:
        job = JobDescription.objects.get(id=job_id)
        job.keywords_func = json.loads(job.keywords_func)
        job.keywords_non_func = json.loads(job.keywords_non_func)
        job.categories = json.loads(job.categories)
        job.concepts = json.loads(job.concepts)
    except:
        messages.warning(request, 'Could not find job.')
        return redirect('profile')
    else:
        applicant, plt, app_matches, matching = None, None, None, []    # Defaults + List of number of matching keywords
        job_keywords = ' '.join(job.keywords_func.keys()).lower()
        for usr in job.applicants.all():
            matches = [kw for kw in json.loads(usr.applicant.keywords).keys() if kw.lower() in job_keywords.split(' ')]
            matching.append(len(matches))

            # Get the currently selected applicant
            if request.GET.get('user') and str(usr.id) == request.GET.get('user'):
                applicant = usr
                applicant.applicant.keywords = json.loads(applicant.applicant.keywords).keys()
                app_matches = matches  # Keywords which match with the job keywords
                # Plot big 5 personality types
                try:
                    raw = json.loads(applicant.applicant.personality)['personality']
                except:
                    pass
                else:
                    labels = [x['name'] for x in raw]
                    data = [x['percentile']*100 for x in raw]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(y=data, x=labels))
                    fig.update_layout(title='Big 5 Personality Breakdown', yaxis=dict(title_text="Percentile"))
                    plt = plot(fig, output_type='div')

        sorted_applicants = [x for _, x in sorted(zip(matching, job.applicants.all()), key=lambda pair: pair[0], reverse=True)]
        context = {'job': job, 'applicants': sorted_applicants, 'applicant': applicant, 'matches': app_matches, 'fig': plt}
        return render(request, 'resume_analysis_app/applicant_dash.html', context)
