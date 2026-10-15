from django.core.management.base import BaseCommand

from userManagement.models import Interesse

INTERESSES_PADRAO = [
    'Python',
    'JavaScript',
    'TypeScript',
    'Frontend',
    'Backend',
    'Banco de Dados',
    'Inteligência Artificial',
    'Ciência de Dados',
    'DevOps/Cloud',
    'Algoritmos',
]


class Command(BaseCommand):
    help = 'Cadastra os interesses padrão de tecnologia no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de interesses...')

        for nome in INTERESSES_PADRAO:
            _, created = Interesse.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Criado: '{nome}'"))
            else:
                self.stdout.write(f"  Já existe: '{nome}'")

        self.stdout.write(self.style.SUCCESS('Seed de interesses concluído.'))
