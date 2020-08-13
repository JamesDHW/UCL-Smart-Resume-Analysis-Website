import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser, PDFDocument

from ..models import Account, JobDescription
from ._my_functions import get_keywords

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

    def upload_cv(CV):
        applicant = Account.objects.get(user=request.user)
        applicant.resume = CV
        applicant.filename = CV.name

        pdf_text = PDF_to_text(CV)  # Text extracted
        applicant.resume_plain_text = pdf_text

        # Call NodeRED to access Watson
        url = 'https://resume-node-red.mybluemix.net/CV'
        response = requests.post(url, data=pdf_text.encode('ascii', errors='ignore')).json()

        my_keywords = get_keywords(pdf_text)

        applicant.categories = json.dumps(response['categories'])
        applicant.concepts = json.dumps(response['concepts'])
        applicant.keywords = json.dumps(my_keywords)

        applicant.save()

    # If CV submitted to page
    if request.method == 'POST' and len(request.FILES) > 0:
        cv = request.FILES['cv']
        # If in PDF format
        if cv.name[-4:] == '.pdf':
            upload_cv(cv)
            messages.success(request, 'Resume Uploaded.')
            return redirect('profile')
        else:
            messages.warning(request, 'Incorrect file type (must be .pdf).')
            return redirect('profile')
    # No files sent to path
    elif request.method == 'POST':
        messages.warning(request, 'No resume selected.')
        return redirect('profile')
    # GET request made
    else:
        # jobs = JobDescription.objects.filter(author=request.user)
        # context = {'jobs': jobs}
        return render(request, 'resume_analysis_app/profile.html')
