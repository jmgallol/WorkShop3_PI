import os
import base64
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie
from openai import OpenAI

class Command(BaseCommand):
    help = "Genera UNA imagen con OpenAI para la primera película y actualiza el campo image (NO quitar el break)."

    def handle(self, *args, **kwargs):
        # ✅ Verifica que la API Key esté cargada desde settings.py
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            self.stderr.write("Falta OPENAI_API_KEY en .env o en settings.")
            return

        client = OpenAI(api_key=api_key)

        # ✅ Carpeta destino para guardar imágenes
        images_dir = Path(settings.MEDIA_ROOT) / "movie" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # ✅ Consulta todas las películas
        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write("No hay películas en la base de datos.")
            return

        self.stdout.write(f"Found {movies.count()} movies")

        # ✅ Procesa SOLO la primera película
        for movie in movies:
            try:
                rel_path = self._generate_and_save_image(client, movie.title, images_dir)
                movie.image = rel_path   # guarda la ruta relativa respecto a MEDIA_ROOT
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")
            break  # 👈 NO quitar

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))

    # -------- Helpers --------
    def _safe_filename(self, title: str) -> str:
        """Genera un nombre de archivo seguro a partir del título."""
        bad = '<>:"/\\|?*'
        cleaned = "".join("_" if c in bad else c for c in title).strip()
        return f"m_{cleaned}.png"

    def _generate_and_save_image(self, client, movie_title: str, save_dir: Path) -> str:
        """Genera imagen con OpenAI, la guarda en disco y retorna la ruta relativa."""
        prompt = f"Movie poster of {movie_title}"

        # ⚠️ Usa gpt-image-1 por defecto. Si tu profe pide dall-e-2, cambia el modelo y deja quality="high"
        response = client.images.generate(
          model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),  # o "dall-e-2" si te lo exigen
          prompt=prompt,
          size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),      # válidos: "1024x1024", "1024x1536", "1536x1024", "auto"
          n=1,
        )

        data = response.data[0]
        filename = self._safe_filename(movie_title)
        full_path = save_dir / filename

        # ✅ Caso 1: respuesta con URL (dall-e-2)
        if getattr(data, "url", None):
            r = requests.get(data.url, timeout=60)
            r.raise_for_status()
            full_path.write_bytes(r.content)
        # ✅ Caso 2: respuesta con base64 (gpt-image-1)
        elif getattr(data, "b64_json", None):
            full_path.write_bytes(base64.b64decode(data.b64_json))
        else:
            raise RuntimeError("Respuesta inesperada: no trae ni url ni b64_json.")

        # Ruta relativa que Django puede servir (MEDIA_URL + esta ruta)
        return os.path.join("movie", "images", filename)
