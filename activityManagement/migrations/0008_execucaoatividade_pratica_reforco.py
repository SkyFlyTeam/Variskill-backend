from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityManagement', '0007_respostaquestao'),
    ]

    operations = [
        migrations.AddField(
            model_name='execucaoatividade',
            name='pratica_reforco',
            field=models.BooleanField(default=False),
        ),
    ]
