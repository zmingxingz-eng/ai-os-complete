import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from apps.system.organization.models import Organization, Position, UserOrganizationRelation
from apps.system.role.models import GroupProfile
from apps.system.permission.models import MenuPermission
from apps.system.menu.models import Menu
from apps.system.rbac.models import GroupMenu, GroupDataScope

User = get_user_model()


def ensure_permission(model, codename, name):
    permission_ct = ContentType.objects.get_for_model(model)
    permission, _ = Permission.objects.get_or_create(
        content_type=permission_ct,
        codename=codename,
        defaults={"name": name}
    )
    permission.name = name
    permission.save(update_fields=["name"])
    return permission


def ensure_menu_permission(menu, permission, perm_type, description):
    binding, _ = MenuPermission.objects.get_or_create(
        menu=menu,
        permission=permission,
        defaults={"perm_type": perm_type, "description": description},
    )
    binding.perm_type = perm_type
    binding.description = description
    binding.save(update_fields=["perm_type", "description"])
    return binding


def ensure_organization(**kwargs):
    defaults = kwargs.copy()
    code = defaults.pop("code")
    obj, _ = Organization.objects.get_or_create(code=code, defaults=defaults)
    for field, value in defaults.items():
        setattr(obj, field, value)
    obj.save()
    return obj


def sync_organization_tree(node):
    parent = node.parent
    if parent:
        node.level = parent.level + 1
        node.path = f"{parent.path}{node.id}/"
        node.path_name = f"{parent.path_name}{node.name}/"
    else:
        node.level = 1
        node.path = f"{node.id}/"
        node.path_name = f"{node.name}/"
    node.save(update_fields=["level", "path", "path_name"])
    for child in Organization.objects.filter(parent=node).order_by("sort", "id"):
        sync_organization_tree(child)


def ensure_position(**kwargs):
    defaults = kwargs.copy()
    code = defaults.pop("code")
    obj, _ = Position.objects.get_or_create(code=code, defaults=defaults)
    for field, value in defaults.items():
        setattr(obj, field, value)
    obj.save()
    return obj


def seed_menu_permissions(menu_map):
    permission_specs = [
        ("/system/users", User, [
            ("add_user", "鏂板鐢ㄦ埛", "button"),
            ("change_user", "缂栬緫鐢ㄦ埛", "button"),
            ("delete_user", "鍒犻櫎鐢ㄦ埛", "button"),
            ("view_user", "鏌ョ湅鐢ㄦ埛", "api"),
        ]),
        ("/system/organization", Organization, [
            ("add_organization", "鏂板缁勭粐", "button"),
            ("change_organization", "缂栬緫缁勭粐", "button"),
            ("delete_organization", "鍒犻櫎缁勭粐", "button"),
            ("view_organization", "鏌ョ湅缁勭粐", "api"),
        ]),
        ("/system/position", Position, [
            ("add_position", "鏂板宀椾綅", "button"),
            ("change_position", "缂栬緫宀椾綅", "button"),
            ("delete_position", "鍒犻櫎宀椾綅", "button"),
            ("view_position", "鏌ョ湅宀椾綅", "api"),
        ]),
        ("/system/role", Group, [
            ("add_group", "鏂板瑙掕壊", "button"),
            ("change_group", "缂栬緫瑙掕壊", "button"),
            ("delete_group", "鍒犻櫎瑙掕壊", "button"),
            ("view_group", "鏌ョ湅瑙掕壊", "api"),
        ]),
        ("/system/menu", Menu, [
            ("add_menu", "鏂板鑿滃崟", "button"),
            ("change_menu", "缂栬緫鑿滃崟", "button"),
            ("delete_menu", "鍒犻櫎鑿滃崟", "button"),
            ("view_menu", "鏌ョ湅鑿滃崟", "api"),
        ]),
        ("/system/menu", Permission, [
            ("add_permission", "鏂板鏉冮檺", "button"),
            ("change_permission", "缂栬緫鏉冮檺", "button"),
            ("delete_permission", "鍒犻櫎鏉冮檺", "button"),
            ("view_permission", "鏌ョ湅鏉冮檺", "api"),
        ]),
    ]

    permission_objs = []
    for menu_path, model, specs in permission_specs:
        menu = menu_map.get(menu_path)
        if not menu:
            continue
        for codename, name, perm_type in specs:
            permission = ensure_permission(model, codename, name)
            ensure_menu_permission(menu, permission, perm_type, name)
            permission_objs.append(permission)
    return permission_objs


