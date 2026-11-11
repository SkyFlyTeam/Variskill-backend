import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistantManagement', '0003_mensagem_origem_resposta'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemoriaPedagogicaUsuario',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pontos_fortes', models.JSONField(blank=True, default=list)),
                ('topicos_dificuldade', models.JSONField(blank=True, default=list)),
                ('total_atividades_avaliadas', models.PositiveIntegerField(default=0)),
                ('taxa_acerto_geral', models.FloatField(default=0.0)),
                ('resumo_perfil_didatico', models.TextField(blank=True, default='')),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('usuario', models.OneToOneField(db_column='usuario_id', on_delete=django.db.models.deletion.CASCADE, related_name='memoria_pedagogica', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Memória Pedagógica do Usuário',
                'verbose_name_plural': 'Memórias Pedagógicas dos Usuários',
                'db_table': 'MEMORIA_PEDAGOGICA_USUARIO',
            },
        ),
    ]
