from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GetPublicKey(APIView):
    def get(self, request):
        from utils.keys.rsa_crypt import read_public_key
        public_key = read_public_key()
        return Response({
            'code': 200,
            'public_key': public_key
        }, status=status.HTTP_200_OK)
