from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackManagement', '0002_create_pgvector_extension'),
    ]

    operations = [
        migrations.AddField(
            model_name='trilha',
            name='gerada_por_ia',
            field=models.BooleanField(default=False),
        ),
    ]
