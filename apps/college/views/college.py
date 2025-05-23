from apps.college.models import College
from apps.college.serializers.college import CollegeDetailSerializer, CollegeBasicSerializer
from rest_framework.decorators import action
from utils.base.baseView import BaseModelViewSet
class CollegeViewSet(BaseModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeBasicSerializer

    def list(self, request, *args, **kwargs):
        colleges = self.get_queryset()
        serializer = CollegeDetailSerializer(colleges, many=True)
        return self.success_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='public')
    def public(self, request, *args, **kwargs):
        colleges = self.get_queryset()
        serializer = self.get_serializer(colleges, many=True)
        return self.success_response(serializer.data)