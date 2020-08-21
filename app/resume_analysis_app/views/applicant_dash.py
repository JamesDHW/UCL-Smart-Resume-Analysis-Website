import json

import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import Account, JobDescription, QuestionResponse

from .._app_functions import update_applicants


@login_required
def applicant_dash(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.warning(request, 'No job selected.')
        return redirect('profile')

    try:
        job = JobDescription.objects.get(id=job_id)
        job.keywords = json.loads(job.keywords)
    except:
        messages.warning(request, 'Could not find job.')
        return redirect('profile')
    else:
        if job.author != request.user:
            messages.warning(request, 'Invalid credentials.')
            return redirect('profile')
        elif add := request.GET.get('add_kw'):
            job.keywords[add] = 3
            job.keywords = json.dumps(job.keywords)  # Dump before saving
            job.save()
            job.keywords = json.loads(job.keywords)  # Reload keywords
        elif rm := request.GET.get('remove_r'):
            job.recommended.remove(Account.objects.get(id=rm))
        elif rm := request.GET.get('remove_a'):
            job.applicants.remove(Account.objects.get(id=rm))
        elif rm := request.GET.get('remove_kw'):
            if rm in job.keywords.keys():
                del job.keywords[rm]
                job.keywords = json.dumps(job.keywords)  # Dump before saving
                job.save()
                job.keywords = json.loads(job.keywords)  # Reload keywords
        elif rm := request.GET.get('remove_con'):
            job.concepts = json.loads(job.concepts)
            if rm in job.concepts.keys():
                del job.concepts[rm]
                job.keywords = json.dumps(job.keywords)  # Dump before saving
                job.concepts = json.dumps(job.concepts)  # Dump before saving
                job.save()
                job.keywords = json.loads(job.keywords)  # Reload keywords
        elif request.GET.get('update'):
            update_applicants(job)

        # Defaults + List of number of matching keywords
        applicant, plt, app_matches, qstns, matching, tones = None, None, None, [], [], []
        job.concepts = json.loads(job.concepts).items()  # Reload concepts
        # Sort keywords
        job.keywords = {k: v for k, v in sorted(job.keywords.items(), key=lambda item: item[1], reverse=True)}
        job_keywords = ' '.join(job.keywords.keys()).lower()
        for usr in (all_applicants := job.applicants.all() | job.recommended.all()):
            # print(f'keywords:{usr.account.keywords} for {usr} of type {type(usr)}')
            matches = [kw for kw in json.loads(usr.account.keywords).keys() if kw.lower() in job_keywords.split(' ')]
            matching.append(len(matches))

            # Get info about the currently selected applicant
            if (uID := request.GET.get('user')) and str(usr.id) == uID:
                applicant = usr
                if (kws := applicant.account.keywords) != '':
                    applicant.account.keywords = [k for k, v in json.loads(kws).items() if v > 1]
                if (conc := applicant.account.concepts) != '':
                    applicant.account.concepts = json.loads(conc).items()
                applicant.account.education = json.loads(applicant.account.education)
                app_matches = matches  # Keywords which match with the job keywords

                # Plot big 5 personality types
                try:
                    pers_big5 = json.loads(applicant.account.pers_big5)
                    pers_openness = json.loads(applicant.account.pers_openness)
                    pers_conscien = json.loads(applicant.account.pers_conscien)
                    pers_agreeabl = json.loads(applicant.account.pers_agreeabl)
                    pers_extraver = json.loads(applicant.account.pers_extraver)
                    pers_em_range = json.loads(applicant.account.pers_em_range)
                    pers_needs = json.loads(applicant.account.needs)
                    pers_values = json.loads(applicant.account.values)

                    aggr_big5 = json.loads(job.aggr_big5)
                    aggr_openness = json.loads(job.aggr_openness)
                    aggr_conscien = json.loads(job.aggr_conscien)
                    aggr_agreeabl = json.loads(job.aggr_agreeabl)
                    aggr_extraver = json.loads(job.aggr_extraver)
                    aggr_em_range = json.loads(job.aggr_em_range)
                    aggr_needs = json.loads(job.needs)
                    aggr_values = json.loads(job.values)

                    qstns = QuestionResponse.objects.filter(user=usr).all()
                    for qstn in qstns:
                        tones.append([json.loads(qstn.language_tones)])
                except Exception as e:
                    print(e)
                else:
                    fig = go.Figure()
                    # Add dropdown
                    fig.update_layout(
                        updatemenus=[
                            dict(
                                buttons=[
                                    dict(
                                        args=[{'r': [[x for x in pers_big5.values()],
                                                     [x for x in aggr_big5.values()]],
                                               'theta': [[x for x in pers_big5.keys()],
                                                         [x for x in aggr_big5.keys()]]}],
                                        label="Big 5",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_openness.values()],
                                                     [x for x in aggr_openness.values()]],
                                               'theta': [[x for x in pers_openness.keys()],
                                                         [x for x in aggr_openness.keys()]]}],
                                        label="Openness",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_conscien.values()],
                                                     [x for x in aggr_conscien.values()]],
                                               'theta': [[x for x in pers_conscien.keys()],
                                                         [x for x in aggr_conscien.keys()]]}],
                                        label="Conscientiousness",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_agreeabl.values()],
                                                     [x for x in aggr_agreeabl.values()]],
                                               'theta': [[x for x in pers_agreeabl.keys()],
                                                         [x for x in aggr_agreeabl.keys()]]}],
                                        label="Agreeableness",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_extraver.values()],
                                                     [x for x in aggr_extraver.values()]],
                                               'theta': [[x for x in pers_extraver.keys()],
                                                         [x for x in aggr_extraver.keys()]]}],
                                        label="Extraversion",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_em_range.values()],
                                                     [x for x in aggr_em_range.values()]],
                                               'theta': [[x for x in pers_em_range.keys()],
                                                         [x for x in aggr_em_range.keys()]]}],
                                        label="Emotional Range",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_needs.values()],
                                                     [x for x in aggr_needs.values()]],
                                               'theta': [[x for x in pers_needs.keys()],
                                                         [x for x in aggr_needs.keys()]]}],
                                        label="Needs",
                                        method="update"
                                    ),
                                    dict(
                                        args=[{'r': [[x for x in pers_values.values()],
                                                     [x for x in aggr_values.values()]],
                                               'theta': [[x for x in pers_values.keys()],
                                                         [x for x in aggr_values.keys()]]}],
                                        label="Values",
                                        method="update"
                                    )],
                                direction="down",
                                pad={"r": 10, "t": 10},
                                showactive=True,
                                x=0,
                                xanchor="right",
                                y=1.1,
                                yanchor="top"
                            ),
                        ]
                    )

                    fig.add_trace(
                        go.Scatterpolar(r=[x * 100 for x in pers_big5.values()], theta=[x for x in pers_big5.keys()],
                                        fill='toself', name='Applicant'))
                    fig.add_trace(
                        go.Scatterpolar(r=[x * 100 for x in aggr_big5.values()], theta=[x for x in aggr_big5.keys()],
                                        fill='toself', name='Employees'))
                    plt = plot(fig, output_type='div')

        srtd_applicants = [x for _, x in sorted(zip(matching, all_applicants), key=lambda x: x[0], reverse=True)]
        context = {'job': job, 'applicants': srtd_applicants, 'applicant': applicant,
                   'matches': app_matches, 'fig': plt, 'questions': zip(qstns, tones)}
        return render(request, 'resume_analysis_app/applicant_dash.html', context)
