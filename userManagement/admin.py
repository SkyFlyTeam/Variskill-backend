from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'nickName', 'is_staff', 'is_active')
    search_fields = ('nickName',)
    ordering = ('nickName',)
    fieldsets = (
        (None, {'fields': ('nickName', 'password')}),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('nickName', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )
