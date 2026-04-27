from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from core.models import playto_user


class BaseAPIView(APIView):
    request_serializer_class = None

    def get_validated_data(self, request):
        serializer = self.request_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_user_obj(self, validated_data):
        pt_id = validated_data.get("pt_id")

        user = playto_user.objects.filter(pt_id=pt_id).first()

        if not user:
            raise NotFound("User not found")

        return user