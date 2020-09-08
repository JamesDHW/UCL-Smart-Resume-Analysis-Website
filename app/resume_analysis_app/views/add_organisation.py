from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import Organisation


@login_required
def add_organisation(request):
    def update_user_org(usr):
        email_ext = usr.email.split('@')[-1]
        try:
            new_org = Organisation.objects.get(email_extension=email_ext)
        except:
            pass
        else:
            usr.account.organisation = new_org
            usr.account.save()
            messages.success(request, 'Account added to organisation.')

    if request.method == "POST" and request.user.is_authenticated:
        if org_id := request.POST.get('id'):
            try:
                org = Organisation.objects.get(id=org_id)
            except:
                messages.warning(request, 'Could not find org.')
                return redirect('profile')
            else:
                # Check credentials to edit
                if org.owner != request.user:
                    messages.warning(request, 'Invalid credentials.')
                    return redirect('profile')
                # If credentials pass and we want to delete
                elif request.POST.get('delete'):
                    org.delete()
                    messages.success(request, 'Organisation deleted.')
                    return redirect('profile')
                # Neither update nor delete - just display the org
                elif not request.POST.get('update'):
                    return render(request, 'resume_analysis_app/add_organisation.html', {'org': org})
        # No org_id provided give a blank org description
        else:
            org = Organisation()
            org.owner = request.user

        # Now POST request is to save or update a org
        if len(request.FILES) == 0:
            messages.warning(request, 'No logo selected')
        else:
            logo = request.FILES['logo']
            if logo.name[-4:] == '.png':
                org.logo = logo
                org.name = request.POST.get('name')
                org.email_extension = request.POST.get('email').lower()
                org.company_description = request.POST.get('description')
                org.website = request.POST.get('website')
                org.save()
                update_user_org(request.user)
                messages.success(request, 'Organisation saved.')
            else:
                messages.warning(request, 'Incorrect logo file type (must be .png).')

        return redirect('profile')
    elif not request.user.is_authenticated:
        return redirect('home')
    # Just get the page with the form on
    else:
        context = {}
        if org_id := request.GET.get('id'):
            try:
                org = Organisation.objects.get(id=org_id)
                if org.owner == request.user:
                    context = {'organisation': org}
            except:
                pass
        return render(request, 'resume_analysis_app/add_organisation.html', context)
