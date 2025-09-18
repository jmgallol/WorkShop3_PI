import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Asigna imágenes existentes en media/movie/images a cada película."

    def _candidatos(self, title: str):
        yield f"m_{title}.png"
        yield f"m_{title}.jpg"
        s = slugify(title, allow_unicode=True)
        yield f"m_{s}.png"
        yield f"m_{s}.jpg"

    def handle(self, *args, **kwargs):
        base_dir = Path(settings.MEDIA_ROOT) / "movie" / "images"
        if not base_dir.exists():
            self.stderr.write(f"No existe la carpeta: {base_dir}")
            return

        qs = Movie.objects.all()
        if not qs.exists():
            self.stdout.write("No hay películas.")
            return

        updated = 0
        for m in qs:
            found = None
            for name in self._candidatos(m.title):
                p = base_dir / name
                if p.exists():
                    found = p
                    break

            if not found:
                self.stderr.write(f"Imagen no encontrada para: {m.title}")
                continue

            rel = os.path.join("movie", "images", found.name)  # ruta relativa a MEDIA_ROOT
            m.image = rel
            m.save()
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"Updated: {m.title} -> {rel}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. Updated {updated} movies."))