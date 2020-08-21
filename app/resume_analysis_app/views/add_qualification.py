import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import Account


@login_required
def add_qualification(request):
    if request.method == 'POST':
        try:
            account = Account.objects.get(user=request.user)
            account.education = json.loads(account.education)
            insti = request.POST.get('institution')
            quali = request.POST.get('qualification')
            grade = request.POST.get('grade')
        except:
            messages.warning(request, 'Qualification not added.')
            return redirect('profile')
        else:
            account.education.append({
                "institution": insti,
                "qualification": quali,
                "grade": grade})
            account.education = json.dumps(account.education)
            account.save()
            messages.success(request, 'Qualification added.')
            return redirect('profile')
    else:
        return render(request, 'resume_analysis_app/add_qualification.html')
