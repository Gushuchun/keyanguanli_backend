from rest_framework import serializers
from apps.college.models import College

class CollegeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['id', 'name', 'prize_num', 'paper_num', 'patent_num']

class CollegeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['id', 'name']