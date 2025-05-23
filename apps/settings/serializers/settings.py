from rest_framework import serializers
from ..models import UserSettings


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['username', 'sn', 'send_email', 'cursor', 'id']
