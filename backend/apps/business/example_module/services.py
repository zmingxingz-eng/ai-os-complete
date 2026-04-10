from .models import Notice

class NoticeService:
    @staticmethod
    def list_all():
        return Notice.objects.all()
