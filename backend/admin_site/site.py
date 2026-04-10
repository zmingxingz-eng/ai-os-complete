from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "AI OS 2.0 管理后台"
    site_title = "AI OS 2.0"
    index_title = "系统维护"

custom_admin_site = CustomAdminSite(name="custom_admin")
