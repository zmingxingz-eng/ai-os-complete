from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Menu

class MenuSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    content_type_label = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id", "name", "code", "path", "component", "menu_type", "icon",
            "visible", "parent", "parent_name", "sort", "content_type",
            "content_type_label", "children", "is_active", "created_at", "updated_at",
        ]

    def get_content_type_label(self, obj):
        if not obj.content_type_id:
            return ""
        return f"{obj.content_type.app_label}.{obj.content_type.model}"

    def get_children(self, obj):
        if self.context.get("nested"):
            return []
        children = getattr(obj, "children", None)
        if children is None:
            children = obj.children.filter(is_active=True).order_by("sort", "id")
        return MenuSerializer(children, many=True, context={"nested": True}).data
