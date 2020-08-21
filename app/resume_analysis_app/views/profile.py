import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser, PDFDocument

from ..models import Account
from .._app_functions import extract_insights


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
        account = Account.objects.get(user=request.user)
        account.resume = CV
        account.filename = CV.name

        pdf_text = PDF_to_text(CV)  # Text extracted
        account.resume_plain_text = pdf_text

        extracted_kws, extracted_cats, extracted_concepts = extract_insights(pdf_text)

        account.keywords = json.dumps(extracted_kws)
        account.concepts = json.dumps(extracted_concepts)
        for i, cat in enumerate(extracted_cats):
            if i == 0: account.category1 = cat
            if i == 1: account.category2 = cat
            if i == 2: account.category3 = cat

        account.save()

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
    # To delete a qualification
    elif request.method == 'POST' and (qual := request.POST.get('delete')):
        account = Account.objects.get(user=request.user)
        qual = json.loads(qual.replace("', '", '", "').replace("': '", '": "').replace("{'", '{"').replace("'}", '"}'))
        account.education = json.loads(account.education)
        account.education.remove(qual)
        account.education = json.dumps(account.education)
        account.save()
        messages.success(request, 'Qualification removed.')
        return redirect('profile')
    # No files sent to path
    elif request.method == 'POST':
        messages.warning(request, 'No resume selected.')
        return redirect('profile')
    # GET request made
    else:
        # jobs = JobDescription.objects.filter(author=request.user)
        # context = {'jobs': jobs}
        account = Account.objects.get(user=request.user)
        account.education = json.loads(account.education)
        return render(request, 'resume_analysis_app/profile.html', {'account': account})
