# from .views import create_interns_from_json
from django.urls import path
from . import views


urlpatterns = [
    # path('read-and-store-data/', create_interns_from_json, name='create_interns_from_json'),
    path('internship/', views.list_Internship),
    path('internship/create/', views.create_Internship),
    path('internship/<int:internship_id>/', views.retrieve_Internship),
    path('internship/<int:internship_id>/update/', views.update_Internship),
    path('internship/delete/<int:internship_id>/', views.delete_internship, name='delete_internship'),  
    path('intern/', views.list_Intern),
    path('internships_by_recruiter/<int:recruiter_id>/', views.all_internships_for_recruiter, name='all_internships_for_recruiter'),
    path('intern/create/', views.create_Intern),
    path('intern/<int:intern_id>/', views.retrieve_Intern),
    path('intern/<int:intern_id>/update/', views.retrieve_Intern),
    path('intern/<int:intern_id>/delete/', views.retrieve_Intern),
    path('start_scraping/<int:Internship_id>/', views.start_scraping),
    path('all_Internship_Interns/<int:Internship_id>/', views.all_Internship_Interns),
    path('code_outlook/<int:Internship_id>/', views.code_outlook, name='code_outlook'),
    path('intern-cv/<path:file_path>/', views.get_intern_cv, name='get_intern_cv'),    
    path('send-email/', views.send_email, name='send_email'),
    path('create-linkedin-ugc-post/', views.create_linkedin_ugc_post, name='create_linkedin_ugc_post'),
]
