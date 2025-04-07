from rest_framework import serializers
from apps.student.models import Student

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'gender', 'phone', 'cn', 'prize_num', 'race_num', 'team_id', 'is_cap', 'college_id']
