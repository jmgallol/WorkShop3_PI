import numpy as np
from django.core.management.base import BaseCommand, CommandError
from movie.models import Movie

class Command(BaseCommand):
    help = "Muestra los primeros valores del embedding de una película."

    def add_arguments(self, parser):
        parser.add_argument("--title", type=str, required=False, help="Título exacto")
        parser.add_argument("--rand", action="store_true", help="Tomar una película al azar")

    def handle(self, *args, **opts):
        if opts.get("rand"):
            m = Movie.objects.order_by("?").first()
        elif opts.get("title"):
            try:
                m = Movie.objects.get(title=opts["title"])
            except Movie.DoesNotExist:
                raise CommandError(f"No encontrada: {opts['title']}")
        else:
            raise CommandError("Usa --title 'Nombre' o --rand")

        vec = np.frombuffer(m.emb, dtype=np.float32)
        self.stdout.write(f"{m.title} | dim={vec.size} | head={vec[:8]}")
