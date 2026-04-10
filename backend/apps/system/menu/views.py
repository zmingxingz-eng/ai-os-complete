from rest_framework import viewsets
from .models import Menu
from .serializers import MenuSerializer

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.select_related("parent").all().order_by("sort", "id")
    serializer_class = MenuSerializer
