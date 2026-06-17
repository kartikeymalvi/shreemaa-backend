from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
class CreateUserByAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Strict Security check: Sirf logged-in admin accounts generate kar sakta hai
        if request.user.role != 'ADMIN':
            return Response({"error": "Unauthorized: Only administrators can create new system accounts."}, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role') # Expected: 'ADMIN' or 'USER'
        email = request.data.get('email', '')

        if not username or not password or not role:
            return Response({"error": "Missing inputs. Username, password and role are mandatory fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username already registered in MySQL
        if CustomUser.objects.filter(username=username).exists():
            return Response({"error": "Conflict: Username already registered in database."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Secure password hashing integration using Django core identity system
            user = CustomUser.objects.create_user(username=username, password=password, email=email, role=role)
            return Response({"message": f"Account for '{username}' as [{role}] successfully deployed into system!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  


# Ek chota serializer jo User ka data JSON me convert karega
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']

# 1. Saare Users ki list nikalne ke liye API
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Security: Sirf ADMIN hi list dekh sakta hai
        if self.request.user.role != 'ADMIN':
            return CustomUser.objects.none()
        return super().get_queryset()

# 2. User ko delete karne ke liye API
class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Access Denied: Only admins can delete users.")
        if instance.id == self.request.user.id:
            raise PermissionDenied("You cannot delete your own admin account!")
        instance.delete()        