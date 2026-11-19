"""Testes da entrega LGPD Sprint 3 (VAR-124).

Cobrem o age gate de menores, o aceite do responsável, a exportação CSV
self-service, a revogação administrativa e o hard delete em cascata.
"""

import pytest
from django.urls import reverse

from userManagement.models import AceiteResponsavel, EventoAuditoria, Interesse, UsuarioInteresse
from userManagement.utils import validar_cpf

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MENSAGEM_MENOR = (
    'Menores de idade precisam de permissão do responsável para utilizar '
    'nossos serviços.'
)

CPF_VALIDO = '529.982.247-25'


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        apelido='sprint3_user',
        nome='Sprint3 User',
        email='sprint3@example.com',
        password='test-password-123',
        idade=21,
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        apelido='sprint3_admin',
        nome='Sprint3 Admin',
        email='sprint3-admin@example.com',
        password='test-password-123',
        is_staff=True,
    )


def _payload_menor(**overrides):
    payload = {
        'apelido': 'menor_sem_resp',
        'nome': 'Menor Sem Responsavel',
        'email': 'menor@example.com',
        'password': 'test-password-123',
        'idade': 16,
        'aceite_termos': True,
    }
    payload.update(overrides)
    return payload


def test_menor_sem_responsavel_bloqueia_cadastro(client, django_user_model):
    response = client.post(reverse('register'), _payload_menor(), format='json')

    assert response.status_code == 400
    assert MENSAGEM_MENOR in str(response.data)
    assert not django_user_model.objects.filter(apelido='menor_sem_resp').exists()


def test_menor_com_responsavel_valido_cadastra_e_audita(client, django_user_model):
    response = client.post(
        reverse('register'),
        _payload_menor(
            responsavel={
                'nome': 'Maria Responsável',
                'cpf': CPF_VALIDO,
                'email': 'responsavel@example.com',
            },
        ),
        format='json',
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(apelido='menor_sem_resp')
    aceite = AceiteResponsavel.objects.get(usuario=user)
    assert aceite.cpf == '52998224725'
    assert response.data['responsavel']['cpf'] == CPF_VALIDO
    evento = EventoAuditoria.objects.filter(
        acao='ACEITE_RESPONSAVEL', recurso_id=user.pk
    ).first()
    assert evento is not None
    assert evento.metadata['menor_de_idade'] is True


def test_responsavel_com_cpf_invalido_e_rejeitado(client, django_user_model):
    response = client.post(
        reverse('register'),
        _payload_menor(
            responsavel={
                'nome': 'Maria Responsável',
                'cpf': '111.111.111-11',
                'email': 'responsavel@example.com',
            },
        ),
        format='json',
    )

    assert response.status_code == 400
    assert 'cpf' in str(response.data)
    assert not django_user_model.objects.filter(apelido='menor_sem_resp').exists()


def test_exportacao_self_service_so_do_titular_logado(client, user, django_user_model):
    outro = django_user_model.objects.create_user(
        apelido='outro_titular',
        nome='Outro Titular',
        email='outro@example.com',
        password='test-password-123',
        idade=30,
    )
    client.force_login(user)

    response = client.get(reverse('user-exportar-csv'))

    assert response.status_code == 200
    assert response['Content-Disposition'].endswith('.csv"')
    conteudo = response.content.decode('utf-8-sig')
    assert conteudo.splitlines()[0] == 'secao,registro_id,campo,valor'
    assert user.email in conteudo
    assert outro.email not in conteudo
    evento = EventoAuditoria.objects.filter(
        acao='EXPORTACAO_DADOS', recurso_id=user.pk
    ).latest('criado_em')
    assert evento.metadata['canal'] == 'self_service'


def test_revogacao_admin_apenas_marca_consentimento(client, user, admin, django_user_model):
    client.force_login(admin)
    url = reverse('user-revogar-consentimento') + f'?email={user.email}'

    response = client.post(url, format='json')
    assert response.status_code == 200
    assert response.data['ja_revogado'] is False

    user.refresh_from_db()
    assert user.consentimento_revogado_em is not None
    assert user.is_active is True
    assert django_user_model.objects.filter(pk=user.pk).exists()

    repetido = client.post(url, format='json')
    assert repetido.status_code == 200
    assert repetido.data['ja_revogado'] is True

    evento = EventoAuditoria.objects.filter(
        acao='CONSENTIMENTO_REVOGADO', recurso_id=user.pk
    ).latest('criado_em')
    assert evento.metadata['canal'] == 'admin'

    client.force_login(user)
    assert client.post(url, format='json').status_code == 403


def test_hard_delete_remove_dados_pessoais_em_cascata(client, user, admin):
    interesse = Interesse.objects.create(nome='Python Cascata')
    UsuarioInteresse.objects.create(usuario=user, interesse=interesse)
    AceiteResponsavel.objects.create(
        usuario=user,
        nome='Responsável Cascata',
        cpf='52998224725',
        email='resp-cascata@example.com',
    )
    user_id = user.pk

    client.force_login(admin)
    response = client.delete(
        reverse('user-hard-delete') + f'?email={user.email}'
    )

    assert response.status_code == 200
    assert not AceiteResponsavel.objects.filter(usuario_id=user_id).exists()
    assert not UsuarioInteresse.objects.filter(usuario_id=user_id).exists()
    # A auditoria é preservada mesmo após a exclusão do titular.
    assert EventoAuditoria.objects.filter(
        acao='HARD_DELETE', recurso_id=user_id
    ).exists()


def test_utilitarios_de_cpf():
    assert validar_cpf(CPF_VALIDO) is True
    assert validar_cpf('111.111.111-11') is False
    assert validar_cpf('123.456.789-00') is False
