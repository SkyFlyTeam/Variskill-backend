from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_remove_activity_content_remove_activity_module_and_more'),
        ('activityManagement', '0006_alter_atividade_modulo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Module',
        ),
    ]
