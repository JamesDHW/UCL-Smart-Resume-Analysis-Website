from django.urls import path

from .views._core_site_views import home, search_results, register
from .views.add_job import add_job
from .views.add_organisation import add_organisation
from .views.add_qualification import add_qualification
from .views.applicant_dash import applicant_dash
from .views.profile import profile
from .views.view_job import job_view
from .views.view_organisation import organisation_view
from .views.view_owned_organisations import owned_oragnisations
from .views.view_posted_positions import posted_positions
from .views.view_question import question_view


urlpatterns = [
    path('', home, name='home'),
    path('add_job/', add_job, name='add_job'),
    path('add_organisation/', add_organisation, name='add_organisation'),
    path('add_qualification/', add_qualification, name='add_qualification'),
    path('dashboard/', applicant_dash, name='dash'),
    path('interview/', question_view, name='interview'),
    path('job/', job_view, name='job_view'),
    path('organisation/', organisation_view, name='organisation_view'),
    path('my_organisations/', owned_oragnisations, name='owned_organisations'),
    path('positions/', posted_positions, name='posted_positions'),
    path('profile/', profile, name='profile'),
    path('register/', register, name="register"),
    path('search/', search_results, name='search'),
]