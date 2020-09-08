import json

import plotly.graph_objects as go
from plotly.offline import plot

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from ..models import Account, JobDescription, QuestionResponse

from .._app_functions import update_applicants


@login_required
def applicant_dash(request):
    def save_job(jb):
        jb.keywords = json.dumps(job.keywords)
        jb.keywords_req = json.dumps(job.keywords_req)
        jb.concepts = json.dumps(job.concepts)
        jb.save()
        jb.keywords = json.loads(job.keywords)
        jb.keywords_req = json.loads(job.keywords_req)
        jb.concepts = json.loads(job.concepts)

    def plot_personality(app):
        # Plot big 5 personality types
        try:
            pers_big5 = json.loads(app.account.pers_big5)
            pers_openness = json.loads(app.account.pers_openness)
            pers_conscien = json.loads(app.account.pers_conscien)
            pers_agreeabl = json.loads(app.account.pers_agreeabl)
            pers_extraver = json.loads(app.account.pers_extraver)
            pers_em_range = json.loads(app.account.pers_em_range)
            pers_needs = json.loads(app.account.needs)
            pers_values = json.loads(app.account.values)

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
            print('exception:', e)
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
            return plot(fig, output_type='div')

    # Check that a job id is given
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.warning(request, 'No job selected.')
        return redirect('profile')

    try:
        job = JobDescription.objects.get(id=job_id)
        job.keywords = json.loads(job.keywords)
        job.keywords_req = json.loads(job.keywords_req)
        job.concepts = json.loads(job.concepts)
    except:
        messages.warning(request, 'Could not find job.')
        return redirect('profile')
    else:
        if job.author != request.user:
            messages.warning(request, 'Invalid credentials.')
            return redirect('profile')
        elif add := request.GET.get('add_kw'):
            add = add.split(',')
            add = [x if x[0] != " " else x[1:] for x in add]
            for kw in add:
                job.keywords[kw] = 3
            save_job(job)
        elif request.GET.get('req_kws'):   # Remove applicant from list
            rq = request.GET.getlist('check')
            for kw in rq:
                job.keywords_req.append(kw)
            save_job(job)
        elif rm := request.GET.get('remove_app'):   # Remove applicant from list
            job.removed.add(User.objects.get(id=rm))
            save_job(job)
        elif request.GET.get('remove_kws'):    # Remove a keyword
            rm = request.GET.getlist('check')
            for kw in rm:
                if kw in job.keywords.keys():
                    del job.keywords[kw]
                if kw in job.keywords_req:
                    del job.keywords_req[job.keywords_req.index(kw)]
            save_job(job)
        elif rm := request.GET.get('remove_req_kw'):    # Remove a required keyword
            if rm in job.keywords_req:
                del job.keywords_req[job.keywords_req.index(rm)]
            save_job(job)
        elif rm := request.GET.get('remove_con'):   # Remove concept
            if rm in job.concepts.keys():
                del job.concepts[rm]
                save_job(job)
        elif request.GET.get('update'):
            update_applicants(job)

        # Defaults + List of number of matching keywords
        applicant, plt, app_matches, qstns, matching, tones = None, None, None, [], [], []
        job.concepts = job.concepts.items()  # Reload concepts
        # Sort keywords for most relevant displayed first
        job.keywords = {k: v for k, v in sorted(job.keywords.items(), key=lambda item: item[1], reverse=True)}
        job_keywords = ' '.join(job.keywords.keys()).lower().split(' ')    # Variable for ease of checking

        if app_id := request.GET.get('search'):
            try:
                applicant = Account.objects.get(id=app_id).user
            except: messages.warning(request, 'Could not load profile.')
            else:
                if (kws := applicant.account.keywords) != '{}':
                    applicant.account.keywords = [k for k, v in json.loads(kws).items() if v > 1]
                if (conc := applicant.account.concepts) != '{}':
                    applicant.account.concepts = json.loads(conc).items()
                applicant.account.education = json.loads(applicant.account.education)
                app_matches = [kw for kw in applicant.account.keywords if kw.lower() in job_keywords]

        for usr in (all_applicants := set(job.applicants.all() | job.recommended.all())):
            all_applicants = [x for x in all_applicants if x not in job.removed.all()]
            matches = [kw for kw in json.loads(usr.account.keywords).keys() if kw.lower() in job_keywords]
            matching.append(len(matches))

            # Get info about the currently selected applicant
            if (uID := request.GET.get('user')) and str(usr.id) == uID:
                applicant = usr
                if (kws := applicant.account.keywords) != '{}':
                    applicant.account.keywords = [k for k, v in json.loads(kws).items() if v > 1]
                if (conc := applicant.account.concepts) != '{}':
                    applicant.account.concepts = json.loads(conc).items()
                applicant.account.education = json.loads(applicant.account.education)
                app_matches = matches  # Keywords which match with the job keywords

        # Plot big 5 personality types
        plt = plot_personality(applicant)

        srtd_applicants = [x for _, x in sorted(zip(matching, all_applicants), key=lambda x: x[0])]
        context = {'job': job, 'applicants': srtd_applicants, 'applicant': applicant, 'search': app_id,
                   'matches': app_matches, 'fig': plt, 'questions': zip(qstns, tones)}
        return render(request, 'resume_analysis_app/applicant_dash.html', context)
