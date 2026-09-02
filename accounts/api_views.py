from rest_framework.viewsets import ModelViewSet

from .models import User
from .permissions import IsAdminRole
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['username', 'email', 'role']
    ordering_fields = ['username', 'id']
