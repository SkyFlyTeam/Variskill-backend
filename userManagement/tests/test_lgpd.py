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
from userManagement.models import EventoAuditoria, SolicitacaoRevisao

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
    user.aceite_privacidade_versao = '1.0'
    user.aceite_privacidade_em = timezone.now()
    user.save(update_fields=['aceite_privacidade_versao', 'aceite_privacidade_em'])

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
    assert user.aceite_privacidade_em is None
    assert user.consentimento_revogado_em is not None


def test_admin_export_by_email_returns_profile_and_audits(client, admin, django_user_model):
    target = django_user_model.objects.create_user(
        apelido='export_target',
        nome='Export Target',
        email='export@example.com',
        password='test-password-123',
    )
    client.force_login(admin)

    response = client.get(
        reverse('user-admin-export') + '?email=export@example.com'
    )

    assert response.status_code == 200
    assert 'attachment' in response['Content-Disposition']
    assert response.json()['perfil']['email'] == target.email
    evento = EventoAuditoria.objects.filter(
        acao='EXPORTACAO_DADOS', recurso_id=target.pk
    ).first()
    assert evento is not None
    assert evento.metadata['email_alvo'] == target.email


def test_admin_export_requires_admin(client, user):
    client.force_login(user)
    assert client.get(reverse('user-admin-export') + '?email=alvo@example.com').status_code == 403


def test_admin_export_rejects_unknown_email(client, admin):
    client.force_login(admin)
    assert client.get(reverse('user-admin-export') + '?email=naoexiste@example.com').status_code == 404


def test_profile_update_is_audited_without_values(client, user):
    client.force_login(user)

    response = client.patch(
        reverse('user-me'),
        {'email': 'novo-email@example.com'},
        format='json',
    )

    assert response.status_code == 200
    evento = EventoAuditoria.objects.filter(
        acao='ALTERACAO_PERFIL', recurso_id=user.pk
    ).latest('criado_em')
    assert evento.metadata['campos'] == ['email']
    assert evento.metadata['email_alterado'] is True
    assert 'novo-email@example.com' not in str(evento.metadata)


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


def test_change_password_route_uses_me_prefix():
    assert reverse('user-change-password') == '/api/users/me/alterar-senha/'


def test_change_password_requires_current_password(client, user):
    client.force_login(user)

    response = client.post(
        '/api/users/me/alterar-senha/',
        {'senha_atual': 'errada', 'nova_senha': 'new-password-123'},
        format='json',
    )
    assert response.status_code == 400
    assert 'senha_atual' in response.data

    response = client.post(
        '/api/users/me/alterar-senha/',
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


def test_registration_marks_consent_accepted(client, django_user_model):
    response = client.post(
        reverse('register'),
        {
            'apelido': 'consent_user',
            'nome': 'Consent User',
            'email': 'consent@example.com',
            'password': 'test-password-123',
            'aceite_termos': True,
        },
        format='json',
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(apelido='consent_user')
    assert user.aceite_privacidade_em is not None
    assert user.aceite_privacidade_versao
    assert user.consentimento_revogado_em is None


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
