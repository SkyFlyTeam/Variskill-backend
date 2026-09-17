from django.contrib import admin

from .models import Intention, IntentionExample, Response


@admin.register(Intention)
class IntentionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'system_action')
    search_fields = ('code',)


@admin.register(IntentionExample)
class IntentionExampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'intention', 'text')
    list_filter = ('intention',)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'intention', 'text')
    list_filter = ('intention',)
