from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/<int:sender_id>/<int:receiver_id>/history/', views.conversation_history),
    path('conversation_users_history/<int:senderId>/', views.conversation_users_history),
    path('conversation_users_history2/<int:senderId>/<int:receiverId>/', views.conversation_users_history2),
    path('save_message/<int:senderId>/<int:receiverId>/', views.save_message),
    
]