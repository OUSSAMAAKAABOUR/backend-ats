from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_post),  # URL for creating a post
    path('list/', views.list_posts),  # URL for listing all posts
    path('list/<int:recruiter_id>/', views.list_posts_by_recruiter),  # URL for listing all posts for a recruiter
    path('<int:post_id>/find', views.retrieve_post),  # URL for retrieving a post
    path('<int:post_id>/update/', views.update_post),  # URL for updating a post
    path('<int:post_id>/delete/', views.delete_post),  # URL for deleting a post
    path('<int:post_id>/findCandidate/', views.findCandidate),  # URL for deleting a post
    path('search_recommendation/', views.search_recommendation, name='search_recommendation'),


]
