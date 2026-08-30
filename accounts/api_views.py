from rest_framework.generics import ListCreateAPIView
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminRole

class UserListCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]