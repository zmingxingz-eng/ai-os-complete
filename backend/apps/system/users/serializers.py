from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.system.organization.models import Organization, Position, UserOrganizationRelation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    organization_id = serializers.PrimaryKeyRelatedField(
        source="organization_binding",
        queryset=Organization.objects.filter(is_active=True),
        write_only=True,
        required=True,
    )
    position_id = serializers.PrimaryKeyRelatedField(
        source="position_binding",
        queryset=Position.objects.filter(status="active", is_active=True),
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "full_name",
            "mobile",
            "organization",
            "organization_name",
            "position",
            "position_name",
            "organization_id",
            "position_id",
            "password",
        ]

    def _get_primary_relation(self, obj):
        prefetched = getattr(obj, "_prefetched_objects_cache", {})
        relations = prefetched.get("organization_relations")
        if relations is not None:
            for relation in relations:
                if relation.relation_type == "primary" and relation.status == "active":
                    return relation
            return None
        return (
            UserOrganizationRelation.objects.select_related("organization", "position")
            .filter(user=obj, relation_type="primary", status="active")
            .first()
        )

    def _sync_primary_relation(self, user, organization, position):
        current_primary = (
            UserOrganizationRelation.objects.select_related("organization", "position")
            .filter(user=user, relation_type="primary")
            .first()
        )
        target_relation = UserOrganizationRelation.objects.filter(user=user, organization=organization).first()

        if current_primary and (target_relation is None or current_primary.pk != target_relation.pk):
            current_primary.relation_type = "part_time"
            current_primary.save(update_fields=["relation_type", "updated_at"])

        if target_relation:
            target_relation.position = position
            target_relation.relation_type = "primary"
            target_relation.status = "active"
            target_relation.save(update_fields=["position", "relation_type", "status", "updated_at"])
        else:
            UserOrganizationRelation.objects.create(
                user=user,
                organization=organization,
                position=position,
                relation_type="primary",
                duty="",
                status="active",
            )

        user.organization = organization
        user.position_name = position.name
        user.save(update_fields=["organization", "position_name"])

    def get_organization(self, obj):
        relation = self._get_primary_relation(obj)
        if relation and relation.organization_id:
            return relation.organization_id
        return getattr(obj, "organization_id", None)

    def get_organization_name(self, obj):
        relation = self._get_primary_relation(obj)
        if relation and relation.organization:
            return relation.organization.name
        return getattr(getattr(obj, "organization", None), "name", "")

    def get_position(self, obj):
        relation = self._get_primary_relation(obj)
        if relation and relation.position_id:
            return relation.position_id
        return None

    def get_position_name(self, obj):
        relation = self._get_primary_relation(obj)
        if relation and relation.position:
            return relation.position.name
        return getattr(obj, "position_name", "")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        organization = validated_data.pop("organization_binding")
        position = validated_data.pop("position_binding")
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        self._sync_primary_relation(user, organization, position)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        organization = validated_data.pop("organization_binding")
        position = validated_data.pop("position_binding")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        self._sync_primary_relation(instance, organization, position)
        return instance
