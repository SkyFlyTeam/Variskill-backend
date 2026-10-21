import uuid
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import Mensagem, Sessao
from questionsManagement.models import Questao
from userManagement.models import Consentimento, EventoAuditoria, SolicitacaoRevisao

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        apelido='lgpd_user',
        nome='LGPD User',
        email='lgpd@example.com',
        password='test-password-123',
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        apelido='lgpd_admin',
        nome='LGPD Admin',
        email='lgpd-admin@example.com',
        password='test-password-123',
        is_staff=True,
    )


def test_export_requires_authentication(client):
    assert client.get(reverse('user-export')).status_code == 403


def test_export_returns_profile_and_history(client, user):
    client.force_login(user)

    response = client.get(reverse('user-export'))

    assert response.status_code == 200
    assert 'attachment' in response['Content-Disposition']
    payload = response.json()
    assert payload['perfil']['id'] == str(user.pk)
    assert payload['perfil']['email'] == user.email
    assert 'execucoes' in payload
    assert 'sessoes_chat' in payload
    assert 'consentimentos' in payload


def test_delete_me_anonymizes_and_blocks_login(client, user, django_user_model):
    sessao = Sessao.objects.create(usuario=user)
    Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.ASSISTENTE,
        conteudo='conteúdo pessoal',
    )
    execucao = baker.make(
        ExecucaoAtividade,
        usuario=user,
        resposta={'texto': 'resposta pessoal'},
        pontuacao_obtida=10,
        aprovado=True,
    )
    questao = baker.make(Questao, atividade=execucao.atividade)
    resposta = baker.make(
        RespostaQuestao,
        execucao=execucao,
        questao=questao,
        resposta_fornecida='resposta pessoal',
        correta=False,
    )
    Consentimento.objects.create(usuario=user, tipo='DADOS_OPCIONAIS')

    client.force_login(user)
    response = client.delete(reverse('user-me'))

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.is_active is False
    assert user.apelido.startswith('anonimo_')
    assert user.email.endswith('@anonimizado.local')
    assert user.sexo is None
    assert user.idade is None
    assert user.anonimizado_em is not None
    assert not user.check_password('test-password-123')
    assert '_auth_user_id' not in client.session

    assert not Sessao.objects.filter(pk=sessao.pk).exists()
    execucao.refresh_from_db()
    resposta.refresh_from_db()
    assert execucao.resposta == {}
    assert resposta.resposta_fornecida is None
    assert Consentimento.objects.get(usuario=user).revogado_em is not None


def test_consentimento_create_and_revoke(client, user):
    client.force_login(user)

    response = client.post(
        reverse('consentimento-list'),
        {'tipo': 'DADOS_OPCIONAIS', 'versao_documento': 'v1'},
        format='json',
    )
    assert response.status_code == 201
    assert response.data['tipo'] == 'DADOS_OPCIONAIS'
    assert response.data['ativo'] is True

    response = client.delete(
        reverse('consentimento-detail', args=['DADOS_OPCIONAIS'])
    )
    assert response.status_code == 204

    response = client.get(reverse('consentimento-list'))
    assert response.status_code == 200
    assert response.data[0]['ativo'] is False
    assert response.data[0]['revogado_em'] is not None


def test_consentimento_requires_authentication(client):
    assert client.get(reverse('consentimento-list')).status_code == 403


def test_revisao_create_and_admin_response(client, user, admin):
    client.force_login(user)
    response = client.post(
        reverse('revisao-list'),
        {'tipo': 'NIVELAMENTO', 'referencia_id': str(uuid.uuid4())},
        format='json',
    )
    assert response.status_code == 201
    revisao_id = response.data['id']

    response = client.patch(
        reverse('revisao-detail', args=[revisao_id]),
        {'status': 'REVISADA', 'resposta': 'Revisado por humano.'},
        format='json',
    )
    assert response.status_code == 403

    client.force_login(admin)
    response = client.patch(
        reverse('revisao-detail', args=[revisao_id]),
        {'status': 'REVISADA', 'resposta': 'Revisado por humano.'},
        format='json',
    )
    assert response.status_code == 200
    assert response.data['status'] == 'REVISADA'
    assert response.data['respondido_em'] is not None
    assert SolicitacaoRevisao.objects.get(pk=revisao_id).resposta == 'Revisado por humano.'


