import json
import threading

import requests
from django.shortcuts import render, redirect

from ..models import Account, Question, QuestionResponse


def question_view(request):
    def save_responses(qstns):
        url = 'https://resume-node-red.mybluemix.net/Answer'
        for qstn in qstns:
            response = requests.post(url, data=request.POST.get(qstn.title).encode('utf-8')).json()
            categories = ["Social Tone", "Language Tone"]   # Desired categories
            tones = [x for x in response["document_tone"]["tone_categories"] if x["category_name"] in categories]

            question_response = QuestionResponse(user=request.user, question=qstn, response=request.POST.get(qstn.title), tones=json.dumps(tones))
            question_response.save()

        # Once tonal analysis is finished move on to personality
        all_responses = '\n'.join([request.POST.get(q.title) for q in qstns])
        url = 'https://resume-node-red.mybluemix.net/Personality'
        response = requests.post(url, data=all_responses.encode('utf-8')).json()
        applicant = Account.objects.get(user=request.user)
        applicant.personality = json.dumps(response)
        applicant.save()

    questions = Question.objects.all()[:5]
    if request.method == "POST":
        t = threading.Thread(target=save_responses(questions))
        t.start()
        return redirect('profile')
    else:
        return render(request, 'resume_analysis_app/view_question.html', {'questions': questions})
