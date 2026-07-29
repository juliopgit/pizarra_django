from django.db import models
from django.contrib.auth.models import User

class PostIt(models.Model):
	COLORES_CHOICES = [
		('#fff740', 'Amarillo'),
		('#ff7eb9', 'Rosa'),
		('#7afcff', 'Azul'),
		('#98ff98', 'Verde'),
	]

	titulo = models.CharField(max_length=100)
	contenido = models.TextField(blank=True)
	color = models.CharField(max_length=7, choices=COLORES_CHOICES, default='#fff740')
	creado_el = models.DateTimeField(auto_now_add=True)
	completada = models.BooleanField(default=False)
	asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postits')

	def __str__(self):
		return self.titulo
