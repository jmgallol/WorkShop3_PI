from django.db import models
import numpy as np
# create your models here

class Movie(models.Model): 
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250) 
    image = models.ImageField(upload_to='movie/images/') 
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self): 
        return self.title



def default_emb_bytes():
    # vector cero float32 (dimensión 1536 del modelo text-embedding-3-small)
    return np.zeros(1536, dtype=np.float32).tobytes()

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1500)
    image = models.ImageField(upload_to='movie/images/', default='movie/images/default.jpg')
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)
    emb = models.BinaryField(default=default_emb_bytes)  # callable, sin paréntesis

    def __str__(self):
        return self.title