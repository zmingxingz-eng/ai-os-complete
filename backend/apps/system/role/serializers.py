from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import GroupProfile

class RoleSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="profile.code")
    description = serializers.CharField(source="profile.description", allow_blank=True, required=False)
    is_active = serializers.BooleanField(source="profile.is_active", required=False)

    class Meta:
        model = Group
        fields = ["id", "name", "code", "description", "is_active"]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        group = Group.objects.create(name=validated_data["name"])
        GroupProfile.objects.create(
            group=group,
            code=profile_data["code"],
            description=profile_data.get("description", ""),
            is_active=profile_data.get("is_active", True),
        )
        return group

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        profile, _ = GroupProfile.objects.get_or_create(
            group=instance,
            defaults={"code": profile_data.get("code", f"group_{instance.id}")}
        )
        if "code" in profile_data:
            profile.code = profile_data["code"]
        if "description" in profile_data:
            profile.description = profile_data["description"]
        if "is_active" in profile_data:
            profile.is_active = profile_data["is_active"]
        profile.save()
        return instance
