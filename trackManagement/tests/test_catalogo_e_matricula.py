import pytest
from rest_framework.test import APIClient

from activityManagement.models import Atividade
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def make_user(django_user_model, apelido='catalogo-user'):
    return django_user_model.objects.create_user(
        apelido=apelido,
        nome='Catalogo User',
        email=f'{apelido}@example.com',
    )


def make_trilha(**kwargs):
    defaults = {'titulo': 'Javascript', 'habilidade': 'Frontend', 'ativo': True}
    defaults.update(kwargs)
    return Trilha.objects.create(**defaults)


def make_modulo(trilha, ordem, **kwargs):
    return Modulo.objects.create(
        trilha=trilha,
        titulo=f'Modulo {ordem}',
        nivel='INICIANTE',
        ordem_modulo=ordem,
        **kwargs,
    )


def make_atividade(modulo, ordem, ativo=True):
    return Atividade.objects.create(
        modulo=modulo,
        titulo=f'Atividade {ordem}',
        contexto_avaliacao='CODIGO',
        ordem=ordem,
        ativo=ativo,
    )


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_listar_trilhas_retorna_apenas_ativas_com_contagens(django_user_model):
    user = make_user(django_user_model)
    trilha = make_trilha(titulo='Javascript')
    make_trilha(titulo='Inativa', ativo=False)
    modulo_1 = make_modulo(trilha, 1)
    modulo_2 = make_modulo(trilha, 2)
    make_atividade(modulo_1, 1, ativo=True)
    make_atividade(modulo_1, 2, ativo=False)
    make_atividade(modulo_2, 1, ativo=True)

    response = authenticated_client(user).get('/api/trilhas/')

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]['id'] == str(trilha.pk)
    assert body[0]['titulo'] == 'Javascript'
    assert body[0]['total_modulos'] == 2
    assert body[0]['total_atividades'] == 2


def test_trilha_gerada_por_outro_estudante_aparece_para_todos_com_a_marcacao(django_user_model):
    autor = make_user(django_user_model, apelido='autor-ia')
    outro = make_user(django_user_model, apelido='outro-aluno')
    make_trilha(titulo='Javascript')
    gerada = make_trilha(titulo='Culinaria: Primeiros Passos', habilidade='Culinaria', gerada_por_ia=True, criada_por=autor)

    body = authenticated_client(outro).get('/api/trilhas/').json()

    marcacoes = {item['titulo']: item['gerada_por_ia'] for item in body}
    assert marcacoes == {'Javascript': False, gerada.titulo: True}


def test_listar_trilhas_exige_autenticacao():
    response = APIClient().get('/api/trilhas/')
    assert response.status_code in (401, 403)


def test_matricular_cria_matricula_e_inicializa_progresso(django_user_model):
    user = make_user(django_user_model)
    trilha = make_trilha()
    make_modulo(trilha, 1)
    make_modulo(trilha, 2)
    make_modulo(trilha, 3)

    response = authenticated_client(user).post(
        '/api/matriculas/', {'trilha_id': str(trilha.pk)}, format='json',
    )

    assert response.status_code == 201
    body = response.json()
    assert body['mensagem'] == 'Matrícula realizada com sucesso'
    assert body['matricula']['trilha_id'] == str(trilha.pk)
    assert body['matricula']['trilha_titulo'] == trilha.titulo
    assert body['matricula']['status'] == 'EM_ANDAMENTO'
    assert body['matricula']['modulo_atual']['status'] == 'EM_ANDAMENTO'

    matricula = Matricula.objects.get(usuario=user, trilha=trilha)
    statuses = list(
        matricula.progresso_modulos
        .order_by('modulo__ordem_modulo')
        .values_list('status', flat=True)
    )
    assert statuses == ['EM_ANDAMENTO', 'BLOQUEADO', 'BLOQUEADO']


def test_matricular_duplicada_retorna_erro(django_user_model):
    user = make_user(django_user_model)
    trilha = make_trilha()
    make_modulo(trilha, 1)
    Matricula.objects.create(usuario=user, trilha=trilha)

    response = authenticated_client(user).post(
        '/api/matriculas/', {'trilha_id': str(trilha.pk)}, format='json',
    )

    assert response.status_code == 400
    detail = response.json()['detail']
    if isinstance(detail, list):
        detail = ' '.join(detail)
    assert user.apelido in detail
    assert user.email in detail
    assert trilha.titulo in detail
    assert Matricula.objects.filter(usuario=user, trilha=trilha).count() == 1


def test_matricular_trilha_sem_modulos_retorna_erro(django_user_model):
    user = make_user(django_user_model)
    trilha = make_trilha()

    response = authenticated_client(user).post(
        '/api/matriculas/', {'trilha_id': str(trilha.pk)}, format='json',
    )

    assert response.status_code == 400
    assert not ProgressoModulo.objects.exists()


def test_matricular_trilha_inexistente_retorna_404(django_user_model):
    import uuid

    user = make_user(django_user_model)
    response = authenticated_client(user).post(
        '/api/matriculas/', {'trilha_id': str(uuid.uuid4())}, format='json',
    )

    assert response.status_code == 404


def test_schema_da_geracao_de_trilha_segue_o_modo_strict():
    # Structured Outputs (strict) exige todo objeto com additionalProperties=False e todos os campos obrigatórios.
    from trackManagement.geracao_trilha import SCHEMA_GERACAO

    def objetos(no):
        if isinstance(no, dict):
            if no.get("type") == "object":
                yield no
            for valor in no.values():
                yield from objetos(valor)
        elif isinstance(no, list):
            for valor in no:
                yield from objetos(valor)

    encontrados = list(objetos(SCHEMA_GERACAO))
    assert len(encontrados) == 5
    for objeto in encontrados:
        assert objeto["additionalProperties"] is False
        assert set(objeto["required"]) == set(objeto["properties"])
