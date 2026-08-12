from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class UsesrAdmin(BaseUserAdmin):
    list_display = ["email", "username", "is_staff"]
    ordering = ["email",]
    search_fields = ["email", "username"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional info", {
            "fields": ["bio", "image"]
        }),
    )
    add_fieldsets = (
            (
                None,
                {
                    "classes": ("wide",),
                    "fields": ("email", "username", "usable_password", "password1", "password2"),
                },
            ),
        )

