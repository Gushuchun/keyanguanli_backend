from ..models import UserSettings
from utils.base.baseView import BaseModelViewSet
from ..serializers import UserSettingsSerializer

class UserSettingsViewSet(BaseModelViewSet):
    queryset = UserSettings.objects.filter(state=1)
    serializer_class = UserSettingsSerializer

    def list(self, request, *args, **kwargs):
        user_settings = self.get_queryset().filter(username=request.user.username)
        serializer = self.get_serializer(user_settings, many=True)
        return self.success_response(serializer.data)

    def update(self, request, *args, **kwargs):
        """处理部分更新"""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.success_response(serializer.data)