def ensure_other_permission_menu(menu_map):
    parent = menu_map.get("/system")
    obj, _ = Menu.objects.get_or_create(
        code="system.other_permissions",
        defaults={
            "name": "鍏朵粬閰嶇疆鏉冮檺",
            "path": "",
            "component": "",
            "menu_type": "menu",
            "icon": "Setting",
            "parent": parent,
            "sort": 99,
            "visible": False,
        }
    )
    obj.name = "鍏朵粬閰嶇疆鏉冮檺"
    obj.menu_type = "menu"
    obj.icon = "Setting"
    obj.parent = parent
    obj.sort = 99
    obj.visible = False
    obj.save(update_fields=["name", "menu_type", "icon", "parent", "sort", "visible"])
    menu_map["__other_permissions__"] = obj
    return obj


def bind_remaining_permissions_to_other_menu(other_menu):
    allowed_app_labels = {"dictionary", "config_center", "audit_log"}
    for permission in Permission.objects.select_related("content_type").all():
        if MenuPermission.objects.filter(permission=permission).exists():
            continue
        if permission.content_type.app_label not in allowed_app_labels:
            continue
        perm_type = "api" if permission.codename.startswith("view_") else "button"
        ensure_menu_permission(other_menu, permission, perm_type, permission.name)


def cleanup_extension_permissions():
    technical_models = [GroupProfile, MenuPermission, GroupMenu, GroupDataScope, UserOrganizationRelation]
    technical_content_type_ids = [ContentType.objects.get_for_model(model).id for model in technical_models]
    Permission.objects.filter(content_type_id__in=technical_content_type_ids).delete()


def cleanup_unwanted_menu_bindings():
    allowed_app_labels = {"users", "organization", "auth", "menu", "dictionary", "config_center", "audit_log"}
    MenuPermission.objects.exclude(permission__content_type__app_label__in=allowed_app_labels).delete()
    user_org_relation_ct = ContentType.objects.get_for_model(UserOrganizationRelation)
    MenuPermission.objects.filter(permission__content_type=user_org_relation_ct).delete()

