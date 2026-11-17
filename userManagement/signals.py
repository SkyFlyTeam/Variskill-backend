from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def conceder_itens_padrao_novo_usuario(sender, instance, created, raw=False, **kwargs):
    if not created or raw:
        return
    from .services import conceder_itens_padrao

    conceder_itens_padrao(instance)
