from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from authentication.models import Candidate,Application, SavedPost
from authentication.serializers import CandidateSerializer,ApplicationSerializer,ApplicationSerializer2, ApplicationSerializer3, SavedPostSerializer
from rest_framework import status
from posts.models import Post
from posts.views import retrieve_post

# Create a new candidate

@api_view(['POST'])
def create_candidate(request):
    serializer = CandidateSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data.get('email')

        # Check if user already exists
        if Candidate.objects.filter(username=username).exists():
            return Response({'error': 'Candidate with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Creating a new user with encrypted password
        user =Candidate.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active=True
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List all candidates
@api_view(['GET'])
def list_candidates(request):
    candidates = Candidate.objects.all()
    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data)

# Read details of a specific candidate
@api_view(['GET'])
def retrieve_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    serializer = CandidateSerializer(candidate)
    return Response(serializer.data)

# Update an existing candidate
@api_view(['PATCH'])
def update_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    serializer = CandidateSerializer(candidate, data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete an existing candidate
@api_view(['DELETE'])
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    candidate.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
def apply_for_job(request):
    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():

        candidate_object = serializer.validated_data['candidate'] #here we return un object not just geting the id
        post_object = serializer.validated_data['post']


        # Accessing IDs from candidate and post objects
        candidate_id = candidate_object.id
        post_id = post_object.id

        try:
            # Retrieve candidate and post objects based on the provided IDs
            candidate = Candidate.objects.get(pk=candidate_id)
            post = Post.objects.get(pk=post_id)

            application_status = serializer.validated_data.get('status')
            additional_documents = serializer.validated_data.get('additional_documents')

            # Check if the candidate has already applied to this post
            if Application.objects.filter(post=post, candidate=candidate).exists():
                return Response({'message': 'You have already applied to this offer'}, status=status.HTTP_409_CONFLICT)

            # Create a new application if the candidate hasn't already applied
            Application.objects.create(post=post, candidate=candidate, status=application_status, additional_documents=additional_documents)
            return Response({'message': 'Application submitted successfully'}, status=status.HTTP_201_CREATED)

        except Candidate.DoesNotExist:
            return Response({'message': 'Candidate does not exist'}, status=status.HTTP_404_NOT_FOUND)

        except Post.DoesNotExist:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List applied posts
@api_view(['GET'])
def list_applied_posts(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    applied_posts = Application.objects.filter(candidate=candidate)
    serializer = ApplicationSerializer2(applied_posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Saved posts
@api_view(['POST'])
def save_post(request, candidate_id, post_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if the post is already saved
    saved_post = SavedPost.objects.filter(candidate=candidate, post=post).first()
    if saved_post:
        saved_post.delete()
        return Response({'message': 'Post unsaved successfully.'}, status=status.HTTP_200_OK)

    saved_post = SavedPost(candidate=candidate, post=post)
    saved_post.save()
    
    return Response({'message': 'Post saved successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def list_saved_posts(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    saved_posts = SavedPost.objects.filter(candidate=candidate)
    serializer = SavedPostSerializer(saved_posts, many=True)
    return Response(serializer.data)



# from rest_framework.parsers import MultiPartParser, FormParser

# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def apply_for_job(request):
#     serializer = ApplicationSerializer(data=request.data)
#     if serializer.is_valid():

#         candidate_object = serializer.validated_data['candidate']
#         post_object = serializer.validated_data['post']

#         # Accessing IDs from candidate and post objects
#         candidate_id = candidate_object.id
#         post_id = post_object.id

#         try:
#             # Retrieve candidate and post objects based on the provided IDs
#             candidate = Candidate.objects.get(pk=candidate_id)
#             post = Post.objects.get(pk=post_id)

#             application_status = serializer.validated_data.get('status')

#             # Check if the candidate has already applied to this post
#             if Application.objects.filter(post=post, candidate=candidate).exists():
#                 return Response({'message': 'You have already applied to this offer'}, status=status.HTTP_409_CONFLICT)

#             # Get additional documents from request data
#             additional_documents = request.FILES.getlist('additional_documents')

#             # Create a new application if the candidate hasn't already applied
#             application = Application.objects.create(
#                 post=post,
#                 candidate=candidate,
#                 status=application_status
#             )

#             # Save additional documents associated with the application
#             for document in additional_documents:
#                 ApplicationDocument.objects.create(application=application, document=document)

#             return Response({'message': 'Application submitted successfully'}, status=status.HTTP_201_CREATED)

#         except Candidate.DoesNotExist:
#             return Response({'message': 'Candidate does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         except Post.DoesNotExist:
#             return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def create_application(request):
#     serializer = ApplicationSerializer(data=request.data, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @permission_classes([IsAuthenticated])

#############################################################################################
import sys
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
matching_path = os.path.join(base_dir, 'candidates', 'matching_service')
# Debugging: Print the constructed path
print(f"Constructed Scrapping Service path: {matching_path}")
sys.path.append(matching_path)

# sys.path.append('C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project/candidates/matching_service')

from main import matching

# @api_view(['POST'])
# def create_application(request):
#     serializer = ApplicationSerializer(data=request.data, context={'request': request})
#     if serializer.is_valid():
#         application = serializer.save()
#         print('well saving !!!')


#         # Get the resume path and post description
#         resume_path = application.resume.path if application.resume else None
#         post_description = application.post.description
#         print('here is the path: ',resume_path)
#         # Call the matching function
#         score = matching(resume_path, post_description)
        
#         # Update the score_matching field
#         application.score_matching = score
#         application.save()

#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from authentication.serializers import PostSerializer

from fuzzywuzzy import process

@api_view(['GET'])
def get_similar_posts(request, candidate_id):
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
        applications = Application.objects.filter(candidate=candidate)

        if not applications.exists():
            return Response({"detail": "No applied posts found for this candidate."}, status=status.HTTP_404_NOT_FOUND)

        # Get the last applied application based on the application number
        last_application = applications.order_by('-id').first()
        last_applied_post = last_application.post if last_application else None

        if not last_applied_post:
            return Response({"detail": "No last applied post found for this candidate."}, status=status.HTTP_404_NOT_FOUND)

        print(f"Last applied post: {last_applied_post}")

        # dd fuzzy matching to find similar posts based on title
        posts = Post.objects.exclude(pk=last_applied_post.pk)

        # Extract all post titles for matching
        post_titles = [post.title for post in posts]

        # Find closest matches based on the title of the last applied post
        closest_matches = process.extract(last_applied_post.title, post_titles, limit=3)

        # Get the actual post instances from the closest matches
        similar_posts_titles = [match[0] for match in closest_matches]
        similar_posts = Post.objects.filter(title__in=similar_posts_titles)[:3]

        # Serialize the similar posts
        serializer = PostSerializer(similar_posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Candidate.DoesNotExist:
        return Response({"detail": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def create_application(request):
    serializer = ApplicationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        application = serializer.save()
        print('Application saved successfully!')

        post_description = application.post.description

        resume_path = application.get_resume_path()

        if resume_path:
            try:
                # Check if the file exists
                if not os.path.exists(resume_path):
                    raise FileNotFoundError(f"Resume file not found: {resume_path}")
                
                # Assuming your matching function can handle file paths
                score = matching(resume_path, post_description)
            except Exception as e:
                print(f"Error processing resume: {str(e)}")
                score = -1
        else:
            score = 0

        # Update the score_matching field
        application.score_matching = score
        application.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_applications_by_post_id(request, post_id):
    try:
        # Filter applications by post ID
        applications = Application.objects.filter(post_id=post_id).order_by('-score_matching')
        
        # Serialize the filtered applications
        serializer = ApplicationSerializer3(applications, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Application.DoesNotExist:
        return Response({'error': 'No applications found for this post ID!!.'}, status=status.HTTP_404_NOT_FOUND)









