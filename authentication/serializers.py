from rest_framework import serializers

from posts.serializers import PostSerializer
from .models import User, Candidate,Event,Application,Recruiter,Post, SavedPost

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False) 
    
    class Meta:
        model = User
        fields = '__all__'

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role

        return token



from rest_framework import serializers
from .models import Candidate, Event

class CandidateSerializer(serializers.ModelSerializer):
     
     class Meta:
         model = Candidate
         fields = '__all__'
     def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "Candidate"

class RecruiterSerializer(serializers.ModelSerializer):
     class Meta:
         model = Recruiter
         fields = '__all__'

# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = '__all__'

class ApplicationStepUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['step']

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

    def validate(self, data):
        if not data.get('resume') and not data.get('resume_path'):
            raise serializers.ValidationError("Either resume or resume_path must be provided")
        return data
    
class ApplicationSerializer2(serializers.ModelSerializer):
    post = PostSerializer() #but if you want to create a post you need comment this line to avoid given all the post object as a parameter
    class Meta:
         model = Application
         fields = '__all__'

class ApplicationSerializer3(serializers.ModelSerializer):
    candidate = CandidateSerializer() #but if you want to create a post you need comment this line to avoid given all the post object as a parameter

    class Meta:
         model = Application
         fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    candidate_id = serializers.PrimaryKeyRelatedField(
        source='candidate',
        queryset=Candidate.objects.all(),
        write_only=True
    )
    candidate = CandidateSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'recruiter', 'candidate_id', 'candidate', 'event_title', 'event_start_date']

from .models import Post

# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = '__all__'

# Saved posts Serializer class serializers.py file, authentification app
class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer()  # Serializer for nested Post data
    class Meta:
        model = SavedPost
        fields = '__all__'


# chatt
from .models import Message, UserStatus, Clients

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'  # Note the double underscores

class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'  # Note the double underscores

class ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'  # Note the double underscores
        