import logging
from typing import Dict, Any

from django.db import transaction

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import MemoriaPedagogicaUsuario

logger = logging.getLogger(__name__)

# Limiares de classificação pedagógica determinística
LIMIAR_DOMINIO_PERCENT = 80.0
LIMIAR_DIFICULDADE_PERCENT = 60.0
MIN_QUESTOES_PARA_PONTO_FORTE = 1


class PedagogicalMemoryService:
    """
    Serviço determinístico de consolidação e síntese pedagógica contínua do estudante (VAR-118).
    
    Analisa o histórico de submissões (RespostaQuestao) a partir da última execução
    de cada atividade já realizada, classificando módulos/tópicos dominados (>= 80%)
    e tópicos com reincidência de vulnerabilidade (< 60%).
    """

    @classmethod
    def consolidar_perfil(cls, usuario) -> MemoriaPedagogicaUsuario:
        """
        Consolida atomicamente a memória pedagógica do estudante com base nas últimas execuções.
        """
        # 1. Recupera o ID da última execução de cada atividade realizada pelo usuário
        ultimas_execucoes_ids = list(
            ExecucaoAtividade.objects.filter(usuario=usuario)
            .order_by("atividade_id", "-executado_em")
            .distinct("atividade_id")
            .values_list("id", flat=True)
        )

        total_atividades = len(ultimas_execucoes_ids)

        if total_atividades == 0:
            with transaction.atomic():
                memoria, _ = MemoriaPedagogicaUsuario.objects.update_or_create(
                    usuario=usuario,
                    defaults={
                        "pontos_fortes": [],
                        "topicos_dificuldade": [],
                        "total_atividades_avaliadas": 0,
                        "taxa_acerto_geral": 0.0,
                        "resumo_perfil_didatico": "Estudante ainda não realizou atividades avaliadas.",
                    },
                )
            return memoria

        # 2. Busca todas as respostas das últimas execuções vinculadas aos módulos
        respostas = (
            RespostaQuestao.objects.filter(execucao_id__in=ultimas_execucoes_ids)
            .select_related("execucao__atividade__modulo")
        )

        total_questoes_geral = 0
        total_acertos_geral = 0
        agregados_por_modulo: Dict[str, Dict[str, Any]] = {}

        for resposta in respostas:
            modulo = resposta.execucao.atividade.modulo
            agregado = agregados_por_modulo.setdefault(
                str(modulo.id),
                {"titulo": modulo.titulo, "total": 0, "acertos": 0},
            )
            agregado["total"] += 1
            total_questoes_geral += 1
            if resposta.correta:
                agregado["acertos"] += 1
                total_acertos_geral += 1

        pontos_fortes = []
        topicos_dificuldade = []

        for dados in agregados_por_modulo.values():
            if dados["total"] == 0:
                continue
            taxa_acerto = round((dados["acertos"] * 100.0) / dados["total"], 1)
            
            # Se atingiu o limiar de domínio e respondeu ao menos o mínimo de questões
            if taxa_acerto >= LIMIAR_DOMINIO_PERCENT and dados["total"] >= MIN_QUESTOES_PARA_PONTO_FORTE:
                pontos_fortes.append({
                    "topico": dados["titulo"],
                    "taxa_acerto": taxa_acerto,
                    "questoes_avaliadas": dados["total"],
                })
            elif taxa_acerto < LIMIAR_DIFICULDADE_PERCENT:
                topicos_dificuldade.append({
                    "topico": dados["titulo"],
                    "taxa_acerto": taxa_acerto,
                    "questoes_avaliadas": dados["total"],
                })

        # Ordenar pontos fortes do maior acerto para o menor
        pontos_fortes.sort(key=lambda x: x["taxa_acerto"], reverse=True)
        # Ordenar tópicos de dificuldade do menor acerto (mais crítico) para o maior
        topicos_dificuldade.sort(key=lambda x: x["taxa_acerto"])

        taxa_acerto_geral = 0.0
        if total_questoes_geral > 0:
            taxa_acerto_geral = round((total_acertos_geral * 100.0) / total_questoes_geral, 1)

        resumo_texto = cls._gerar_resumo_textual(
            total_atividades=total_atividades,
            taxa_acerto_geral=taxa_acerto_geral,
            pontos_fortes=pontos_fortes,
            topicos_dificuldade=topicos_dificuldade,
        )

        with transaction.atomic():
            memoria, _ = MemoriaPedagogicaUsuario.objects.update_or_create(
                usuario=usuario,
                defaults={
                    "pontos_fortes": [pf["topico"] for pf in pontos_fortes],
                    "topicos_dificuldade": [td["topico"] for td in topicos_dificuldade],
                    "total_atividades_avaliadas": total_atividades,
                    "taxa_acerto_geral": taxa_acerto_geral,
                    "resumo_perfil_didatico": resumo_texto,
                },
            )

        logger.info(
            "Memória pedagógica consolidada para usuário %s: %d fortes, %d a reforçar, taxa geral %.1f%%",
            usuario.id,
            len(pontos_fortes),
            len(topicos_dificuldade),
            taxa_acerto_geral,
        )
        return memoria

    @classmethod
    def obter_ou_consolidar(cls, usuario) -> MemoriaPedagogicaUsuario:
        """
        Recupera a memória pedagógica existente ou consolida uma nova se ainda não existir.
        """
        memoria = getattr(usuario, "memoria_pedagogica", None)
        if memoria is not None:
            return memoria
        return cls.consolidar_perfil(usuario)

    @staticmethod
    def _gerar_resumo_textual(
        total_atividades: int,
        taxa_acerto_geral: float,
        pontos_fortes: list,
        topicos_dificuldade: list,
    ) -> str:
        partes = [f"Estudante realizou {total_atividades} atividades com {taxa_acerto_geral}% de acerto geral."]
        if pontos_fortes:
            topicos_pf = ", ".join(pf["topico"] for pf in pontos_fortes[:3])
            partes.append(f"Domínio demonstrado em: {topicos_pf}.")
        if topicos_dificuldade:
            topicos_td = ", ".join(td["topico"] for td in topicos_dificuldade[:3])
            partes.append(f"Recomenda-se reforço em: {topicos_td}.")
        return " ".join(partes)
