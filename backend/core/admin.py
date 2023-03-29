from django.contrib import admin

from core.models import Tag, Ingredient

admin.site.register(Tag)
admin.site.register(
    Ingredient,
    list_display=('name', 'measurement_unit'),
    list_filter=('name',)
)
