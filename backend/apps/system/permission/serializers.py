from django.contrib.auth.models import Permission
from rest_framework import serializers
from apps.system.menu.models import Menu
from .models import MenuPermission

class PermissionSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), write_only=True, required=False, allow_null=True)
    perm_type = serializers.ChoiceField(choices=MenuPermission.TYPE_CHOICES, write_only=True, required=False, default="button")
    description = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")
    app_label = serializers.CharField(source="content_type.app_label", read_only=True)
    model = serializers.CharField(source="content_type.model", read_only=True)
    code = serializers.SerializerMethodField()
    menu_name = serializers.SerializerMethodField()
    menu_ids = serializers.SerializerMethodField()
    binding_type = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = [
            "id", "name", "codename", "content_type", "app_label", "model",
            "code", "menu", "menu_name", "menu_ids", "binding_type", "perm_type", "description",
        ]

    def create(self, validated_data):
        menu = validated_data.pop("menu", None)
        perm_type = validated_data.pop("perm_type", "button")
        description = validated_data.pop("description", "")
        permission = Permission.objects.create(**validated_data)
        if menu:
            MenuPermission.objects.create(
                menu=menu,
                permission=permission,
                perm_type=perm_type,
                description=description,
            )
        return permission

    def update(self, instance, validated_data):
        menu = validated_data.pop("menu", None) if "menu" in validated_data else serializers.empty
        perm_type = validated_data.pop("perm_type", "button")
        description = validated_data.pop("description", "")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if menu is not serializers.empty:
            instance.menu_bindings.all().delete()
            if menu:
                MenuPermission.objects.create(
                    menu=menu,
                    permission=instance,
                    perm_type=perm_type,
                    description=description,
                )
        return instance

    def get_code(self, obj):
        return f"{obj.content_type.app_label}.{obj.codename}"

    def get_menu_name(self, obj):
        binding = obj.menu_bindings.select_related("menu").order_by("sort", "id").first()
        return binding.menu.name if binding else ""

    def get_menu_ids(self, obj):
        return list(obj.menu_bindings.values_list("menu_id", flat=True))

    def get_binding_type(self, obj):
        binding = obj.menu_bindings.order_by("sort", "id").first()
        return binding.perm_type if binding else ""


class MenuPermissionSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)
    permission_code = serializers.SerializerMethodField()

    class Meta:
        model = MenuPermission
        fields = [
            "id", "menu", "menu_name", "permission", "permission_name",
            "permission_code", "perm_type", "sort", "description",
        ]

    def get_permission_code(self, obj):
        return f"{obj.permission.content_type.app_label}.{obj.permission.codename}"
