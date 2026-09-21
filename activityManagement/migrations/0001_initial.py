import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('admin', '0001_initial'),
        ('userManagement', '0002_rename_nickname_user_apelido_user_criado_em_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name="Modulo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("titulo", models.CharField(max_length=255)),
            ],
            options={"db_table": "MODULO"},
        ),
        migrations.CreateModel(
            name="Atividade",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("titulo", models.CharField(max_length=255)),
                ("descricao", models.TextField(blank=True, default="")),
                ("contexto_avaliacao", models.CharField(max_length=64)),
                ("xp_recompensa", models.PositiveIntegerField(default=0)),
                ("ordem", models.PositiveIntegerField()),
                ("ativo", models.BooleanField(default=True)),
                ("modulo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="atividades", to="activityManagement.modulo")),
            ],
            options={"db_table": "ATIVIDADE", "ordering": ["ordem"]},
        ),
        migrations.CreateModel(
            name="ExecucaoAtividade",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("resposta", models.JSONField()),
                ("pontuacao_obtida", models.IntegerField()),
                ("aprovado", models.BooleanField()),
                ("executado_em", models.DateTimeField(auto_now_add=True)),
                ("atividade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="execucoes", to="activityManagement.atividade")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="execucoes_atividade", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "EXECUCAO_ATIVIDADE"},
        ),
    ]
