from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import Subscriptions, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для пользователей."""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('id', 'username')
    list_filter = ('email', 'first_name')
    empty_value_display = '-пусто-'


admin.site.register(Subscriptions)
admin.site.unregister(Group)
