from .models import User,Candidate,CustomToken,Recruiter
# <<<<<<< HEAD
# from .serializers import CustomTokenObtainPairSerializer, UserSerializer,CandidateSerializer,RecruiterSerializer
# =======
from .serializers import ApplicationSerializer, UserSerializer,CandidateSerializer,RecruiterSerializer
# >>>>>>> d38f552fb8c65c9629d1ed5d94496992a304116b
from rest_framework.decorators import api_view ,authentication_classes,permission_classes
from rest_framework.response import Response 
from rest_framework import status
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.contrib.auth import authenticate, login
from datetime import timedelta
from dotenv import load_dotenv
import os
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from django.shortcuts import redirect
from django.http import HttpResponse
import requests
from .models import Application
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Candidate
from .serializers import RecruiterSerializer
import random
import string

# Load the .env file
load_dotenv()


# @api_view(['POST'])
# def user_login(request):
#     email = request.data.get('email')
#     password = request.data.get('password')

  
#     user = authenticate(email=email, password=password)

#     if user is None:
#         return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
#     if not user.is_active:
#         return Response({"detail": "Your account is not active, please verify your email address"}, status=status.HTTP_401_UNAUTHORIZED)
#     print('this is the user : ',user)
#     # log the user into the current session
#     login(request, user)

#     # Generate tokens
#     refresh = RefreshToken.for_user(user)
#     access = AccessToken.for_user(user)

#     return Response({
#         "access_token": str(access),
#         "refresh_token": str(refresh),
#         "status": status.HTTP_200_OK,
#         "user": UserSerializer(instance=user).data,
#         'role': user.role
#     })
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)

    if user is None:
        return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({"detail": "Your account is not active, please verify your email address"}, status=status.HTTP_401_UNAUTHORIZED)
    print('this is the user : ',user)
    # log the user into the current session
    login(request, user)

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access = CustomTokenObtainPairSerializer.get_token(user)

    return Response({
        "access_token": str(access.access_token),
        "refresh_token": str(refresh),
        "status": status.HTTP_200_OK,
        "user": UserSerializer(instance=user).data,
        'role': user.role
    })



class CustomTokenRefreshView(TokenRefreshView):
    pass



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from dotenv import load_dotenv
import os
from .models import Candidate, CustomToken
from .serializers import CandidateSerializer

