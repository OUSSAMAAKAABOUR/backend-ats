from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Internship,Intern
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from .serializers import InternshipSerializer,InternSerializer
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from authentication.models import Recruiter
from django.conf import settings
import os
import sys


@api_view(['POST'])
def create_Internship(request):
    serializer = InternshipSerializer(data=request.data)
    if serializer.is_valid():
        recruiter_id = serializer.validated_data.get('recruiter')
        try:
            recruiter = Recruiter.objects.get(pk=recruiter_id)
        except recruiter.DoesNotExist:
            return Response({'error': 'Recruiter does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def list_Internship(request):
    interns = Internship.objects.all()
    serializer = InternshipSerializer(interns, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def retrieve_Internship(request, Internship_id):
    intern = get_object_or_404(Internship, pk=Internship_id)
    serializer = InternshipSerializer(intern)
    return Response(serializer.data)

@api_view(['PUT'])
def update_Internship(request, Internship_id):
    intern = get_object_or_404(Internship, pk=Internship_id)
    serializer = InternshipSerializer(intern, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_internship(request, internship_id):
    # Get the internship object by ID
    internship = get_object_or_404(Internship, id=internship_id)
    
    # Delete the internship object
    internship.delete()
    return Response({"message": "Internship deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def list_Intern(request):
    interns = Intern.objects.all()
    serializer = InternSerializer(interns, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def list_interns_by_internship(request, recruiter_id):
    try:
        internship = Internship.objects.get(id=recruiter_id)
    except Internship.DoesNotExist:
        return Response({"error": "Internship not found"}, status=status.HTTP_404_NOT_FOUND)
    
    interns = internship.internship.all()
    serializer = InternSerializer(interns, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_Intern(request):
    serializer = InternSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def retrieve_Intern(request, intern_id):
    try:
        intern = Intern.objects.get(pk=intern_id)
    except Intern.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InternSerializer(intern)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InternSerializer(intern, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        intern.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['Post'])
# def create_interns_from_json(request, json_file_path=None):
#     if json_file_path is None:
#         json_file_path = request.query_params.get('json_file_path')

#     if json_file_path:
#         try:
#             with open(json_file_path, 'r') as file:
#                 data = json.load(file)
#                 interns_data = data.get('interns', []) 

#                 for intern_data in interns_data:
#                     intern = Intern(
#                         name=intern_data.get('name'),
#                         email=intern_data.get('email'),
#                         phone=intern_data.get('phone'),
#                         skills=intern_data.get('skills'),
#                         education=intern_data.get('education'),
#                     )
#                     intern.save()  

#             return Response({'message': 'Interns created successfully'})
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)
#     else:
#         return Response({'error': 'No JSON file path provided'}, status=400)



# @api_view(['POST'])
# def create_Internship(request,recruiter_id):
#     if request.method == 'POST':
#         get_object_or_404(Recruiter,pk=recruiter_id)
#         # Load access token data from JSON file
#         with open(r'C:/Users/youne/OneDrive/Desktop/project4/backend_django-master/backend_django-master/utils/test.json', 'r') as f:
#             access_token_data = json.load(f)

#         # Create Intern instance
#         internship = Internship.objects.create(
#             access_token=access_token_data,
#             recruiter_id=recruiter_id
#         )
        
#         return JsonResponse({'message': 'Intern created successfully'}, status=201)
    
#     return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
def all_Internship_Interns(request, Internship_id):
    try:
        # internship = Internship.objects.get(pk=Internship_id)
        interns = Intern.objects.filter(id_internship=Internship_id)
        serializer = InternSerializer(interns, many=True)
        # serializer.save()
        return Response(serializer.data)
    except Internship.DoesNotExist:
        return Response({"error": "Internship matching query does not exist."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def all_internships_for_recruiter(request, recruiter_id):
    try:
        internships = Internship.objects.filter(recruiter=recruiter_id)
        if not internships:
            return Response({"error": "No internships found for this recruiter."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InternshipSerializer(internships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# sys.path.append('C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project/Scrapping_Service/Outlook')
# from demo import handle_Scrapping
# Construct the relative path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scrapping_service_path = os.path.join(base_dir, 'Scrapping_Service', 'Outlook')
# Debugging: Print the constructed path
print(f"Constructed Scrapping Service path: {scrapping_service_path}")
# Append the constructed path to sys.path
sys.path.append(scrapping_service_path)
from demo import handle_Scrapping

@api_view(['GET'])
def start_scraping(request,Internship_id):
    state = False
    internship = get_object_or_404(Internship, pk=Internship_id)
    
    subject = internship.subject

    handle_Scrapping(subject, Internship_id)
    state = True
    
    return Response({'state': state})




# <<<<<<< HEAD
import os
@api_view(['GET'])
def code_outlook(request, Internship_id):
    # json_file_path = r'C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project/user_code.json'
    # json_file_path = r'F:/myApp/ATS_PROJECT/ATS_Project/user_code.json'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(base_dir,  'user_code.json')
# =======
# # @api_view(['GET'])
# # def code_outlook(request, Internship_id):
# #     json_file_path = r'C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project/user_code.json'
# #      # Construct the relative path

# #     try:
# #         with open(json_file_path, 'r') as file:
# #             data = json.load(file)
# #             user_code_key = f'user_code_{Internship_id}'
# #             user_code = data.get(user_code_key)
# #             if user_code:
# #                 return Response({'user_code': user_code})
# #             else:
# #                 return Response({'error': f'User code for Internship ID {Internship_id} not found'}, status=404)
# #     except Exception as e:
# #         return Response({'error': str(e)}, status=500)
# @api_view(['GET'])
# def code_outlook(request, Internship_id):
#     # Construct the relative path
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     json_file_path = os.path.join(base_dir,  'user_code.json')

#     # Debugging: Print the constructed path
#     print(f"Constructed JSON file path: {json_file_path}")

# >>>>>>> d38f552fb8c65c9629d1ed5d94496992a304116b
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            user_code_key = f'user_code_{Internship_id}'
            user_code = data.get(user_code_key)
            if user_code:
                return Response({'user_code': user_code})
            else:
                return Response({'error': f'User code for Internship ID {Internship_id} not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# views.py
@csrf_exempt 
def send_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject', '')
            message = data.get('message', '')
            recipient = data.get('recipient', '')
            # my_mail = data.get('myMail', '')
            
            if not all([subject, message, recipient]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            print(subject,message,recipient)
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER, # From email
                [recipient],  # To email
                fail_silently=False,
            )
            return JsonResponse({'message': 'Email sent successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json


# @csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import json

# @api_view(['POST'])
# def create_linkedin_ugc_post(request):
#     if request.method == 'POST':
#         # Extract parameters from the POST request
#         text = request.data.get('text', '')
        
#         # Define the LinkedIn API endpoint
#         linkedin_api_url = 'https://api.linkedin.com/v2/ugcPosts'
        
#         # Retrieve access token from the request headers
#         # access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
#         access_token = 'AQUiUedUKoLj4s2P6_9G3Frpa0ufXLt08ozIgDVgXw9Na9Sh5yWyCWZ1xTJE8r2tZ6PI2-nja_1VGzDSgy7yz6K3Lb0lpEgXFq29r5HD0ShhoZ-84msv9a-m7RSYnlTsgiD3pv3UuHUcTX9NpVMdRRmQjsyGfuUpc7BIHyDMvt1gMCnAeO9Mg91hQYUIJfL70b-8_PzjWYEqFaYA4rTjOLCfZKZQ4yJXoSY3ZN9c2KQltrnThca0fw9y70k8yrdotIkZVMv2INDmIB3y0IfOBbXX080Wh0pjh_Ztlrchu8HqSva_Xi6AOsZxg6u892w8tQgU9UPnWGZuf4lDiwO0feUCsoExaQ'
        
#         # Check if access token is present
#         if not access_token:
#             return Response({'error': 'Access token missing in the request'}, status=401)
        
#         # Define the request headers with the access token
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }
        
#         # Define the payload for the POST request
#         payload = {
#             "author": "urn:li:person:AYQKWDWFIk",
#             "lifecycleState": "PUBLISHED",
#             "specificContent": {
#                 "com.linkedin.ugc.ShareContent": {
#                     "shareCommentary": {
#                         "text": text
#                     },
#                     "shareMediaCategory": "NONE"   
#                 }
#             },
#             "visibility": {
#                 "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
#             }
#         }
        
#         # Send POST request to LinkedIn API
#         response = requests.post(linkedin_api_url, headers=headers, data=json.dumps(payload))
        
#         # Check if the request was successful
#         if response.status_code == 201:
#             return Response({'message': 'UGC post created successfully'}, status=201)
#         else:
#             return Response({'error': 'Failed to create UGC post'}, status=response.status_code)
#     else:
#         return Response({'error': 'Only POST requests are allowed'}, status=405)



# @api_view(['POST'])
# def create_linkedin_ugc_post(request):
#     if request.method == 'POST':
#         # Extract parameters from the POST request
#         text = request.data.get('text', '').strip()
        
#         # Check if text is not empty
#         if not text:
#             return Response({'error': 'Text field is required'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
#         # Define the LinkedIn API endpoint
#         linkedin_api_url = 'https://api.linkedin.com/v2/ugcPosts'
        
#         access_token = 'AQUiUedUKoLj4s2P6_9G3Frpa0ufXLt08ozIgDVgXw9Na9Sh5yWyCWZ1xTJE8r2tZ6PI2-nja_1VGzDSgy7yz6K3Lb0lpEgXFq29r5HD0ShhoZ-84msv9a-m7RSYnlTsgiD3pv3UuHUcTX9NpVMdRRmQjsyGfuUpc7BIHyDMvt1gMCnAeO9Mg91hQYUIJfL70b-8_PzjWYEqFaYA4rTjOLCfZKZQ4yJXoSY3ZN9c2KQltrnThca0fw9y70k8yrdotIkZVMv2INDmIB3y0IfOBbXX080Wh0pjh_Ztlrchu8HqSva_Xi6AOsZxg6u892w8tQgU9UPnWGZuf4lDiwO0feUCsoExaQ'

#         # Check if access token is present
#         if not access_token:
#             return Response({'error': 'Access token missing in the request'}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Define the request headers with the access token
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }
        
#         # Define the payload for the POST request
#         payload = {
#             "author": "urn:li:person:NKKfxPSMpd",
#             "lifecycleState": "PUBLISHED",
#             "specificContent": {
#                 "com.linkedin.ugc.ShareContent": {
#                     "shareCommentary": {
#                         "text": text
#                     },
#                     "shareMediaCategory": "NONE"
#                 }
#             },
#             "visibility": {
#                 "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
#             }
#         }
        
#         try:
#             # Send POST request to LinkedIn API
#             response = requests.post(linkedin_api_url, headers=headers, data=json.dumps(payload))
            
#             # Check if the request was successful
#             if response.status_code == 201:
#                 return Response({'message': 'UGC post created successfully'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'Failed to create UGC post', 'details': response.json()}, status=response.status_code)
#         except requests.exceptions.RequestException as e:
#             # Handle exceptions
#             return Response({'error': 'An error occurred while creating the UGC post', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response({'error': 'Only POST requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests

@api_view(['POST'])
@authentication_classes([])  # This line disables authentication for this view
@permission_classes([AllowAny])  # This line allows any user to access this view
def create_linkedin_ugc_post(request):
    if request.method == 'POST':
        # Extract parameters from the POST request
        text = request.data.get('text', '').strip()
        linkedin_access_token = request.data.get('access_token', '')
       
        # Check if text and access_token are not empty
        if not text or not linkedin_access_token:
            return Response({'error': 'Text and access_token are required'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
       
        # Define the LinkedIn API endpoint
        linkedin_api_url = 'https://api.linkedin.com/v2/ugcPosts'
       
        # Define the request headers with the access token
        headers = {
            'Authorization': f'Bearer {linkedin_access_token}',
            'Content-Type': 'application/json'
        }
       
        # Define the payload for the POST request
        payload = {
            "author": "urn:li:person:NKKfxPSMpd",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
       
        try:
            # Send POST request to LinkedIn API
            response = requests.post(linkedin_api_url, headers=headers, json=payload)
           
            # Check if the request was successful
            if response.status_code == 201:
                return Response({'message': 'UGC post created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to create UGC post', 'details': response.json()}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            # Handle exceptions
            return Response({'error': 'An error occurred while creating the UGC post', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Only POST requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
import os
from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Intern

@require_GET
@csrf_exempt
def get_intern_cv(request, file_path):
    try:
        # Decode the file path
        file_path = file_path.replace('|', '\\')
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file and create a FileResponse
            cv_file = open(file_path, 'rb')
            response = FileResponse(cv_file)
            
            # Set the content type and attachment filename
            file_name = os.path.basename(file_path)
            response['Content-Type'] = 'application/pdf'  # Adjust if not always PDF
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            
            return response
        else:
            return JsonResponse({'error': 'CV file not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)