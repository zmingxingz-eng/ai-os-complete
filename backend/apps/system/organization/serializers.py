from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Organization, Position, UserOrganizationRelation

User = get_user_model()


def _sync_status_fields(validated_data):
    status = validated_data.get("status")
    is_active = validated_data.get("is_active")
    if status is None and is_active is not None:
        validated_data["status"] = "active" if is_active else "disabled"
    elif status is not None and is_active is None:
        validated_data["is_active"] = status == "active"
    elif status is not None and is_active is not None:
        validated_data["is_active"] = status == "active"
    return validated_data


def _update_organization_tree(node: Organization):
    parent = node.parent
    if parent:
        node.level = parent.level + 1
        node.path = f"{parent.path}{node.id}/"
        node.path_name = f"{parent.path_name}{node.name}/"
    else:
        node.level = 1
        node.path = f"{node.id}/"
        node.path_name = f"{node.name}/"
    Organization.objects.filter(pk=node.pk).update(
        level=node.level,
        path=node.path,
        path_name=node.path_name,
    )
    for child in Organization.objects.filter(parent=node).order_by("sort", "id"):
        _update_organization_tree(child)


class OrganizationSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    leader_name = serializers.CharField(source="leader.full_name", read_only=True)

    class Meta:
        model = Organization
        fields = "__all__"

    def validate_parent(self, parent):
        instance = getattr(self, "instance", None)
        if instance is None or parent is None:
            return parent
        if parent.pk == instance.pk:
            raise serializers.ValidationError("上级组织不能选择当前组织。")
        instance_path = instance.path or f"{instance.pk}/"
        if parent.path and parent.path.startswith(instance_path):
            raise serializers.ValidationError("不能将组织移动到自己的下级组织下。")
        return parent

    def create(self, validated_data):
        validated_data = _sync_status_fields(validated_data)
        instance = super().create(validated_data)
        _update_organization_tree(instance)
        instance.refresh_from_db()
        return instance

    def update(self, instance, validated_data):
        validated_data = _sync_status_fields(validated_data)
        instance = super().update(instance, validated_data)
        _update_organization_tree(instance)
        instance.refresh_from_db()
        return instance


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

    def validate(self, attrs):
        attrs = _sync_status_fields(attrs)
        return super().validate(attrs)


class UserOrganizationRelationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    position_name = serializers.CharField(source="position.name", read_only=True)

    class Meta:
        model = UserOrganizationRelation
        fields = [
            "id",
            "user",
            "username",
            "user_full_name",
            "organization",
            "organization_name",
            "position",
            "position_name",
            "relation_type",
            "duty",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        user = attrs.get("user") or getattr(instance, "user", None)
        organization = attrs.get("organization") or getattr(instance, "organization", None)
        position = attrs.get("position") or getattr(instance, "position", None)
        if user and organization:
            qs = UserOrganizationRelation.objects.filter(user=user, organization=organization)
            if instance is not None:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError("同一用户在同一组织下只能保留一条关系记录。")
        if position is None:
            raise serializers.ValidationError({"position": "请选择任职岗位。"})
        attrs["status"] = attrs.get("status", getattr(instance, "status", "active"))
        return attrs

    def _sync_primary_relation(self, relation):
        if relation.relation_type == "primary":
            UserOrganizationRelation.objects.filter(
                user=relation.user,
                relation_type="primary",
            ).exclude(pk=relation.pk).update(relation_type="part_time")

    def _sync_user_cache(self, relation):
        primary_relation = (
            UserOrganizationRelation.objects.select_related("organization", "position")
            .filter(user=relation.user, relation_type="primary", status="active")
            .first()
        )
        relation.user.organization = primary_relation.organization if primary_relation else None
        relation.user.position_name = primary_relation.position.name if primary_relation and primary_relation.position else ""
        relation.user.save(update_fields=["organization", "position_name"])

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._sync_primary_relation(instance)
        self._sync_user_cache(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._sync_primary_relation(instance)
        self._sync_user_cache(instance)
        return instance
