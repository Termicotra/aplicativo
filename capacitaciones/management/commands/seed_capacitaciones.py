from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Comando reservado. La app capacitaciones está desacoplada de evaluaciones.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'Este comando no realiza acciones. Usa el dominio correspondiente de la app capacitaciones.'
            )
        )
