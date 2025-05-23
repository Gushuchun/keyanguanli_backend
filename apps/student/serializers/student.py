# serializers.py
from rest_framework import serializers
from apps.student.models import Student


class StudentListSerializer(serializers.ModelSerializer):
    college = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'username', 'sn', 'college', 'phone', 'avatar']
        read_only_fields = fields  # 所有字段均为只读

    def get_college(self, obj):
        """处理学院信息的序列化"""
        return obj.get_college(obj.college_id)