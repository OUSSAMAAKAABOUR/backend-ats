from rest_framework import serializers
from ..authentication.models import Application

class AppliccationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'post', 'candidate', 'status', 'resume', 'cover_letter', 'date']
        read_only_fields = ['id', 'candidate', 'date']

    def create(self, validated_data):
        request = self.context.get('request')
        candidate = request.user if request else None
        validated_data['candidate'] = candidate
        return super().create(validated_data)
    
