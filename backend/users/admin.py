from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, Subscribe

admin.site.register(User, UserAdmin, list_filter=('email', 'username'))
admin.site.register(Subscribe)
