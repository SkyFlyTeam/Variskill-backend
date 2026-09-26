from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from activityManagement.models import Atividade
from assistantManagement.models import Mensagem, Sessao
from questionsManagement.models import Questao
from trackManagement.models import Modulo, Trilha

User = get_user_model()


class HintEndpointTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nome='Test User',
            apelido='tester',
        )
        self.client.force_authenticate(user=self.user)

        self.trilha = Trilha.objects.create(
            titulo='Trilha Teste',
            descricao='Desc',
            habilidade='Frontend',
        )
        self.modulo = Modulo.objects.create(
            trilha=self.trilha,
            titulo='Modulo 1',
            nivel='INICIANTE',
            ordem_modulo=1,
        )
        self.atividade = Atividade.objects.create(
            modulo=self.modulo,
            titulo='Atividade 1',
            contexto_avaliacao='CODIGO',
            ordem=1,
        )
        self.questao_local = Questao.objects.create(
            atividade=self.atividade,
            tipo_exercicio='MULTIPLA_ESCOLHA',
            enunciado='Qual o comando para declarar constante?',
            gabarito_esperado='const',
            dica_conceitual='Use a palavra const quando o valor nao for reatribuido.',
            ordem_questao=1,
        )
        self.questao_sem_dica = Questao.objects.create(
            atividade=self.atividade,
            tipo_exercicio='MULTIPLA_ESCOLHA',
            enunciado='Qual o comando para loop?',
            gabarito_esperado='for',
            dica_conceitual='',
            ordem_questao=2,
        )
        self.sessao = Sessao.objects.create(usuario=self.user)
        self.url = f'/api/atividades/{self.atividade.id}/pedir-dica/'

    def test_pedir_dica_local_sucesso(self):
        payload = {
            'sessao_id': str(self.sessao.id),
            'questao_id': str(self.questao_local.id),
            'pergunta': 'Como crio uma constante?',
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['origem_resposta'], 'PLN_LOCAL')
        self.assertEqual(response.data['resposta_coach'], self.questao_local.dica_conceitual)
        self.assertEqual(response.data['questao_id'], str(self.questao_local.id))

        # Verifica histórico de mensagens salvas
        self.assertEqual(Mensagem.objects.filter(sessao=self.sessao).count(), 2)

    @patch('learning.hint_service.HintService._call_external_ai')
    def test_pedir_dica_fallback_ia_sucesso(self, mock_ai):
        mock_ai.return_value = 'Pense sobre estruturas de repeticao como o loop for.'
        payload = {
            'sessao_id': str(self.sessao.id),
            'questao_id': str(self.questao_sem_dica.id),
            'pergunta': 'Como repito um codigo varias vezes?',
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['origem_resposta'], 'IA_EXTERNA')
        self.assertEqual(response.data['resposta_coach'], 'Pense sobre estruturas de repeticao como o loop for.')

    @patch('learning.hint_service.HintService._call_external_ai')
    def test_pedir_dica_resiliencia_contingencia(self, mock_ai):
        mock_ai.return_value = None  # Simula erro/timeout na IA
        payload = {
            'sessao_id': str(self.sessao.id),
            'questao_id': str(self.questao_sem_dica.id),
            'pergunta': 'Duvida sem resposta.',
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['origem_resposta'], 'CONTINGENCIA')
        self.assertIn('instabilidade momentânea', response.data['resposta_coach'])


