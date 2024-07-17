from rest_framework import serializers

from recruiters.serializers import RecruiterSerializer

from .models import Post

class PostSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(read_only=True)
    salary = serializers.CharField(write_only=True, required=False) 
    number_of_people_to_hire = serializers.CharField(write_only=True, required=False) 
    localisation = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Post
        fields = '__all__'
class PostSerializer2(serializers.ModelSerializer):
    salary = serializers.CharField(write_only=True, required=False) 
    number_of_people_to_hire = serializers.CharField(write_only=True, required=False) 
    localisation = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Post
        fields = '__all__'

