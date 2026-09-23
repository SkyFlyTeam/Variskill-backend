from django.db import migrations


def delete_activities_of_legacy_modules(apps, schema_editor):
    # Toda atividade existente aponta para learning.Module, que deixa de existir.
    Atividade = apps.get_model('activityManagement', 'Atividade')
    Atividade.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('activityManagement', '0004_execucaoatividade_usuario'),
    ]

    operations = [
        migrations.RunPython(delete_activities_of_legacy_modules, migrations.RunPython.noop),
    ]
