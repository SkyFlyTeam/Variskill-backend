from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userManagement', '0003_sync_user_id_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_primeiro_acesso',
            field=models.BooleanField(default=True),
        ),
    ]