def main():
    root_org = ensure_organization(
        code="ROOT",
        name="鎬婚儴",
        org_kind="group",
        sort=1,
        status="active",
        is_active=True,
        is_temporary=False,
    )
    tech_org = ensure_organization(
        code="TECH",
        name="鎶€鏈儴",
        parent=root_org,
        org_kind="department",
        sort=2,
        status="active",
        is_active=True,
        is_temporary=False,
    )
    sync_organization_tree(root_org)

    admin_position = ensure_position(
        code="SYS_ADMIN",
        name="绯荤粺绠＄悊鍛?,
        category="绯荤粺绠＄悊",
        status="active",
        is_active=True,
        sort=1,
        remark="绯荤粺鍒濆鍖栭粯璁ゅ矖浣?,
    )
    ensure_position(
        code="DEV_ENGINEER",
        name="寮€鍙戝伐绋嬪笀",
        category="鐮斿彂",
        status="active",
        is_active=True,
        sort=2,
        remark="绯荤粺鍒濆鍖栭粯璁ゅ矖浣?,
    )

    admin_group, _ = Group.objects.get_or_create(
        name="绠＄悊鍛?
    )
    GroupProfile.objects.get_or_create(
        group=admin_group,
        defaults={"code": "admin", "description": "绯荤粺绠＄悊鍛?}
    )
    dev_group, _ = Group.objects.get_or_create(name="寮€鍙戜汉鍛?)
    GroupProfile.objects.get_or_create(
        group=dev_group,
        defaults={"code": "developer", "description": "寮€鍙戣鑹?}
    )

    menus = [
        ("绯荤粺棣栭〉", "system.dashboard", "/system/dashboard", "views/system/dashboard/index.vue", "menu", None, 0, None, "House"),
        ("绯荤粺绠＄悊", "system", "/system", "", "directory", None, 1, None, "Setting"),
        ("鐢ㄦ埛绠＄悊", "system.users", "/system/users", "views/system/users/index.vue", "menu", "/system", 10, User, "User"),
        ("缁勭粐绠＄悊", "system.organization", "/system/organization", "views/system/organization/index.vue", "menu", "/system", 20, Organization, "OfficeBuilding"),
        ("宀椾綅绠＄悊", "system.position", "/system/position", "views/system/position/index.vue", "menu", "/system", 30, Position, "Postcard"),
        ("瑙掕壊绠＄悊", "system.role", "/system/role", "views/system/role/index.vue", "menu", "/system", 40, Group, "UserFilled"),
        ("鑿滃崟绠＄悊", "system.menu", "/system/menu", "views/system/menu/index.vue", "menu", "/system", 50, Menu, "Setting"),
    ]
    legacy_menu_codes = [
        "system.permission",
        "system.rbac.user_role",
        "system.rbac.role_permission",
        "system.rbac.role_menu",
    ]
    Menu.objects.filter(code__in=legacy_menu_codes).delete()

    menu_objs = []
    menu_map = {}
    for name, code, path, component, menu_type, parent_path, sort, model, icon in menus:
        parent = menu_map.get(parent_path) if parent_path else None
        content_type = ContentType.objects.get_for_model(model) if model else None
        obj, _ = Menu.objects.get_or_create(
            path=path,
            defaults={
                "name": name,
                "code": code,
                "component": component,
                "menu_type": menu_type,
                "icon": icon,
                "parent": parent,
                "sort": sort,
                "content_type": content_type,
            }
        )
        obj.name = name
        obj.code = code
        obj.component = component
        obj.menu_type = menu_type
        obj.icon = icon
        obj.parent = parent
        obj.sort = sort
        obj.content_type = content_type
        obj.save()
        menu_map[path] = obj
        menu_objs.append(obj)

    perm_objs = seed_menu_permissions(menu_map)
    ensure_other_permission_menu(menu_map)
    cleanup_extension_permissions()
    cleanup_unwanted_menu_bindings()
    bind_remaining_permissions_to_other_menu(menu_map["__other_permissions__"])

    admin_user = User.objects.filter(username="admin").first()
    if admin_user:
        admin_user.groups.add(admin_group)
        admin_group.permissions.add(*perm_objs)
        for menu in menu_objs:
            GroupMenu.objects.get_or_create(group=admin_group, menu=menu)
        GroupDataScope.objects.get_or_create(group=admin_group, defaults={"scope_type": "all"})
        admin_user.full_name = "绯荤粺绠＄悊鍛?
        admin_user.organization = root_org
        admin_user.position_name = admin_position.name
        admin_user.save(update_fields=["full_name", "organization", "position_name"])
        UserOrganizationRelation.objects.update_or_create(
            user=admin_user,
            organization=root_org,
            defaults={
                "position": admin_position,
                "relation_type": "primary",
                "status": "active",
                "duty": "绯荤粺绠＄悊鍛?,
            },
        )
        root_org.leader = admin_user
        root_org.save(update_fields=["leader"])

    if not getattr(tech_org, "path", ""):
        sync_organization_tree(root_org)

    print("seed demo data done")

if __name__ == "__main__":
    main()

