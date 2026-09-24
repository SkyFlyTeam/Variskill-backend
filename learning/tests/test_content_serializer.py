import uuid

import pytest

from learning.models import Content
from learning.serializers import ContentSerializer


pytestmark = [pytest.mark.unit]


def valid_payload(**overrides):
    payload = {
        'titulo': 'Variáveis',
        'texto_explicativo': 'Variáveis armazenam dados.',
        'tempo_estimado_minutos': 4,
    }
    payload.update(overrides)
    return payload


def test_serializer_maps_contract_fields_to_model_fields():
    serializer = ContentSerializer(data=valid_payload())

    assert serializer.is_valid()
    assert serializer.validated_data == {
        'title': 'Variáveis',
        'explanatory_text': 'Variáveis armazenam dados.',
        'estimated_minutes': 4,
    }


def test_serializer_requires_all_mandatory_fields():
    serializer = ContentSerializer(data={})

    assert not serializer.is_valid()
    assert set(serializer.errors) == {
        'titulo',
        'texto_explicativo',
        'tempo_estimado_minutos',
    }


def test_serializer_preserves_markdown_whitespace_and_newlines():
    markdown = '\n\n```js\nconst total = 4\n```\n\n'
    serializer = ContentSerializer(data=valid_payload(texto_explicativo=markdown))

    assert serializer.is_valid()
    assert serializer.validated_data['explanatory_text'] == markdown


def test_serializer_ignores_read_only_fields():
    serializer = ContentSerializer(
        data=valid_payload(id=str(uuid.uuid4()), criado_em='2026-09-08T10:00:00Z')
    )

    assert serializer.is_valid()
    assert 'id' not in serializer.validated_data
    assert 'criado_em' not in serializer.validated_data


def test_serializer_output_exposes_contract_fields():
    content = Content(
        title='Variáveis',
        explanatory_text='Texto',
        estimated_minutes=4,
    )

    data = ContentSerializer(content).data

    assert set(data) == {
        'id',
        'titulo',
        'texto_explicativo',
        'tempo_estimado_minutos',
        'criado_em',
    }
    assert data['titulo'] == 'Variáveis'
    assert data['texto_explicativo'] == 'Texto'
    assert data['tempo_estimado_minutos'] == 4
