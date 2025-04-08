from rest_framework import serializers
from apps.teacher.models import Teacher
import logging

logger = logging.getLogger('student')

class TeacherInfoSerializer(serializers.ModelSerializer):


    class Meta:
        model = Teacher
        fields = [
            'id', 'username', 'email',
            'gender', 'phone', 'college_id'
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'id': {'read_only': True},
            'college_id': {'read_only': True},
        }