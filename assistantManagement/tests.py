import pytest
from django.db import IntegrityError
from django.utils import timezone
from model_bakery import baker

from intents.models import Intention

from .models import Mensagem, Sessao


@pytest.mark.django_db
def test_sessao_cria_com_usuario_e_timestamps(django_user_model):
    usuario = baker.make(django_user_model)

    sessao = Sessao.objects.create(usuario=usuario)

    assert sessao.usuario == usuario
    assert sessao.criada_em is not None
    assert sessao.atualizada_em is not None
    assert sessao.atualizada_em >= sessao.criada_em


@pytest.mark.django_db
def test_mensagem_persiste_intencao_e_distancia(django_user_model):
    usuario = baker.make(django_user_model)
    sessao = Sessao.objects.create(usuario=usuario)
    intencao = baker.make(Intention)

    mensagem = Mensagem.objects.create(
        sessao=sessao,
        intencao=intencao,
        remetente=Mensagem.Remetente.ASSISTENTE,
        conteudo='Resposta do coach',
        distancia='0.123456',
    )

    mensagem.refresh_from_db()
    assert mensagem.sessao == sessao
    assert mensagem.intencao == intencao
    assert mensagem.remetente == 'ASSISTENTE'
    assert mensagem.conteudo == 'Resposta do coach'
    assert str(mensagem.distancia) == '0.123456'
    assert mensagem.criada_em is not None


@pytest.mark.django_db
def test_mensagem_pode_ser_criada_sem_intencao(django_user_model):
    sessao = Sessao.objects.create(usuario=baker.make(django_user_model))

    mensagem = Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.USUARIO,
        conteudo='Preciso de ajuda',
    )

    assert mensagem.intencao is None


@pytest.mark.django_db
def test_sessao_exclui_mensagens_em_cascata(django_user_model):
    sessao = Sessao.objects.create(usuario=baker.make(django_user_model))
    mensagem = baker.make(Mensagem, sessao=sessao)

    sessao.delete()

    assert not Mensagem.objects.filter(pk=mensagem.pk).exists()


@pytest.mark.django_db
def test_sessao_possui_indice_por_usuario():
    index_names = {index.name for index in Sessao._meta.indexes}

    assert 'sessao_usuario_idx' in index_names


@pytest.mark.django_db
def test_mensagem_possui_indice_por_sessao():
    index_names = {index.name for index in Mensagem._meta.indexes}

    assert 'mensagem_sessao_idx' in index_names
