import pytest
from trackManagement.serializers import (
    TrilhaSerializer,
    ModuloSerializer,
    MatriculaSerializer,
    ProgressoModuloSerializer,
)


@pytest.mark.django_db
def test_trilha_serializer_create():
    data = {"titulo": "NodeJS", "descricao": "desc", "habilidade": "Backend", "ativo": True}
    ser = TrilhaSerializer(data=data)
    assert ser.is_valid(), ser.errors
    trilha = ser.save()
    assert trilha.titulo == "NodeJS"


@pytest.mark.django_db
def test_modulo_serializer_create(trilha=None):
    # create trilha via serializer
    trilha_data = {"titulo": "Go", "descricao": "desc", "habilidade": "Backend", "ativo": True}
    trilha = TrilhaSerializer(data=trilha_data)
    trilha.is_valid(raise_exception=True)
    trilha = trilha.save()

    data = {"trilha": trilha.id, "titulo": "Módulo X", "descricao": "d", "nivel": "INICIANTE", "ordem_modulo": 1}
    ser = ModuloSerializer(data=data)
    assert ser.is_valid(), ser.errors
    modulo = ser.save()
    assert modulo.titulo == "Módulo X"


@pytest.mark.django_db
def test_matricula_serializer_duplicate_prevent(django_user_model):
    user = django_user_model.objects.create_user(nickName='srl')
    trilha_data = {"titulo": "Rust", "descricao": "desc", "habilidade": "Backend", "ativo": True}
    trilha_ser = TrilhaSerializer(data=trilha_data)
    trilha_ser.is_valid(raise_exception=True)
    trilha = trilha_ser.save()

    data = {"usuario": user.id, "trilha": trilha.id}
    ser = MatriculaSerializer(data=data)
    assert ser.is_valid(), ser.errors
    ser.save()

    ser2 = MatriculaSerializer(data=data)
    assert not ser2.is_valid()
    # Accept either custom validation message or DRF's UniqueTogetherValidator message
    assert 'non_field_errors' in ser2.errors


@pytest.mark.django_db
def test_progresso_modulo_serializer_create(django_user_model):
    user = django_user_model.objects.create_user(nickName='srl2')
    trilha = TrilhaSerializer(data={"titulo": "TS", "descricao": "d", "habilidade": "Frontend", "ativo": True})
    trilha.is_valid(raise_exception=True)
    trilha = trilha.save()
    modulo = ModuloSerializer(data={"trilha": trilha.id, "titulo": "M1", "descricao": "", "nivel": "INICIANTE", "ordem_modulo": 1})
    modulo.is_valid(raise_exception=True)
    modulo = modulo.save()
    matricula = MatriculaSerializer(data={"usuario": user.id, "trilha": trilha.id})
    matricula.is_valid(raise_exception=True)
    matricula = matricula.save()

    prog = ProgressoModuloSerializer(data={"matricula": matricula.id, "modulo": modulo.id})
    assert prog.is_valid(), prog.errors
    p = prog.save()
    assert p.status == 'BLOQUEADO'
