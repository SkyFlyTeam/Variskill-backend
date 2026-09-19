import pytest
from django.db import IntegrityError

from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from django.conf import settings


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_trilha_and_modulo_str_and_ordering():
    trilha = Trilha.objects.create(titulo='Javascript', descricao='Desc', habilidade='Frontend')
    m1 = Modulo.objects.create(trilha=trilha, titulo='Módulo 2', nivel='INTERMEDIARIO', ordem_modulo=2)
    m2 = Modulo.objects.create(trilha=trilha, titulo='Módulo 1', nivel='INICIANTE', ordem_modulo=1)

    # __str__ and ordering
    assert str(trilha) == 'Javascript'
    modulos = list(trilha.modulos.all())
    assert modulos[0].ordem_modulo == 1
    assert modulos[0].titulo == 'Módulo 1'


def test_matricula_unique_constraint_and_progresso_defaults(django_user_model):
    # create user
    user = django_user_model.objects.create_user(apelido='testuser')
    trilha = Trilha.objects.create(titulo='Python', descricao='Py', habilidade='Backend')

    # first matricula ok
    m = Matricula.objects.create(usuario=user, trilha=trilha)
    assert m.status == 'EM_ANDAMENTO'

    # duplicate should raise IntegrityError at DB level
    from django.db import transaction
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Matricula.objects.create(usuario=user, trilha=trilha)

    # progresso modulo defaults
    modulo = Modulo.objects.create(trilha=trilha, titulo='Módulo A', nivel='INICIANTE', ordem_modulo=1)
    prog = ProgressoModulo.objects.create(matricula=m, modulo=modulo)
    assert prog.status == 'BLOQUEADO'
    assert str(prog).startswith('Progresso')
