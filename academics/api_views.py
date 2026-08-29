from rest_framework.generics import ListCreateAPIView
from .models import Department
from .serializers import DepartmentSerializer

class DepartmentListCreateAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer