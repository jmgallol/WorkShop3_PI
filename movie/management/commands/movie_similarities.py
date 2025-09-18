import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from movie.models import Movie
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"

class Command(BaseCommand):
    help = (
        "Calcula similitud de coseno entre descripciones de películas "
        "y opcionalmente contra un prompt usando embeddings de OpenAI."
    )

    def add_arguments(self, parser):
        parser.add_argument("--m1", type=str, default="La lista de Schindler",
                            help="Título de la primera película")
        parser.add_argument("--m2", type=str, default="El club de la pelea",
                            help="Título de la segunda película")
        parser.add_argument("--prompt", type=str, default="película sobre la Segunda Guerra Mundial",
                            help="Texto libre para comparar contra m1 y m2")

    def handle(self, *args, **opts):
        if not settings.OPENAI_API_KEY:
            raise CommandError("Falta OPENAI_API_KEY en settings/.env")

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # --- helpers ---
        def get_embedding(text: str) -> np.ndarray:
            # Limpieza mínima por si hay saltos de línea largos
            text = " ".join((text or "").split())
            resp = client.embeddings.create(
                model=EMBED_MODEL,
                input=[text]
            )
            return np.array(resp.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0:
                return 0.0
            return float(np.dot(a, b) / denom)

        # --- obtener películas ---
        m1_title = opts["m1"]
        m2_title = opts["m2"]
        prompt_text = opts["prompt"]

        try:
            movie1 = Movie.objects.get(title=m1_title)
        except Movie.DoesNotExist:
            raise CommandError(f"No encontrada m1: '{m1_title}'")

        try:
            movie2 = Movie.objects.get(title=m2_title)
        except Movie.DoesNotExist:
            raise CommandError(f"No encontrada m2: '{m2_title}'")

        # --- embeddings de descripciones ---
        emb1 = get_embedding(movie1.description or movie1.title)
        emb2 = get_embedding(movie2.description or movie2.title)

        sim12 = cosine_similarity(emb1, emb2)
        self.stdout.write(f"🎬 {movie1.title} vs {movie2.title}: {sim12:.4f}")

        # --- prompt vs películas ---
        if prompt_text:
            prompt_emb = get_embedding(prompt_text)
            sim_p_m1 = cosine_similarity(prompt_emb, emb1)
            sim_p_m2 = cosine_similarity(prompt_emb, emb2)
            self.stdout.write(f"📝 Prompt: {prompt_text}")
            self.stdout.write(f" Similitud prompt  vs '{movie1.title}': {sim_p_m1:.4f}")
            self.stdout.write(f" Similitud prompt  vs '{movie2.title}': {sim_p_m2:.4f}")

        self.stdout.write(self.style.SUCCESS("Listo."))

