from django.conf import settings
from django.db import migrations, models


def asignar_usuario_por_defecto(apps, schema_editor):
	PostIt = apps.get_model('tareas', 'PostIt')
	Usuario = apps.get_model('auth', 'User')

	if not PostIt.objects.exists():
		return

	usuario, _ = Usuario.objects.get_or_create(
		pk=1,
		defaults={
			'username': 'usuario_default',
			'email': 'usuario_default@example.com',
		},
	)
	PostIt.objects.filter(asignado_a__isnull=True).update(asignado_a=usuario)


class Migration(migrations.Migration):

	dependencies = [
		('tareas', '0001_initial'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.AddField(
			model_name='postit',
			name='asignado_a',
			field=models.ForeignKey(null=True, on_delete=models.CASCADE, related_name='postits', to=settings.AUTH_USER_MODEL),
		),
		migrations.RunPython(asignar_usuario_por_defecto, migrations.RunPython.noop),
	]
