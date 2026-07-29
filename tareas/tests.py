from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import PostIt


class TareasPermissionsTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass123')
		self.user = User.objects.create_user(username='usuario', password='userpass123')
		self.other_user = User.objects.create_user(username='otro', password='otherpass123')

		self.user_task = PostIt.objects.create(
			titulo='Tarea propia',
			contenido='Pendiente del usuario',
			asignado_a=self.user,
		)
		self.other_task = PostIt.objects.create(
			titulo='Tarea ajena',
			contenido='Pendiente de otro usuario',
			asignado_a=self.other_user,
		)
		self.completed_task = PostIt.objects.create(
			titulo='Tarea completada',
			contenido='Ya finalizada',
			asignado_a=self.user,
			completada=True,
		)

	def test_usuario_normal_ve_solo_sus_pendientes(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('pizarra'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerySetEqual(
			response.context['postits'],
			[repr(self.user_task)],
			transform=repr,
		)

	def test_usuario_normal_ve_solo_su_historial(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('historial_completadas'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerySetEqual(
			response.context['postits'],
			[repr(self.completed_task)],
			transform=repr,
		)

	def test_usuario_normal_no_puede_crear_editar_o_eliminar(self):
		self.client.force_login(self.user)

		create_response = self.client.post(
			reverse('pizarra'),
			{
				'titulo': 'Nueva',
				'contenido': 'Contenido',
				'color': '#fff740',
				'asignado_a': self.user.id,
			},
		)
		edit_response = self.client.post(
			reverse('editar_tarea', args=[self.user_task.id]),
			{
				'titulo': 'Editada',
				'contenido': 'Contenido editado',
				'color': '#fff740',
				'asignado_a': self.other_user.id,
			},
		)
		delete_response = self.client.get(reverse('eliminar_tarea', args=[self.user_task.id]))

		self.assertEqual(create_response.status_code, 403)
		self.assertEqual(edit_response.status_code, 403)
		self.assertEqual(delete_response.status_code, 403)

	def test_usuario_normal_solo_puede_completar_sus_tareas(self):
		self.client.force_login(self.user)

		own_response = self.client.get(reverse('completar_tarea', args=[self.user_task.id]))
		other_response = self.client.get(reverse('completar_tarea', args=[self.other_task.id]))

		self.assertEqual(own_response.status_code, 302)
		self.assertEqual(other_response.status_code, 404)
		self.user_task.refresh_from_db()
		self.assertTrue(self.user_task.completada)

	def test_superusuario_ve_todas_las_tareas_y_puede_asignar_al_crear(self):
		self.client.force_login(self.admin)
		response = self.client.get(reverse('pizarra'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['postits'].count(), 2)

		create_response = self.client.post(
			reverse('pizarra'),
			{
				'titulo': 'Asignada por admin',
				'contenido': 'Nueva tarea',
				'color': '#fff740',
				'asignado_a': self.user.id,
			},
		)

		self.assertEqual(create_response.status_code, 302)
		self.assertTrue(PostIt.objects.filter(titulo='Asignada por admin', asignado_a=self.user).exists())

	def test_superusuario_si_edita_una_tarea_se_reasigna_al_usuario_por_defecto(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse('editar_tarea', args=[self.user_task.id]),
			{
				'titulo': 'Tarea propia editada',
				'contenido': 'Sigue pendiente',
				'color': '#ff7eb9',
				'asignado_a': self.other_user.id,
			},
		)

		self.assertEqual(response.status_code, 302)
		self.user_task.refresh_from_db()
		self.assertEqual(self.user_task.asignado_a_id, self.other_user.id)

	def test_usuario_normal_recibe_forbidden_si_intenta_entrar_al_admin(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('admin:index'))

		self.assertEqual(response.status_code, 403)

	def test_superusuario_puede_entrar_al_admin_y_ve_boton_en_la_pizarra(self):
		self.client.force_login(self.admin)

		admin_response = self.client.get(reverse('admin:index'))
		pizarra_response = self.client.get(reverse('pizarra'))

		self.assertEqual(admin_response.status_code, 200)
		self.assertContains(pizarra_response, reverse('admin:index'))

	def test_usuario_normal_no_ve_boton_del_admin(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('pizarra'))

		self.assertNotContains(response, reverse('admin:index'))
