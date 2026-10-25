import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from trackManagement.models import Matricula, Modulo, Trilha
from userManagement.models import Interesse, UsuarioInteresse


pytestmark = [pytest.mark.integration, pytest.mark.django_db]

URL = '/api/trilhas/recomendadas/'


def make_user(django_user_model, apelido, sexo=None, idade=None, interesses=(), **kwargs):
    user = django_user_model.objects.create_user(
        apelido=apelido,
        nome=apelido,
        email=f'{apelido}@example.com',
        sexo=sexo,
        idade=idade,
        **kwargs,
    )
    UsuarioInteresse.objects.bulk_create([
        UsuarioInteresse(usuario=user, interesse=interesse) for interesse in interesses
    ])
    return user


def make_trilha(titulo, **kwargs):
    trilha = Trilha.objects.create(titulo=titulo, habilidade='Geral', ativo=True, **kwargs)
    Modulo.objects.create(trilha=trilha, titulo='Modulo 1', nivel='INICIANTE', ordem_modulo=1)
    return trilha


def matricular(user, trilha):
    return Matricula.objects.create(usuario=user, trilha=trilha)


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def interesses():
    return {
        nome: Interesse.objects.create(nome=nome)
        for nome in ('Python', 'JavaScript', 'Ciência de Dados')
    }


def test_recomenda_trilha_feita_por_estudantes_com_perfil_similar(django_user_model, interesses):
    python_web = make_trilha('Python Web')
    javascript = make_trilha('JavaScript Basico')
    user = make_user(django_user_model, 'aluna', sexo='F', idade=20, interesses=[interesses['Python']])

    for indice in range(2):
        similar = make_user(
            django_user_model, f'similar-{indice}', sexo='F', idade=21, interesses=[interesses['Python']],
        )
        matricular(similar, python_web)
    for indice in range(3):
        diferente = make_user(
            django_user_model, f'diferente-{indice}', sexo='M', idade=45, interesses=[interesses['JavaScript']],
        )
        matricular(diferente, javascript)

    response = authenticated_client(user).get(URL)

    assert response.status_code == 200
    assert [t['titulo'] for t in response.data] == ['Python Web', 'JavaScript Basico']
    primeira = response.data[0]
    assert primeira['criterio'] == 'PERFIL_SIMILAR'
    assert primeira['motivo'] == (
        'Estudantes com interesses parecidos com os seus e idade próxima à sua estão fazendo esta trilha.'
    )
    assert primeira['total_modulos'] == 1
    assert response.data[1]['criterio'] == 'POPULARIDADE'


def test_interesses_em_comum_pesam_mais_que_sexo_e_idade(django_user_model, interesses):
    dados = make_trilha('Analise de Dados')
    frontend = make_trilha('Frontend')
    user = make_user(
        django_user_model, 'aluno', sexo='M', idade=30, interesses=[interesses['Ciência de Dados']],
    )
    matricular(
        make_user(django_user_model, 'mesmo-interesse', sexo='F', idade=50, interesses=[interesses['Ciência de Dados']]),
        dados,
    )
    matricular(make_user(django_user_model, 'mesmo-perfil', sexo='M', idade=30), frontend)

    response = authenticated_client(user).get(URL)

    assert [t['titulo'] for t in response.data] == ['Analise de Dados', 'Frontend']
    assert all(t['criterio'] == 'PERFIL_SIMILAR' for t in response.data)


def test_nao_recomenda_trilhas_em_que_o_estudante_ja_esta_matriculado(django_user_model, interesses):
    feita = make_trilha('Ja Matriculada')
    nova = make_trilha('Nova')
    user = make_user(django_user_model, 'aluno', interesses=[interesses['Python']])
    matricular(user, feita)
    similar = make_user(django_user_model, 'similar', interesses=[interesses['Python']])
    matricular(similar, feita)
    matricular(similar, nova)

    response = authenticated_client(user).get(URL)

    assert [t['titulo'] for t in response.data] == ['Nova']


def test_ignora_estudantes_anonimizados_ou_sem_consentimento(django_user_model, interesses):
    make_trilha('Catalogo A')
    revogada = make_trilha('Catalogo B')
    user = make_user(django_user_model, 'aluno', sexo='F', idade=20, interesses=[interesses['Python']])
    matricular(
        make_user(
            django_user_model, 'revogou', sexo='F', idade=20, interesses=[interesses['Python']],
            consentimento_revogado_em=timezone.now(),
        ),
        revogada,
    )

    response = authenticated_client(user).get(URL)

    trilha_b = next(t for t in response.data if t['titulo'] == 'Catalogo B')
    assert trilha_b['criterio'] == 'POPULARIDADE'


def test_sem_perfis_similares_recorre_a_popularidade_e_ao_catalogo(django_user_model):
    make_trilha('B Sem Matriculas', descricao='Descricao da trilha B')
    popular = make_trilha('Z Popular')
    user = make_user(django_user_model, 'sem-perfil')
    matricular(make_user(django_user_model, 'outro'), popular)

    response = authenticated_client(user).get(URL)

    assert [(t['titulo'], t['criterio']) for t in response.data] == [
        ('Z Popular', 'POPULARIDADE'),
        ('B Sem Matriculas', 'CATALOGO'),
    ]
    assert response.data[1]['motivo'] == 'Descricao da trilha B'


def test_respeita_o_limite_informado(django_user_model):
    for indice in range(5):
        make_trilha(f'Trilha {indice}')
    user = make_user(django_user_model, 'aluno')

    response = authenticated_client(user).get(URL, {'limite': 2})

    assert response.status_code == 200
    assert len(response.data) == 2
    assert authenticated_client(user).get(URL, {'limite': 0}).status_code == 400


def test_recomendadas_exige_autenticacao():
    assert APIClient().get(URL).status_code in (401, 403)
