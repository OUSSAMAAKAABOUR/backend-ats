# from django.conf import settings
# from django.urls import path
# from . import views
# from django.conf.urls.static import static

# urlpatterns = [
#     path('login/',views.user_login),
#     path('signup/',views.signup),
#     path('email_verified/<str:uidb64>/<str:token>/',views.email_verified),
#     path('reset_password/',views.reset_password),
#     path('reseted_password/<str:uidb64>/<str:token>/',views.reseted_password),
#     path('token/refresh/', views.CustomTokenRefreshView.as_view),


#     path('linkedin-auth/', views.linkedin_auth, name='linkedin_auth'),
#     path('linkedin-callback/', views.linkedin_callback, name='linkedin_callback'),


#     # path('accounts/', include('allauth.urls')),
#     # path('employee/savefile/', views.SaveFile, name='save-file'),
#     path('google/userinfo/', views.get_google_user_info, name='google_user_info'),
#     path('create-linkedin-ugc-post/',views.create_linkedin_ugc_post name='create_linkedin_ugc_post'),

# ] 
# # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.user_login),
    path('signup/', views.signup),
    path('email_verified/<str:uidb64>/<str:token>/', views.email_verified),
    path('reset_password/', views.reset_password),
    path('reseted_password/<str:uidb64>/<str:token>/', views.reseted_password),
    path('token/refresh/', views.CustomTokenRefreshView.as_view()),

    # path('linkedin-auth/', views.linkedin_auth, name='linkedin_auth'),
    path('linkedin-callback/', views.linkedin_callback, name='linkedin_callback'),
                      
    path('google/userinfo/', views.get_google_user_info, name='google_user_info'),
    # path('get-linkedin-ugc-post-endpoint/', views.get_linkedin_ugc_post_endpoint, name='get_linkedin_ugc_post_endpoint'),
    path('candidates-for-post/<int:post_id>/', views.get_candidates_for_post, name='get_candidates_for_post'),
    path('files-for-candidate/<int:candidate_id>/', views.get_files_for_candidate, name='get_files_for_candidate'),

    path('change-role-to-recruiter/<int:user_id>/', views.change_role_to_recruiter, name='change_role_to_recruiter'),

    path('events/', views.event_list_create, name='event-list-create'),
    # path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:recruiter_id>/', views.events_by_recruiter, name='events-by-recruiter'),
    path('events/delete/<int:event_id>/', views.event_list_delete, name='event_delete'),
    path('applications/<int:pk>/update-step/', views.update_application_step, name='update-application-step'),

]
