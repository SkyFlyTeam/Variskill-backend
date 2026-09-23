import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityManagement', '0005_delete_atividades_de_modulos_legados'),
        ('trackManagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atividade',
            name='modulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atividades', to='trackManagement.modulo'),
        ),
    ]
