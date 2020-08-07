import json

# import PyPDF2 as PyPDF2
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

from .models import Applicant, JobDescription


def home(request):
    jobs = JobDescription.objects.all().order_by('-id')[:10]
    return render(request, 'resume_analysis_app/home.html', {'jobs': jobs})


@login_required
def profile(request):

    def PDF_to_text(PDF):
        # https://stackoverflow.com/questions/44024697/how-to-read-pdf-file-using-pdfminer3k
        # Extract text from PDF upload
        parser = PDFParser(PDF)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        device = PDFPageAggregator(PDFResourceManager(), laparams=LAParams())
        interpreter = PDFPageInterpreter(PDFResourceManager(), device)
        extrctd_txt = ''

        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extrctd_txt += lt_obj.get_text()
        extrctd_txt = extrctd_txt.replace("•\n", "-").replace("•", "-").replace(u'\u2013', '–')
        return extrctd_txt

    # If CV submitted to page
    if request.method == 'POST' and len(request.FILES) > 0:
        CV = request.FILES['cv']
        if CV.name[-4:] == '.pdf':
            applicant = Applicant.objects.get(user=request.user)
            applicant.resume = CV
            applicant.filename = CV.name

            pdf_text = PDF_to_text(CV)    # Text extracted
            applicant.resume_plain_text = pdf_text

            # Call NodeRED to access Watson
            url = 'https://resume-node-red.mybluemix.net/CV'
            response = requests.post(url, data=pdf_text.encode('ascii', errors='ignore')).json()
            applicant.categories = json.dumps(response['categories'])
            applicant.concepts = json.dumps(response['concepts'])

            # Select all proper nouns from text
            # Take into account strings of multiple proper nouns
            temp_keywords = []
            common_PROPN = 'JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecemberABCDEFGCSEs' \
                           'References'
            prev = None
            for word in response['syntax']['tokens']:
                if word['part_of_speech'] == 'PROPN' or (word['part_of_speech'] == 'NOUN' and word['text'][0].isupper()):
                    if prev and word['text'].lower() in common_PROPN.lower():
                        temp_keywords.append(prev)
                    elif word['text'].lower() in common_PROPN.lower():
                        continue
                    elif prev:
                        prev += ' ' + word['text']
                        temp_keywords.append(prev)
                    else:
                        temp_keywords.append(word['text'])
                        prev = word['text']
                else:
                    prev = None
            i = 0
            while i + 1 < len(temp_keywords):
                if temp_keywords[i] in temp_keywords[i + 1]:
                    del temp_keywords[i]
                else:
                    i += 1

            # Reformat list of proper nouns to be a dictionary of counts
            my_keywords = {}
            for kw in temp_keywords:
                if kw not in common_PROPN:
                    my_keywords[kw] = temp_keywords.count(kw)

            # Add in IBMs keywords
            for kw in response['keywords']:
                my_keywords[kw['text']] = kw['count']

            applicant.keywords = json.dumps(my_keywords)

            applicant.save()
            messages.success(request, 'Resume Uploaded.')
            return redirect('profile')
        else:
            messages.warning(request, 'Incorrect file type (must be .pdf).')
            return redirect('profile')
    elif request.method == 'POST':
        messages.warning(request, 'No resume selected.')
        return redirect('profile')
    else:
        # GET request made
        jobs = JobDescription.objects.filter(author=request.user)
        return render(request, 'resume_analysis_app/profile.html', {'jobs': jobs})


def search_results(request):
    search = request.GET.get('search')
    jobs = JobDescription.objects.filter(title__icontains=search)
    return render(request, 'resume_analysis_app/search_results.html', {'jobs': jobs, 'search': search})


def job_view(request):
    job_id = request.GET.get('id')
    if job_id:
        try:
            job = JobDescription.objects.get(id=job_id)
        except:
            messages.warning(request, 'Could not find job details.')
            return redirect('home')
        if request.GET.get('apply'):
            job.applicants.add(request.user)
            messages.success(request, 'Applied for position.')
    else:
        messages.warning(request, 'Error finding job details.')
        return redirect('home')

    return render(request, 'resume_analysis_app/job_view.html', {'job': job})


@login_required
def add_job(request):
    if request.method == "POST" and request.POST.get('id'):
        # job_id passed through - editing an existing job
        job_id = request.POST.get('id')
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
        return redirect('home')
    else:
        applicant, app_matches, matching = None, None, []    # Defaults + List of number of matching keywords
        job_keywords = ' '.join(job.keywords_func.keys()).lower()
        for usr in job.applicants.all():
            matches = [kw for kw in json.loads(usr.applicant.keywords).keys() if kw.lower() in job_keywords.split(' ')]
            matching.append(len(matches))

            # Get the currently selected applicant
            if request.GET.get('user') and str(usr.id) == request.GET.get('user'):
                applicant = usr
                applicant.applicant.keywords = json.loads(applicant.applicant.keywords).keys()
                app_matches = matches  # Keywords which match with the job keywords

        sorted_applicants = [x for _, x in sorted(zip(matching, job.applicants.all()), key=lambda pair: pair[0], reverse=True)]
        context = {'job': job, 'applicants': sorted_applicants, 'applicant': applicant, 'matches': app_matches}
        return render(request, 'resume_analysis_app/applicant_dash.html', context)
