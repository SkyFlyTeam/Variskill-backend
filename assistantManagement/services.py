from rest_framework.exceptions import NotFound, ValidationError
from assistantManagement.models import Sessao
from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from activityManagement.models import Atividade


def decidir_nivel_trilha(usuario, sessao_id, trilha_id, opcao):
    sessao = Sessao.objects.filter(id=sessao_id, usuario=usuario).first()
    if not sessao:
        raise NotFound("Sessão do assistente não encontrada para este usuário.")

    trilha = Trilha.objects.filter(id=trilha_id).first()
    if not trilha:
        raise NotFound("Trilha não encontrada.")

    if opcao == "TESTE_DIAGNOSTICO":
        atividade_diagnostica = Atividade.objects.filter(
            modulo__trilha=trilha,
            contexto_avaliacao="DIAGNOSTICO_INICIAL",
            ativo=True
        ).first()

        if not atividade_diagnostica:
            raise ValidationError({
                "trilha_id": "Nenhuma atividade diagnóstica encontrada para esta trilha."
            })

        return {
            "acao": "INICIAR_TESTE_DIAGNOSTICO",
            "mensagem_assistente": f"Excelente desafio! Preparei uma bateria rápida para calibrarmos seu nível em {trilha.titulo}. Clique no botão abaixo para começar:",
            "atividade_diagnostica_id": str(atividade_diagnostica.id),
            "redirecionar_para": f"/atividades/{atividade_diagnostica.id}"
        }

    # Opções 'INICIO' ou 'INICIAR_DO_INICIO'
    matricula, _ = Matricula.objects.get_or_create(
        usuario=usuario,
        trilha=trilha,
        defaults={"status": "EM_ANDAMENTO"}
    )
    if matricula.status != "EM_ANDAMENTO":
        matricula.status = "EM_ANDAMENTO"
        matricula.save()

    modulos = Modulo.objects.filter(trilha=trilha).order_by("ordem_modulo")
    for index, modulo in enumerate(modulos):
        status_modulo = "EM_ANDAMENTO" if index == 0 else "BLOQUEADO"
        progresso, created = ProgressoModulo.objects.get_or_create(
            matricula=matricula,
            modulo=modulo,
            defaults={"status": status_modulo}
        )
        if not created and index == 0 and progresso.status == "BLOQUEADO":
            progresso.status = "EM_ANDAMENTO"
            progresso.save()

    primeiro_modulo = modulos.first()
    primeira_atividade = None
    if primeiro_modulo:
        primeira_atividade = Atividade.objects.filter(
            modulo=primeiro_modulo,
            ativo=True
        ).exclude(
            contexto_avaliacao="DIAGNOSTICO_INICIAL"
        ).order_by("ordem").first()

    primeira_atividade_id = str(primeira_atividade.id) if primeira_atividade else None
    redirecionar_para = f"/atividades/{primeira_atividade_id}" if primeira_atividade_id else f"/trilhas/{trilha.id}"

    response_data = {
        "acao": "INICIAR_DO_INICIO",
        "mensagem_assistente": f"Ótima escolha! Sua matrícula na trilha '{trilha.titulo}' foi efetuada e você já pode começar a primeira atividade.",
        "redirecionar_para": redirecionar_para
    }
    if primeira_atividade_id:
        response_data["primeira_atividade_id"] = primeira_atividade_id

    return response_data

