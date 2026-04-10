from .models import Organization

class OrganizationService:
    @staticmethod
    def list_all():
        return Organization.objects.select_related("parent").all()
