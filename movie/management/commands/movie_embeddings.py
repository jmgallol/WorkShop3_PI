import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"

class Command(BaseCommand):
    help = "Genera embeddings de las descripciones y los almacena en Movie.emb"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None, help="Cantidad máxima a procesar")

    def handle(self, *args, **opts):
        if not settings.OPENAI_API_KEY:
            self.stderr.write("Falta OPENAI_API_KEY en .env/settings.")
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        def get_embedding(text: str) -> np.ndarray:
            text = " ".join((text or "").split())
            r = client.embeddings.create(model=EMBED_MODEL, input=[text])
            return np.array(r.data[0].embedding, dtype=np.float32)

        qs = Movie.objects.all()
        if opts["limit"]:
            qs = qs[:opts["limit"]]

        self.stdout.write(f"Found {qs.count()} movies")
        for m in qs:
            emb = get_embedding(m.description or m.title)
            m.emb = emb.tobytes()
            m.save(update_fields=["emb"])
            self.stdout.write(self.style.SUCCESS(f"👌 Embedding stored for: {m.title}"))

        self.stdout.write(self.style.SUCCESS("🌟 Finished generating embeddings."))
