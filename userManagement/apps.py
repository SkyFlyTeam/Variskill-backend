from django.apps import AppConfig


class UsermanagementConfig(AppConfig):
    name = 'userManagement'

    def ready(self):
        from . import signals  # noqa: F401
