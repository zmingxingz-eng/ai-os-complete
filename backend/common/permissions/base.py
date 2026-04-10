from rest_framework.permissions import IsAuthenticated

class DefaultPermission(IsAuthenticated):
    pass
