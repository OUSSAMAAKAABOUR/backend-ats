    
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_candidate),  # URL for creating a candidate
    path('list/', views.list_candidates),  # URL for listing all candidate
    path('<int:candidate_id>/find/', views.retrieve_candidate),  # URL for retrieving a candidate
    path('<int:candidate_id>/update/', views.update_candidate),  # URL for updating a candidate
    path('<int:candidate_id>/delete/', views.delete_candidate),  # URL for deleting a candidate 
    path('application/create/', views.create_application, name='create_application'),
    path('list_applied_posts/<int:candidate_id>/', views.list_applied_posts, name='list_applied_posts'), 
    path('applications/by-post/<int:post_id>/', views.get_applications_by_post_id, name='get-applications-by-post-id'),

    # save post urls
    path('save_post/<int:candidate_id>/<int:post_id>/', views.save_post, name='save_post'),
    path('list_saved_posts/<int:candidate_id>/', views.list_saved_posts, name='list_saved_posts'), 
    path('get_similar_posts/<int:candidate_id>/', views.get_similar_posts, name='get_similar_posts'),
    
]