@api_view(['POST'])
def signup(request):
    serializer = CandidateSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        email = request.data.get('email')

        if Candidate.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        candidate = serializer.save()
        candidate.set_password(request.data['password'])
        candidate.is_active = False
        candidate.save()

        token = default_token_generator.make_token(candidate)
        expiration_time = timezone.now() + timezone.timedelta(hours=12)
        CustomToken.objects.create(user=candidate, token=token, expiration_date=expiration_time)


        uidb64 = urlsafe_base64_encode(force_bytes(candidate.pk))
        load_dotenv()
        reset_password = os.getenv('PULS_DIGITAL')

        verification_url = f"{reset_password}{uidb64}/{token}/"

        subject = 'Verify your email address'
        message = f'Click the following link to verify your email address: <a href="{verification_url}">click</a>'
        send_mail(subject, '', '', [email], html_message=message)
        
        return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def email_verified(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        custom_token = CustomToken.objects.get(user=user, token=token)
    except CustomToken.DoesNotExist:
        return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)
        
    if timezone.now() > custom_token.expiration_date:
        return Response({'error': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        user.is_active = True
        user.save()
        custom_token.delete()
        
        return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate and save token with expiration time
    token = default_token_generator.make_token(user)
    expiration_time = timezone.now() + timedelta(minutes=15)
    CustomToken.objects.create(user=user, token=token, expiration_date=expiration_time)
    
    # Generate password reset URL
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    load_dotenv()
    print(os.getenv("RESETED_PASSWORD"))
    reset_password = os.getenv('RESETED_PASSWORD')

    verification_url = f"{reset_password}{uidb64}/{token}/"

    # Send verification email
    subject = 'Reset Your Password'
    
    message = f'Click the following link to reset your password: <a href="{verification_url}">click</a>'

    recipient_email = user.email
    
    send_mail(subject, None, None, [recipient_email], None, None, None, None, message)
    
    return Response({"message": "Check your email for password reset instructions"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reseted_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        custom_token = CustomToken.objects.get(user=user, token=token)
    except CustomToken.DoesNotExist:
        return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)
        
    if timezone.now() > custom_token.expiration_date:
        return Response({'error': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        custom_token.delete()
        
        return Response({'message': 'Password successfully reset'}, status=status.HTTP_200_OK)
    


    

# @api_view(['GET'])
# def linkedin_auth(request):
#     # Redirect the user to the LinkedIn authorization page
#     linkedin_auth_url = (
#         "https://www.linkedin.com/oauth/v2/authorization"
#         "?response_type=code"
#         "&client_id=78q7n8oilzgi18"
#         "&redirect_uri=http://localhost:3000/admin/dashboard"
#         "&state=1234"
#         "&scope=openid%20email%20profile"
#     )
    
#     return redirect(linkedin_auth_url)

# # Django view for handling LinkedIn callback
# import requests




# @api_view(['GET'])

# def linkedin_callback(request):

    
#     # Extract the authentication code from the query parameters
#     code = request.GET.get('code')
#     state = request.GET.get('state')
#     # Make a POST request to exchange the code for an access token
#     if code:
#         params = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': 'https://oauth.pstmn.io/linkedin/callback',
#             'client_id': '78q7n8oilzgi18',
#             'client_secret': 'WPL_AP0.khyYEipcPsAtKLM1.NzU5ODc1NDU1'
#         }
#         response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=params)

#         # Process the response from LinkedIn
#         if response.status_code == 200:
#             access_token = response.json()['access_token']
#             # Now you can use the access token to make requests to LinkedIn API
#             # Store the access token in session or database for future use
#             return HttpResponse('Authentication successful! Access token: ' + access_token)
#         else:
#             return HttpResponse('Failed to get access token')

#     return HttpResponse('No code received')



# @api_view(['GET'])
# def linkedin_auth(request):
#     # Redirect the user to the LinkedIn authorization page
#     linkedin_auth_url = (
#         "https://www.linkedin.com/oauth/v2/authorization"
#         "?response_type=code"
#         "&client_id=" + os.getenv('CLIENT_ID') +
#         "&redirect_uri=" + os.getenv('REDIRECT_URI') +
#         "&state=1234"
#         "&scope=openid%20email%20profile"
#     )
    
#     return redirect(linkedin_auth_url)

import base64
import json


def parse_id_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise Exception("Incorrect id token format")

    payload = parts[1]
    padded = payload + '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(padded)
    # print('code decoded : ',decoded)
    return json.loads(decoded)
# @api_view(['GET'])
# def linkedin_callback(request):
#     # Extract the authentication code from the query parameters
#     code = request.GET.get('code')
#     state = request.GET.get('state')
#     print('this is the code :', code)

#     # Make a POST request to exchange the code for an access token
#     if code:
#         params = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': 'http://localhost:3000/login',
#             'client_id': '78q7n8oilzgi18',
#             'client_secret': 'WPL_AP0.khyYEipcPsAtKLM1.NzU5ODc1NDU1'
#         }
#         response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=params)

#         # Process the response from LinkedIn
#         if response.status_code == 200:
#             access_token = response.json().get('access_token')
#             id_token = response.json().get('id_token')
#             decoded = parse_id_token(id_token)
#             print('this is the id token : ', decoded)

#             # Extract user data from the decoded token
#             name = decoded.get('given_name')
#             email = decoded.get('email')
#             last_name = decoded.get('family_name')

#             # Create a dictionary containing the user data
#             user_data = {
#                 # 'username': name,  # You can set the username to the email address
#                 'email': email,
#                 'first_name': name,
#                 'last_name': last_name
#             }

            

#             print('test1==>',email)
#             # Check if the user already exists
#             user = User.objects.filter(email=email).first()
#             print('test2 -->', user)
#             # If user doesn't exist, create a new user
#             if not user:
#                 print('test3')
#                 user = User.objects.create_user(username=name, email=email, first_name=name, last_name=last_name)
#                 user.save()
            
#             else: 
#                 print('test4==>',user)
            
#             # Pass the user data to the login function
#                 login(request, user)


#             # Generate tokens
#                 refresh = RefreshToken.for_user(user)
#                 access = AccessToken.for_user(user)
#                 return Response({
#                     "access_token": str(access),
#                     "refresh_token": str(refresh),
#                     "status": status.HTTP_200_OK,
#                     "user": UserSerializer(instance=user).data
#                 })
#         else:
#             return HttpResponse('Failed to get access token')

#     return HttpResponse('No code received')

@api_view(['GET'])
def linkedin_callback(request):
    code = request.GET.get('code')
    print('this is the code :', code)
    # print('this is the redirect URI from env file :', os.getenv('REDIRECT_URI'),os.getenv('CLIENT_ID'),os.getenv('CLIENT_SECRET'))

    if code:
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': os.getenv('REDIRECT_URI'),
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET')
        }
        response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=params)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            id_token = response.json().get('id_token')
            decoded = parse_id_token(id_token)
            print('this is the id token : ', decoded)
            print('this is the whole response : ', response.json())

            name = decoded.get('given_name')
            email = decoded.get('email')
            last_name = decoded.get('family_name')

            print('test1==>', email)
            user = User.objects.filter(email=email).first()
            print('test2 -->', user)

            if not user:
                print('test3')
                user = Candidate.objects.create(username=email, email=email, first_name=name, last_name=last_name)
                print("test6")
                user.is_active = True
                print("test7")
                user.save()
                print("test8")
                print('user well created ')
            else:
                print('test4==>', user)

            # Specify the backend for the login function
            backend = 'django.contrib.auth.backends.ModelBackend'  # or the specific backend you are using
            user.backend = backend

            login(request, user, backend=backend)

            refresh = RefreshToken.for_user(user)
            # access = AccessToken.for_user(user)
            access = CustomTokenObtainPairSerializer.get_token(user)

            return Response({
                "linkedIn_access_token":access_token,
                "access_token": str(access),
                "refresh_token": str(refresh),
                "status": status.HTTP_200_OK,
                "user": UserSerializer(instance=user).data
            })
        else:
            return HttpResponse('Failed to get access token')

    return HttpResponse('No code received')


from django.contrib.auth import login as auth_login

# @api_view(['GET'])
# def get_google_user_info(request):
#     email = request.query_params.get('email')
#     print(email)
#     # Check if the user already exists
#     user = User.objects.filter(email=email).first()
#     print(user)
#     if user:
#         # If the user exists, log them in
#         auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#     else:
#         # If the user doesn't exist, create a new user
#         name = request.query_params.get('givenName')
#         last_name = request.query_params.get('familyName')

#         user = Candidate.objects.create(
#             username=email,
#             email=email,
#             first_name=name,
#             last_name=last_name
#         )
#         user.is_active = True
#         user.save()

#         # Log in the newly created user
#         auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

#     # Generate access and refresh tokens
#     refresh_token = RefreshToken.for_user(user)
#     access_token = AccessToken.for_user(user)
#     # access = CustomTokenObtainPairSerializer.get_token(user)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer

User = get_user_model()

@api_view(['GET'])
def get_google_user_info(request):
    email = request.query_params.get('email')
    print(email)
    # Check if the user already exists
    user = User.objects.filter(email=email).first()
    print(user)
    if user:
        # If the user exists, log them in
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    else:
        # If the user doesn't exist, create a new user
        name = request.query_params.get('givenName')
        last_name = request.query_params.get('familyName')

        user = Candidate.objects.create(
            username=email,
            email=email,
            first_name=name,
            last_name=last_name
        )
        user.is_active = True
        user.save()

        # Log in the newly created user
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # Generate access and refresh tokens
    refresh_token = RefreshToken.for_user(user)
    access_token = CustomTokenObtainPairSerializer.get_token(user).access_token

    # Return tokens along with user data
    return Response({
        "access_token": str(access_token),
        "refresh_token": str(refresh_token),
        "status": status.HTTP_200_OK,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
    })

    

@api_view(['GET'])
def get_candidates_for_post(request, post_id):
    applications = Application.objects.filter(post_id=post_id)
    candidates = [application.candidate for application in applications]
    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def get_files_for_candidate(request, candidate_id):
#     applications = Application.objects.filter(candidate_id=candidate_id).values('resume','date')
#     return JsonResponse(list(applications), safe=False)
from django.db.models import Q
@api_view(['GET'])
def get_files_for_candidate(request, candidate_id):
    applications = Application.objects.filter(
        Q(candidate_id=candidate_id) & 
        (Q(resume__isnull=False) & ~Q(resume=''))
    ).values('resume', 'date')

    return JsonResponse(list(applications), safe=False)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.db import transaction
from .models import Candidate
from .serializers import RecruiterSerializer
import random
import string

# @api_view(['POST'])
# def change_role_to_recruiter(request, user_id):
#     try:
#         # Check if the candidate exists
#         candidate = get_object_or_404(Candidate, id=user_id)
        
#         # Store candidate information
#         candidate_info = {
#             'username': candidate.username + '_recruiter',  # Add '_recruiter' suffix to username to ensure uniqueness
#             'password': ''.join(random.choices(string.ascii_letters + string.digits, k=10)),  # Generate a random password
#             'first_name': candidate.first_name,
#             'last_name': candidate.last_name,
#             'email': candidate.email,
#             'role': 'r',
#             'gender': candidate.gender if candidate.gender in ['m', 'f'] else 'm',  # Ensure valid gender value
#             'address': candidate.address,
#             'city': candidate.city,
#             'country': candidate.country,
#             'postal_code': candidate.postal_code,
#             'company': 'Default Company',
#             'comp_industry': 'default',
#             'comp_description': 'default'
#         }

#         # Use Django's transaction.atomic() to ensure that all operations are atomic
#         with transaction.atomic():
#             # Delete the candidate
#             candidate.delete()

#             # Create a new recruiter with candidate's information
#             serializer = RecruiterSerializer(data=candidate_info)
            
#             if serializer.is_valid():
#                 recruiter = serializer.save()
#                 recruiter.is_active = True
#                 recruiter.save()  

#                 auth_login(request, recruiter, backend='django.contrib.auth.backends.ModelBackend')
                
#                 refresh_token = RefreshToken.for_user(recruiter)
#                 access_token = AccessToken.for_user(recruiter)

#                 return JsonResponse({
#                     "access_token": str(access_token),
#                     "refresh_token": str(refresh_token),
#                     "recruiter_id": recruiter.id,  # Include recruiter_id in the response
#                 }, status=status.HTTP_201_CREATED)
#             else:
#                 # If serializer is invalid, return the errors
#                 return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     except ObjectDoesNotExist:
#         return JsonResponse({'error': 'Candidate does not exist'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         # Catch any other exceptions and return an error response
#         return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

@api_view(['POST'])
def change_role_to_recruiter(request, user_id):
    try:
        # Check if the candidate exists
        candidate = get_object_or_404(Candidate, id=user_id)
        
        # Store candidate information
        candidate_info = {
            'username': candidate.username + '_recruiter',  # Add '_recruiter' suffix to username to ensure uniqueness
            'password': ''.join(random.choices(string.ascii_letters + string.digits, k=10)),  # Generate a random password
            'first_name': candidate.first_name,
            'last_name': candidate.last_name,
            'email': candidate.email,
            'role': 'r',
            'gender': candidate.gender if candidate.gender in ['m', 'f'] else 'm',  # Ensure valid gender value
            'address': candidate.address,
            'city': candidate.city,
            'country': candidate.country,
            'postal_code': candidate.postal_code,
            'company': 'Default Company',
            'comp_industry': 'default',
            'comp_description': 'default'
        }

        # Use Django's transaction.atomic() to ensure that all operations are atomic
        with transaction.atomic():
            # Delete the candidate
            candidate.delete()

            # Create a new recruiter with candidate's information
            serializer = RecruiterSerializer(data=candidate_info)
            
            if serializer.is_valid():
                recruiter = serializer.save()
                recruiter.is_active = True
                recruiter.save()  

                auth_login(request, recruiter, backend='django.contrib.auth.backends.ModelBackend')
                
                # Generate access and refresh tokens using the custom serializer
                refresh_token = RefreshToken.for_user(recruiter)
                access_token = CustomTokenObtainPairSerializer.get_token(recruiter).access_token

                return JsonResponse({
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token),
                    "recruiter_id": recruiter.id, 
                }, status=status.HTTP_201_CREATED)
            else:
                # If serializer is invalid, return the errors
                return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Candidate does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Catch any other exceptions and return an error response
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer

@api_view(['GET', 'POST'])
def event_list_create(request):
    if request.method == 'GET':
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['DELETE'])
def event_list_delete(request, event_id):
    if not event_id:
        return Response({"error": "ID is required to delete an event."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return Response({"message": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
# def event_detail(request, pk):
#     try:
#         event = Event.objects.get(pk=pk)
#     except Event.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     serializer = EventSerializer(event)
#     return Response(serializer.data)

@api_view(['GET'])
def events_by_recruiter(request, recruiter_id):
    events = Event.objects.filter(recruiter_id=recruiter_id)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationStepUpdateSerializer
@api_view(['PATCH'])
def update_application_step(request, pk):
    try:
        application = Application.objects.get(pk=pk)
    except Application.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = ApplicationStepUpdateSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)