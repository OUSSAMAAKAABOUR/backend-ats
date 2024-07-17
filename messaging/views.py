# views.py

from rest_framework.response import Response
from authentication.models import Message ,User
from authentication.serializers import MessageSerializer,UserSerializer 
from rest_framework.decorators import api_view
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Q, Max
from django.contrib.auth import get_user_model
User = get_user_model()
@api_view(['GET'])
def conversation_history(request, sender_id, receiver_id):
    # Fetch conversation history from the database
    messages = Message.objects.filter(
        sender=sender_id, recipient=receiver_id
    ) | Message.objects.filter(
        sender=receiver_id, recipient=sender_id
    )

    # Serialize the messages
    serialized_messages = MessageSerializer(messages, many=True)

    return Response(serialized_messages.data)




# @api_view(['GET'])
# def conversation_users_history(request, senderId):
#     # Fetch conversation history from the database
#     messages = Message.objects.filter(
#         Q(sender=senderId) | Q(recipient=senderId)
#     ).distinct()  # Ensuring distinct users

#     # Get unique recipient IDs excluding the current user
#     sender = set()
#     for message in messages:
#         if message.sender_id != senderId:
#             sender.add(message.sender_id)
#         if message.recipient_id != senderId:
#             sender.add(message.recipient_id)

#     # Fetch User instances corresponding to recipient IDs
#     users = User.objects.filter(pk__in=sender)

#     # Serialize the user instances
#     serializer = UserSerializer(users, many=True)  # Assuming you have a UserSerializer
#     return Response(serializer.data)
@api_view(['GET'])
def conversation_users_history(request, senderId):
    # Get the latest message for each conversation
    latest_messages = Message.objects.filter(
        Q(sender_id=senderId) | Q(recipient_id=senderId)
    ).values(
        'sender_id', 'recipient_id'
    ).annotate(
        last_message_time=Max('timestamp')
    ).order_by('-last_message_time')

    # Extract unique user IDs excluding the current user
    user_ids = set()
    for message in latest_messages:
        if message['sender_id'] != senderId:
            user_ids.add(message['sender_id'])
        if message['recipient_id'] != senderId:
            user_ids.add(message['recipient_id'])

    # Fetch User instances corresponding to the extracted IDs
    users = User.objects.filter(pk__in=user_ids)

    # Sort users based on their last interaction time
    sorted_users = sorted(
        users,
        key=lambda user: next(
            msg['last_message_time'] for msg in latest_messages
            if msg['sender_id'] == user.id or msg['recipient_id'] == user.id
        ),
        reverse=True
    )

    # Serialize the sorted user instances
    serializer = UserSerializer(sorted_users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def conversation_users_history2(request, senderId, receiverId):
    # Fetch conversation history from the database
    messages = Message.objects.filter(
        (Q(sender=senderId) & Q(recipient=receiverId)) |
        (Q(sender=receiverId) & Q(recipient=senderId))
    )

    # Fetch the specific User instance
    try:
        user = User.objects.get(pk=receiverId)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # Serialize the user instance
    serializer = UserSerializer(user)  # Assuming you have a UserSerializer

    return Response(serializer.data)
@api_view(['POST'])
def save_message(request, senderId, receiverId):
    try:
        sender = get_object_or_404(User, id=senderId)
        recipient = get_object_or_404(User, id=receiverId)
       
        content = request.data.get('content', 'Say hi!')
        print('sender',sender)
        print('recipient',recipient)
        print('content',content)
        Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=content,
        )
        return Response({'message': 'Message saved successfully'}, status=status.HTTP_201_CREATED)
   
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
