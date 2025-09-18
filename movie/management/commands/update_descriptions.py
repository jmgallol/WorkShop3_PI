from django.core.management.base import BaseCommand
from movie.models import Movie
from django.conf import settings
from openai import OpenAI

class Command(BaseCommand):
    help = "Actualiza la descripción de UNA película usando OpenAI (NO quitar el break)."

    def handle(self, *args, **kwargs):
        # ✅ Inicializar cliente dentro de handle()
        if not settings.OPENAI_API_KEY:
            self.stderr.write("No hay API Key en settings.OPENAI_API_KEY")
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        def get_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return resp.choices[0].message.content.strip()

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
            "debe incluir el género de la película y cualquier información adicional que sirva "
            "para crear un sistema de recomendación."
        )

        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write("No hay películas en la base de datos.")
            return

        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")
            try:
                prompt = (
                    f"{instruction} "
                    f"Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
                )
                updated = get_completion(prompt)
                movie.description = updated
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")
            break  # NO quitar
