import json

import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Account, Question, QuestionResponse


def question_view(request):
    def save_response(respns):
        url = 'https://resume-node-red.mybluemix.net/Answer'
        response = requests.post(url, data=respns.encode('utf-8')).json()

        qst = Question.objects.get(title=request.POST.get("question"))
        question_response = QuestionResponse(user=request.user, question=qst, response=respns)

        for x in response["document_tone"]["tone_categories"]:
            if x["category_name"] == "Language Tone":
                question_response.language_tones = json.dumps(x)
            elif x["category_name"] == "Social Tone":
                question_response.social_tones = json.dumps(x)

        question_response.save()

    def personality_insights(respns_list):
        url = 'https://resume-node-red.mybluemix.net/Personality'
        all_responses = '\n'.join(respns_list)
        response = requests.post(url, data=all_responses.encode('utf-8')).json()
        # response.status_code = 200
        applicant = Account.objects.get(user=request.user)
        applicant.pers_big5 = json.dumps({x['name']: x['percentile'] for x in response['personality']})

        personality = iter(response['personality'])
        applicant.pers_openness = json.dumps({x['name']: x['percentile'] * 100 for x in next(personality)['children']})
        applicant.pers_conscien = json.dumps({x['name']: x['percentile'] * 100 for x in next(personality)['children']})
        applicant.pers_extraver = json.dumps({x['name']: x['percentile'] * 100 for x in next(personality)['children']})
        applicant.pers_agreeabl = json.dumps({x['name']: x['percentile'] * 100 for x in next(personality)['children']})
        applicant.pers_em_range = json.dumps({x['name']: x['percentile'] * 100 for x in next(personality)['children']})
        applicant.needs = json.dumps({x['name']: x['percentile'] * 100 for x in response['needs']})
        applicant.values = json.dumps({x['name']: x['percentile'] * 100 for x in response['values']})
        applicant.save()

    try:
        users_answers = [x.question.title for x in QuestionResponse.objects.filter(user=request.user).all()]
        question = next((x for x in Question.objects.all() if x.title not in users_answers and x.title != request.POST.get('question')), False)
    except:
        messages.warning(request, 'Could not find the questions.')
        return redirect('profile')

    # Some response posted to page
    if (request.method == "POST") and (response := request.POST.get('response')):

        # Get accumulated responses
        if responses := request.POST.get('responses'):
            responses = responses.replace("['", '["').replace("']", '"]').replace("', '", '", "')
            responses = json.loads(responses)
        else: responses = []

        responses.append(response)
        save_response(response)

        # If total answers are longer than 1000 words
        if (words := len(' '.join(responses).split(' '))) > 1000:
            personality_insights(responses)
            messages.success(request, 'Questions Complete - Thank You!')
            return redirect('profile')
        # If we haven't reached 1000 words, reload page with new question
        else:
            if question:
                context = {'question': question, 'responses': responses, 'prog': words / 10}
                return render(request, 'resume_analysis_app/view_question.html', context)
            else:
                messages.warning(request, 'All questions complete - try again later.')
                return redirect('profile')

    # GET request made to page
    else:
        if question:
            return render(request, 'resume_analysis_app/view_question.html', {'question': question, 'prog': 1})
        else:
            messages.warning(request, 'All questions complete - try again later.')
            return redirect('profile')
