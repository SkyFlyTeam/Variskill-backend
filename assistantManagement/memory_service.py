import logging
import threading
from datetime import timedelta
from typing import Dict, Any

from django.db import transaction

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import MemoriaPedagogicaUsuario

logger = logging.getLogger(__name__)

# Limiares de classificação pedagógica determinística
LIMIAR_DOMINIO_PERCENT = 80.0
LIMIAR_DIFICULDADE_PERCENT = 60.0
MIN_QUESTOES_PARA_PONTO_FORTE = 3
MIN_ERROS_PARA_REINCIDENCIA = 2
# Execuções da mesma atividade a menos disso da anterior são retentativas da mesma rodada
# (salvo a que inicia uma prática pelo "Praticar de novo" do Raio-X).
JANELA_RETENTATIVA = timedelta(hours=12)


def ids_execucoes_avaliadas(usuario) -> list:
    """
    Para cada atividade, a primeira execução da rodada mais recente. Retentativas imediatas
    ("Tentar de novo" reenvia as respostas já corretas) não apagam os erros, mas voltar à
    atividade depois, ou praticá-la pelo Raio-X, e acertar de primeira mostra que o
    estudante superou o tópico.
    """
    execucoes = (
        ExecucaoAtividade.objects.filter(usuario=usuario)
        .order_by("atividade_id", "executado_em")
        .values_list("id", "atividade_id", "executado_em", "pratica_reforco")
    )
    inicio_da_rodada = {}
    execucao_anterior = {}
    for execucao_id, atividade_id, executado_em, pratica_reforco in execucoes:
        anterior = execucao_anterior.get(atividade_id)
        if pratica_reforco or anterior is None or executado_em - anterior > JANELA_RETENTATIVA:
            inicio_da_rodada[atividade_id] = execucao_id
        execucao_anterior[atividade_id] = executado_em
    return list(inicio_da_rodada.values())


