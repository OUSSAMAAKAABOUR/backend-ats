from rest_framework import status
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post
from .serializers import PostSerializer, PostSerializer2
from rest_framework.authentication import SessionAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from authentication.models import Candidate, Recruiter
from authentication.serializers import CandidateSerializer



@permission_classes([IsAuthenticated])  

# @api_view(['POST'])
# def create_post(request):
#     serializer = PostSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def create_post(request):
    serializer = PostSerializer2(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5  # Number of posts per page
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def list_posts(request):
    paginator = CustomPagination()
    posts = Post.objects.all()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def list_posts_by_recruiter(request, recruiter_id):
    posts = Post.objects.filter(recruiter_id=recruiter_id)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
# Read details of a specific post
@api_view(['GET'])
def retrieve_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    serializer = PostSerializer(post)
    return Response(serializer.data)

# Update an existing post
@api_view(['PUT'])
def update_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    serializer = PostSerializer(post, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete an existing post
@api_view(['DELETE'])
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Find candidates by its post
@api_view(['GET'])
def findCandidate(request, post_id):
    try:
        post = get_object_or_404(Post, pk=post_id)
        candidates = Candidate.objects.filter(applications__post=post)
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
 
# #######################################################################

#Dependency for the Search post view
from fuzzywuzzy import process
def find_closest_match(query, choices):
    return process.extract(query, choices, limit=100)
	

@api_view(['GET'])
def search_recommendation(request):
    if request.method == 'GET':
        title = request.query_params.get('title', '')
        localisation = request.query_params.get('localisation', '')

        # Use find_closest_match to get similar titles and localisations
        titles = Post.objects.values_list('title', flat=True)
        localisations = Post.objects.values_list('localisation', flat=True)

        closest_matches_title = find_closest_match(title, titles)
        closest_matches_localisations = find_closest_match(localisation, localisations)

        # Extract the matched titles and localisations
        matched_titles = [match[0] for match in closest_matches_title]
        matched_localisations = [match[0] for match in closest_matches_localisations]

        # Query the Post model for posts based on matched titles and localisations
        if title and localisation:
            posts = Post.objects.filter(title__in=matched_titles, localisation__in=matched_localisations)
        elif title:
            posts = Post.objects.filter(title__in=matched_titles)
        elif localisation:
            posts = Post.objects.filter(localisation__in=matched_localisations)
        else:
            posts = Post.objects.none()

        # Create a dictionary to hold the posts and their similarity scores
        classified_posts = []

        # Iterate over the posts to calculate and store their similarity scores for both title and localisation
        for post in posts:
            title_similarity = process.extractOne(title, [post.title])[1] if title else 0
            localisation_similarity = process.extractOne(localisation, [post.localisation])[1] if localisation else 0

            # Add the post if the title and/or localisation similarity is above the threshold
            if (title and localisation and title_similarity >= 50 and localisation_similarity >= 80) or \
               (title and not localisation and title_similarity >= 50) or \
               (localisation and not title and localisation_similarity >= 80):
                classified_posts.append({
                    'post': PostSerializer(post).data,
                    'title_similarity': title_similarity,
                    'localisation_similarity': localisation_similarity
                })

        # Sort the classified posts by title similarity and localisation similarity
        sorted_classified_posts = sorted(classified_posts, key=lambda x: (x['title_similarity'], x['localisation_similarity']), reverse=True)

        # Check if there are no posts with both title and localisation similarity > 50
        if not sorted_classified_posts:
            if localisation and not title:
                return Response({
                    'message': f'La recherche Emploie à {localisation} ne donne aucun résultat. Vérifiez l’orthographe ou essayez d’autres mots clés.',
                    'posts': []
                })
            elif title and not localisation:
                return Response({
                    'message': f'La recherche {title} ne donne aucun résultat. Vérifiez l’orthographe ou essayez d’autres mots clés.',
                    'posts': []
                })
            elif title and localisation:
                return Response({
                    'message': f'La recherche {title} à {localisation} ne donne aucun résultat. Vérifiez l’orthographe ou essayez d’autres mots clés.',
                    'posts': []
                })

        return Response({'posts': sorted_classified_posts})
    else:
        return Response({'error': 'Method not allowed'}, status=405)
