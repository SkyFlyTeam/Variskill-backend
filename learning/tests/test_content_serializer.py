import uuid

import pytest

from activityManagement.models import Conteudo
from learning.serializers import ContentSerializer

pytestmark = [pytest.mark.unit]


def payload(**overrides):
    value = {'titulo': 'Variaveis', 'texto_explicativo': 'Texto', 'tempo_estimado_minutos': 4}
    value.update(overrides)
    return value


def test_serializer_maps_fields():
    serializer = ContentSerializer(data=payload())
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['titulo'] == 'Variaveis'
    assert serializer.validated_data['texto_explicativo'] == 'Texto'
    assert serializer.validated_data['tempo_estimado_minutos'] == 4


def test_serializer_requires_mandatory_fields():
    serializer = ContentSerializer(data={})
    assert not serializer.is_valid()
    assert set(serializer.errors) == {'titulo', 'texto_explicativo', 'tempo_estimado_minutos'}


def test_serializer_preserves_markdown():
    markdown = '\n\n```js\nconst total = 4\n```\n\n'
    serializer = ContentSerializer(data=payload(texto_explicativo=markdown))
    assert serializer.is_valid()
    assert serializer.validated_data['texto_explicativo'] == markdown


def test_serializer_output_exposes_fields():
    content = Conteudo(titulo='Variaveis', texto_explicativo='Texto', tempo_estimado_minutos=4)
    data = ContentSerializer(content).data
    assert set(data) == {'id', 'titulo', 'texto_explicativo', 'tempo_estimado_minutos', 'criado_em'}
    assert data['titulo'] == 'Variaveis'


def test_serializer_ignores_read_only_fields():
    serializer = ContentSerializer(data=payload(id=str(uuid.uuid4()), criado_em='2026-09-08T10:00:00Z'))
    assert serializer.is_valid()
    assert 'id' not in serializer.validated_data
    assert 'criado_em' not in serializer.validated_data
