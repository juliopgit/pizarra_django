from django.contrib import admin

from .models import PostIt


@admin.register(PostIt)
class PostItAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'asignado_a', 'completada', 'creado_el',)
	list_filter = ('completada', 'asignado_a')
	search_fields = ('titulo', 'contenido', 'asignado_a__username')
