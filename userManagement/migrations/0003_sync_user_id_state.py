import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userManagement', '0002_rename_nickname_user_apelido_user_criado_em_and_more'),
    ]

    # A 0002 converteu a PK para UUID via RunSQL, sem atualizar o estado do Django.
    # O banco já está correto; aqui só alinhamos o estado para que FKs futuras usem uuid.
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='user',
                    name='id',
                    field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
            ],
        ),
    ]
