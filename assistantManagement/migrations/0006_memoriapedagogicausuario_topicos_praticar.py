from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistantManagement', '0005_mensagem_duvida_assimilada'),
    ]

    operations = [
        migrations.AddField(
            model_name='memoriapedagogicausuario',
            name='topicos_praticar',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
