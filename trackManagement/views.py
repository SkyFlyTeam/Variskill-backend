from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from activityManagement.models import Atividade
from .models import Matricula, ProgressoModulo, Trilha

class RoadmapView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, trilha_id):
        trilha = get_object_or_404(Trilha, pk=trilha_id, ativo=True)
        matricula = Matricula.objects.filter(usuario=request.user, trilha=trilha, status='EM_ANDAMENTO').first()
        progress = {p.modulo_id: p.status for p in ProgressoModulo.objects.filter(matricula=matricula)} if matricula else {}
        modules = list(trilha.modulos.all().order_by('ordem_modulo'))
        activities = Atividade.objects.filter(modulo_id__in=[m.pk for m in modules], ativo=True).select_related('conteudo').order_by('ordem')
        by_module = {}
        for a in activities: by_module.setdefault(a.modulo_id, []).append(a)
        done = set(Atividade.objects.filter(execucoes__usuario=request.user, execucoes__aprovado=True, modulo_id__in=by_module).values_list('pk', flat=True)) if matricula else set()
        result, recommended, completed, total = [], None, 0, 0
        for module in modules:
            module_status = progress.get(module.pk, 'BLOQUEADO') if matricula else 'BLOQUEADO'
            unlocked, output = module_status != 'BLOQUEADO' and matricula is not None, []
            for a in by_module.get(module.pk, []):
                total += 1
                if a.pk in done: status = 'CONCLUIDO'; completed += 1
                elif unlocked:
                    status, unlocked = 'EM_ANDAMENTO', False
                    if recommended is None: recommended = {'id': a.pk, 'titulo': a.titulo, 'modulo_id': module.pk}
                else: status = 'BLOQUEADO'
                output.append({'id': a.pk, 'titulo': a.titulo, 'contexto_avaliacao': a.contexto_avaliacao, 'status': status, 'xp_recompensa': a.xp_recompensa, 'conteudo_teorico': ({'id': a.conteudo.pk, 'titulo': a.conteudo.titulo} if a.conteudo else None)})
            if module_status == 'CONCLUIDO' or (output and all(a['status'] == 'CONCLUIDO' for a in output)): module_status = 'CONCLUIDO'
            result.append({'id': module.pk, 'titulo': module.titulo, 'nivel': module.nivel, 'status': module_status, 'atividades': output})
        return Response({'trilha': {'id': trilha.pk, 'titulo': trilha.titulo, 'habilidade': trilha.habilidade}, 'percentual_conclusao': round(completed * 100 / total, 1) if total else 0.0, 'modulos': result, 'proxima_atividade_recomendada': recommended})