class PedagogicalMemoryService:
    """
    Serviço determinístico de consolidação e síntese pedagógica contínua do estudante (VAR-118).
    
    Analisa o histórico de submissões (RespostaQuestao) a partir da primeira execução
    da rodada mais recente de cada atividade (ver ids_execucoes_avaliadas), classificando módulos/tópicos dominados (>= 80%)
    e tópicos com reincidência de vulnerabilidade (< 60%).
    """

    @classmethod
    def consolidar_perfil(cls, usuario) -> MemoriaPedagogicaUsuario:
        """
        Consolida atomicamente a memória pedagógica do estudante com base nas execuções avaliadas.
        """
        # 1. Recupera a execução avaliada de cada atividade realizada pelo usuário
        execucoes_avaliadas_ids = ids_execucoes_avaliadas(usuario)

        total_atividades = len(execucoes_avaliadas_ids)

        if total_atividades == 0:
            with transaction.atomic():
                memoria, _ = MemoriaPedagogicaUsuario.objects.update_or_create(
                    usuario=usuario,
                    defaults={
                        "pontos_fortes": [],
                        "topicos_dificuldade": [],
                        "topicos_praticar": [],
                        "total_atividades_avaliadas": 0,
                        "taxa_acerto_geral": 0.0,
                        "resumo_perfil_didatico": "Estudante ainda não realizou atividades avaliadas.",
                    },
                )
            return memoria

        # 2. Busca todas as respostas das execuções avaliadas vinculadas aos módulos
        respostas = (
            RespostaQuestao.objects.filter(execucao_id__in=execucoes_avaliadas_ids)
            .select_related("execucao__atividade__modulo")
        )

        total_questoes_geral = 0
        total_acertos_geral = 0
        agregados_por_modulo: Dict[str, Dict[str, Any]] = {}
        execucoes_com_questoes = set()

        for resposta in respostas:
            execucoes_com_questoes.add(resposta.execucao_id)
            atividade = resposta.execucao.atividade
            modulo = atividade.modulo
            agregado = agregados_por_modulo.setdefault(
                str(modulo.id),
                {"titulo": modulo.titulo, "trilha_id": str(modulo.trilha_id), "total": 0, "acertos": 0, "atividades": {}},
            )
            # Por atividade, para indicar qual delas o estudante deve praticar de novo
            agregado_atividade = agregado["atividades"].setdefault(
                str(atividade.id), {"ordem": atividade.ordem, "total": 0, "acertos": 0},
            )
            agregado["total"] += 1
            agregado_atividade["total"] += 1
            total_questoes_geral += 1
            if resposta.correta:
                agregado["acertos"] += 1
                agregado_atividade["acertos"] += 1
                total_acertos_geral += 1

        # Considera como atividades avaliadas apenas aquelas que possuem questões
        total_atividades_avaliadas = len(execucoes_com_questoes)

        pontos_fortes = []
        topicos_dificuldade = []

        for dados in agregados_por_modulo.values():
            if dados["total"] == 0:
                continue
            taxa_acerto = round((dados["acertos"] * 100.0) / dados["total"], 1)
            erros = dados["total"] - dados["acertos"]
            
            # Se atingiu o limiar de domínio e respondeu ao menos o mínimo de questões (>= 3)
            if taxa_acerto >= LIMIAR_DOMINIO_PERCENT and dados["total"] >= MIN_QUESTOES_PARA_PONTO_FORTE:
                pontos_fortes.append({
                    "topico": dados["titulo"],
                    "taxa_acerto": taxa_acerto,
                    "questoes_avaliadas": dados["total"],
                })
            # Tópico de vulnerabilidade: taxa < 60% com reincidência de erros (>= 2 erros ou questão única com erro)
            elif taxa_acerto < LIMIAR_DIFICULDADE_PERCENT and (erros >= MIN_ERROS_PARA_REINCIDENCIA or dados["total"] == 1):
                topicos_dificuldade.append({
                    "topico": dados["titulo"],
                    "taxa_acerto": taxa_acerto,
                    "questoes_avaliadas": dados["total"],
                    "trilha_id": dados["trilha_id"],
                    "atividade_id": cls._atividade_com_menor_acerto(dados["atividades"]),
                })

        # Ordenar pontos fortes do maior acerto para o menor
        pontos_fortes.sort(key=lambda x: x["taxa_acerto"], reverse=True)
        # Ordenar tópicos de dificuldade do menor acerto (mais crítico) para o maior
        topicos_dificuldade.sort(key=lambda x: x["taxa_acerto"])

        taxa_acerto_geral = 0.0
        if total_questoes_geral > 0:
            taxa_acerto_geral = round((total_acertos_geral * 100.0) / total_questoes_geral, 1)

        resumo_texto = cls._gerar_resumo_textual(
            total_atividades=total_atividades_avaliadas,
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
                    "topicos_praticar": [
                        {"topico": td["topico"], "trilha_id": td["trilha_id"], "atividade_id": td["atividade_id"]}
                        for td in topicos_dificuldade
                    ],
                    "total_atividades_avaliadas": total_atividades_avaliadas,
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
    def consolidar_perfil_async(cls, usuario) -> None:
        """
        Dispara a consolidação da memória pedagógica em background (thread daemon)
        sem bloquear o ciclo de requisição/resposta HTTP do estudante.
        """
        user_id = getattr(usuario, "id", usuario)
        
        def _worker():
            from django.contrib.auth import get_user_model
            try:
                user_obj = get_user_model().objects.get(pk=user_id)
                cls.consolidar_perfil(user_obj)
            except Exception as exc:
                logger.error("Erro na consolidação assíncrona da memória pedagógica (usuário %s): %s", user_id, exc)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

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
    def _atividade_com_menor_acerto(atividades: Dict[str, Dict[str, Any]]) -> str:
        """Atividade do módulo com menor taxa de acerto (empate: a primeira na ordem da trilha)."""
        return min(
            atividades,
            key=lambda atividade_id: (
                atividades[atividade_id]["acertos"] / atividades[atividade_id]["total"],
                atividades[atividade_id]["ordem"],
            ),
        )

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
