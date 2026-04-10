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
from apps.system.organization.models import Organization
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


def seed_menu_permissions(menu_map):
    permission_specs = [
        ("/system/users", User, [
            ("add_user", "新增用户", "button"),
            ("change_user", "编辑用户", "button"),
            ("delete_user", "删除用户", "button"),
            ("view_user", "查看用户", "api"),
        ]),
        ("/system/organization", Organization, [
            ("add_organization", "新增组织", "button"),
            ("change_organization", "编辑组织", "button"),
            ("delete_organization", "删除组织", "button"),
            ("view_organization", "查看组织", "api"),
        ]),
        ("/system/role", Group, [
            ("add_group", "新增角色", "button"),
            ("change_group", "编辑角色", "button"),
            ("delete_group", "删除角色", "button"),
            ("view_group", "查看角色", "api"),
        ]),
        ("/system/menu", Menu, [
            ("add_menu", "新增菜单", "button"),
            ("change_menu", "编辑菜单", "button"),
            ("delete_menu", "删除菜单", "button"),
            ("view_menu", "查看菜单", "api"),
        ]),
        ("/system/menu", Permission, [
            ("add_permission", "新增权限", "button"),
            ("change_permission", "编辑权限", "button"),
            ("delete_permission", "删除权限", "button"),
            ("view_permission", "查看权限", "api"),
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
            "name": "其他配置权限",
            "path": "",
            "component": "",
            "menu_type": "menu",
            "parent": parent,
            "sort": 99,
            "visible": False,
        }
    )
    obj.name = "其他配置权限"
    obj.menu_type = "menu"
    obj.parent = parent
    obj.sort = 99
    obj.visible = False
    obj.save(update_fields=["name", "menu_type", "parent", "sort", "visible"])
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
    technical_models = [GroupProfile, MenuPermission, GroupMenu, GroupDataScope]
    technical_content_type_ids = [ContentType.objects.get_for_model(model).id for model in technical_models]
    Permission.objects.filter(content_type_id__in=technical_content_type_ids).delete()


def cleanup_unwanted_menu_bindings():
    allowed_app_labels = {"users", "organization", "auth", "menu", "dictionary", "config_center", "audit_log"}
    MenuPermission.objects.exclude(permission__content_type__app_label__in=allowed_app_labels).delete()

def main():
    root_org, _ = Organization.objects.get_or_create(
        code="ROOT",
        defaults={"name": "总部", "sort": 1}
    )
    Organization.objects.get_or_create(
        code="TECH",
        defaults={"name": "技术部", "parent": root_org, "sort": 2}
    )

    admin_group, _ = Group.objects.get_or_create(
        name="管理员"
    )
    GroupProfile.objects.get_or_create(
        group=admin_group,
        defaults={"code": "admin", "description": "系统管理员"}
    )
    dev_group, _ = Group.objects.get_or_create(name="开发人员")
    GroupProfile.objects.get_or_create(
        group=dev_group,
        defaults={"code": "developer", "description": "开发角色"}
    )

    menus = [
        ("系统管理", "system", "/system", "", "directory", None, 1, None),
        ("系统首页", "system.dashboard", "/system/dashboard", "views/system/dashboard/index.vue", "menu", "/system", 1, None),
        ("用户管理", "system.users", "/system/users", "views/system/users/index.vue", "menu", "/system", 2, User),
        ("组织管理", "system.organization", "/system/organization", "views/system/organization/index.vue", "menu", "/system", 3, Organization),
        ("角色管理", "system.role", "/system/role", "views/system/role/index.vue", "menu", "/system", 4, Group),
        ("菜单管理", "system.menu", "/system/menu", "views/system/menu/index.vue", "menu", "/system", 5, Menu),
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
    for name, code, path, component, menu_type, parent_path, sort, model in menus:
        parent = menu_map.get(parent_path) if parent_path else None
        content_type = ContentType.objects.get_for_model(model) if model else None
        obj, _ = Menu.objects.get_or_create(
            path=path,
            defaults={
                "name": name,
                "code": code,
                "component": component,
                "menu_type": menu_type,
                "parent": parent,
                "sort": sort,
                "content_type": content_type,
            }
        )
        obj.name = name
        obj.code = code
        obj.component = component
        obj.menu_type = menu_type
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
        admin_user.full_name = "系统管理员"
        admin_user.organization = root_org
        admin_user.save(update_fields=["full_name", "organization"])

    print("seed demo data done")

if __name__ == "__main__":
    main()
