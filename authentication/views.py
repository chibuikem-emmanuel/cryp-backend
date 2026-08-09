from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import AdminRegistrationSerializer, AdminLoginSerializer

class RegisterAdminView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Admin user registered successfully.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "is_staff": user.is_staff
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)