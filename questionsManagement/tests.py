import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from activityManagement.models import Atividade
from learning.models import Module

from .models import Questao, QuestaoOpcao


@pytest.fixture
def admin_user(django_user_model):
    return baker.make(django_user_model, is_staff=True)


@pytest.fixture
def atividade():
    return baker.make(Atividade, modulo=baker.make(Module))


@pytest.mark.django_db
def test_admin_cria_questao_com_opcoes_em_uma_operacao(admin_user, atividade):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    payload = {
        'atividade_id': str(atividade.id),
        'tipo_exercicio': 'ORDENAR_BLOCOS',
        'enunciado': 'Ordene os blocos',
        'codigo_snippet': 'const x = 1',
        'gabarito_esperado': '["bloco_2", "bloco_1"]',
        'explicacao': 'Explicacao',
        'dica_conceitual': 'Dica',
        'ordem_questao': 1,
        'peso_pontuacao': 15,
        'opcoes': [
            {'texto_opcao': 'bloco_1', 'ordem': 1},
            {'texto_opcao': 'bloco_2', 'ordem': 2},
        ],
    }

    response = client.post('/api/questoes/', payload, format='json')

    assert response.status_code == 201
    questao = Questao.objects.get()
    assert questao.gabarito_esperado == payload['gabarito_esperado']
    assert questao.peso_pontuacao == 15
    assert list(questao.opcoes.values_list('ordem', flat=True)) == [1, 2]
    assert response.data['gabarito_esperado'] == payload['gabarito_esperado']


@pytest.mark.django_db
def test_questao_rejeita_tipo_de_exercicio_invalido(admin_user, atividade):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    payload = {
        'atividade_id': str(atividade.id),
        'tipo_exercicio': 'TIPO_INVALIDO',
        'enunciado': 'Enunciado',
        'gabarito_esperado': 'gabarito',
        'ordem_questao': 1,
    }

    response = client.post('/api/questoes/', payload, format='json')

    assert response.status_code == 400
    assert not Questao.objects.exists()


@pytest.mark.django_db
def test_questao_exige_administrador(admin_user, atividade, django_user_model):
    client = APIClient()
    usuario = baker.make(django_user_model, is_staff=False)
    payload = {
        'atividade_id': str(atividade.id),
        'tipo_exercicio': 'COMPLETE_CODIGO',
        'enunciado': 'Complete',
        'gabarito_esperado': 'return 1',
        'ordem_questao': 1,
    }

    client.force_authenticate(user=usuario)
    assert client.post('/api/questoes/', payload, format='json').status_code == 403

    client.force_authenticate(user=admin_user)
    assert client.post('/api/questoes/', payload, format='json').status_code == 201


@pytest.mark.django_db
def test_excluir_questao_exclui_opcoes_em_cascata(atividade):
    questao = baker.make(Questao, atividade=atividade)
    opcao = baker.make(QuestaoOpcao, questao=questao)

    questao.delete()

    assert not QuestaoOpcao.objects.filter(pk=opcao.pk).exists()
