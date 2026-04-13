from django.conf import settings
from django.db import models

from common.models.base import AuditModel, TimestampedModel


class Organization(AuditModel):
    KIND_CHOICES = (
        ("group", "集团"),
        ("company", "公司/分支机构"),
        ("department", "部门"),
        ("team", "小组"),
    )

    STATUS_CHOICES = (
        ("active", "正常"),
        ("disabled", "停用"),
    )

    name = models.CharField("组织名称", max_length=100)
    code = models.CharField("组织编码", max_length=50, unique=True)
    org_kind = models.CharField("组织类型", max_length=20, choices=KIND_CHOICES, default="department")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
        verbose_name="上级组织",
    )
    path = models.CharField("层级路径", max_length=500, blank=True, default="")
    path_name = models.CharField("全路径名称", max_length=500, blank=True, default="")
    level = models.PositiveIntegerField("层级", default=1)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="led_organizations",
        verbose_name="负责人",
    )
    is_temporary = models.BooleanField("是否临时机构", default=False)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="active")
    sort = models.PositiveIntegerField("排序", default=0)
    remark = models.TextField("备注", blank=True, default="")

    class Meta:
        verbose_name = "组织机构"
        verbose_name_plural = verbose_name
        ordering = ["sort", "id"]

    def __str__(self):
        return self.name


class Position(AuditModel):
    STATUS_CHOICES = (
        ("active", "启用"),
        ("disabled", "停用"),
    )

    name = models.CharField("岗位名称", max_length=100)
    code = models.CharField("岗位编码", max_length=50, unique=True)
    category = models.CharField("岗位类别", max_length=50, blank=True, default="")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="active")
    sort = models.PositiveIntegerField("排序", default=0)
    remark = models.TextField("备注", blank=True, default="")

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = "岗位管理"
        ordering = ["sort", "id"]

    def __str__(self):
        return self.name


class UserOrganizationRelation(TimestampedModel):
    RELATION_CHOICES = (
        ("primary", "隶属"),
        ("part_time", "兼职"),
        ("borrowed", "借调"),
        ("temporary", "临时加入"),
    )

    STATUS_CHOICES = (
        ("active", "有效"),
        ("inactive", "失效"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_relations",
        verbose_name="用户",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="user_relations",
        verbose_name="组织",
    )
    position = models.ForeignKey(
        Position,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_relations",
        verbose_name="岗位",
    )
    relation_type = models.CharField("关系类型", max_length=20, choices=RELATION_CHOICES, default="primary")
    duty = models.CharField("职务说明", max_length=100, blank=True, default="")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        verbose_name = "用户组织关系"
        verbose_name_plural = "用户组织关系"
        unique_together = ("user", "organization")
        default_permissions = ()

    def __str__(self):
        return f"{self.user} - {self.organization}"