def test_xp_and_streak_are_read_only(client, user):
    client.force_login(user)

    response = client.patch(
        reverse('user-me'),
        {'xp_total': 9999, 'streak_dias': 9999},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.xp_total == 0
    assert user.streak_dias == 0


def test_change_password_requires_current_password(client, user):
    client.force_login(user)

    response = client.post(
        reverse('user-change-password'),
        {'senha_atual': 'errada', 'nova_senha': 'new-password-123'},
        format='json',
    )
    assert response.status_code == 400
    assert 'senha_atual' in response.data

    response = client.post(
        reverse('user-change-password'),
        {'senha_atual': 'test-password-123', 'nova_senha': 'new-password-123'},
        format='json',
    )
    assert response.status_code == 204
    user.refresh_from_db()
    assert user.check_password('new-password-123')
    assert '_auth_user_id' not in client.session


def test_expurgar_dados_dry_run_and_execute(client, user):
    sessao = Sessao.objects.create(usuario=user)
    execucao = baker.make(
        ExecucaoAtividade,
        usuario=user,
        resposta={'texto': 'dado antigo'},
        pontuacao_obtida=10,
        aprovado=True,
    )
    questao = baker.make(Questao, atividade=execucao.atividade)
    resposta = baker.make(
        RespostaQuestao,
        execucao=execucao,
        questao=questao,
        resposta_fornecida='dado antigo',
        correta=False,
    )
    antigo = timezone.now() - timedelta(days=2)
    Sessao.objects.filter(pk=sessao.pk).update(criada_em=antigo)
    ExecucaoAtividade.objects.filter(pk=execucao.pk).update(executado_em=antigo)

    call_command('expurgar_dados', dias=1)
    assert Sessao.objects.filter(pk=sessao.pk).exists()
    execucao.refresh_from_db()
    resposta.refresh_from_db()
    assert execucao.resposta == {'texto': 'dado antigo'}
    assert resposta.resposta_fornecida == 'dado antigo'

    call_command('expurgar_dados', dias=1, executar=True)
    assert not Sessao.objects.filter(pk=sessao.pk).exists()
    execucao.refresh_from_db()
    resposta.refresh_from_db()
    assert execucao.resposta == {}
    assert resposta.resposta_fornecida is None


def test_registration_creates_termos_de_uso_consent(client, django_user_model):
    response = client.post(
        reverse('register'),
        {
            'apelido': 'consent_user',
            'nome': 'Consent User',
            'email': 'consent@example.com',
            'password': 'test-password-123',
        },
        format='json',
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(apelido='consent_user')
    consentimento = Consentimento.objects.get(usuario=user, tipo='TERMOS_DE_USO')
    assert consentimento.email_assinante == user.email
    assert consentimento.concedido_em is not None
    assert consentimento.versao_documento
    assert user.aceite_privacidade_em is not None


def test_audit_middleware_logs_authenticated_request(client, user):
    client.force_login(user)

    response = client.get(reverse('user-me'))

    assert response.status_code == 200
    evento = EventoAuditoria.objects.filter(
        acao='REQUISICAO', ator_email=user.email
    ).first()
    assert evento is not None
    assert evento.rota == reverse('user-me')
    assert evento.ator_is_staff is False


def test_audit_query_is_admin_only(client, user, admin):
    EventoAuditoria.objects.create(
        usuario=user,
        ator_email=user.email,
        acao='LOGIN',
        resultado='SUCESSO',
    )
    client.force_login(user)
    assert client.get(reverse('auditoria-list')).status_code == 403

    client.force_login(admin)
    response = client.get(reverse('auditoria-list'))
    assert response.status_code == 200
    assert any(item['acao'] == 'LOGIN' for item in response.data)


def test_hard_delete_requires_admin(client, user, django_user_model):
    target = baker.make(
        django_user_model, apelido='alvo', email='alvo@example.com'
    )
    client.force_login(user)

    response = client.delete(
        reverse('user-hard-delete'), {'email': target.email}
    )

    assert response.status_code == 403
    assert django_user_model.objects.filter(pk=target.pk).exists()


def test_hard_delete_by_email_cascades_and_audits(client, admin, django_user_model):
    target = baker.make(
        django_user_model, apelido='alvo', email='alvo@example.com'
    )
    sessao = Sessao.objects.create(usuario=target)
    Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.ASSISTENTE,
        conteudo='mensagem do alvo',
    )
    Consentimento.objects.create(
        usuario=target,
        tipo='TERMOS_DE_USO',
        email_assinante=target.email,
    )
    client.force_login(admin)

    response = client.delete(
        reverse('user-hard-delete'), {'email': target.email.upper()}
    )

    assert response.status_code == 200
    assert response.data['deleted'] is True
    assert not django_user_model.objects.filter(pk=target.pk).exists()
    assert not Sessao.objects.filter(pk=sessao.pk).exists()
    evento = EventoAuditoria.objects.filter(
        acao='HARD_DELETE', recurso_id=target.pk
    ).first()
    assert evento is not None
    assert evento.metadata['email_alvo'] == target.email


def test_hard_delete_validates_email(client, admin):
    client.force_login(admin)

    assert client.delete(reverse('user-hard-delete')).status_code == 400
    assert client.delete(
        reverse('user-hard-delete'), {'email': 'naoexiste@example.com'}
    ).status_code == 404


def test_expurgar_auditoria_dry_run_and_execute(user):
    evento = EventoAuditoria.objects.create(
        usuario=user,
        ator_email=user.email,
        acao='LOGIN',
    )
    EventoAuditoria.objects.filter(pk=evento.pk).update(
        criado_em=timezone.now() - timedelta(days=2)
    )

    call_command('expurgar_auditoria', dias=1)
    assert EventoAuditoria.objects.filter(pk=evento.pk).exists()

    call_command('expurgar_auditoria', dias=1, executar=True)
    assert not EventoAuditoria.objects.filter(pk=evento.pk).exists()
