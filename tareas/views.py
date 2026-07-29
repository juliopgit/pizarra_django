from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .models import PostIt


def _usuarios_disponibles():
	return User.objects.order_by('username')


def _postits_visibles(user):
	queryset = PostIt.objects.all()
	if not user.is_superuser:
		queryset = queryset.filter(asignado_a=user)
	return queryset


def _postits_pendientes(user):
	return _postits_visibles(user).filter(completada=False).order_by('-creado_el')


def _postits_completados(user):
	return _postits_visibles(user).filter(completada=True).order_by('-creado_el')


def login_view(request):
	if request.user.is_authenticated:
		return redirect('pizarra')

	form = AuthenticationForm(request, data=request.POST or None)

	if request.method == 'POST' and form.is_valid():
		login(request, form.get_user())
		return redirect('pizarra')

	return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
	if request.method == 'POST':
		logout(request)
		return redirect('login')

	return redirect('pizarra')


@login_required
def pizarra(request):
	if request.method == 'POST':
		if not request.user.is_superuser:
			raise PermissionDenied

		v_titulo = request.POST.get('titulo')
		v_contenido = request.POST.get('contenido')
		v_color = request.POST.get('color')
		v_asignado_a = get_object_or_404(User, id=request.POST.get('asignado_a'))

		PostIt.objects.create(titulo=v_titulo, contenido=v_contenido, color=v_color, asignado_a=v_asignado_a)
		return redirect('pizarra')

	postits_pendientes = _postits_pendientes(request.user)
	usuarios = _usuarios_disponibles() if request.user.is_superuser else []
	return render(request, 'pizarra.html', {'postits': postits_pendientes, 'usuarios': usuarios})


@login_required
def completar_tarea(request, tarea_id):
	queryset = PostIt.objects.filter(completada=False)
	if not request.user.is_superuser:
		queryset = queryset.filter(asignado_a=request.user)
	tarea = get_object_or_404(queryset, id=tarea_id)
	tarea.completada = True
	tarea.save()
	return redirect('pizarra')


@login_required
def editar_tarea(request, tarea_id):
	if not request.user.is_superuser:
		raise PermissionDenied

	tarea = get_object_or_404(PostIt, id=tarea_id, completada=False)
	usuarios = _usuarios_disponibles()

	if request.method == 'POST':
		tarea.titulo = request.POST.get('titulo')
		tarea.contenido = request.POST.get('contenido')
		tarea.color = request.POST.get('color')
		tarea.asignado_a = get_object_or_404(User, id=request.POST.get('asignado_a'))
		tarea.save()
		return redirect('pizarra')

	return render(request, 'editar.html', {'tarea': tarea, 'usuarios': usuarios})


@login_required
def eliminar_tarea(request, tarea_id):
	if not request.user.is_superuser:
		raise PermissionDenied

	tarea = get_object_or_404(PostIt, id=tarea_id)
	if not tarea.completada:
		tarea.delete()

	return redirect('pizarra')


@login_required
def historial_completadas(request):
	postits_completados = _postits_completados(request.user)
	return render(request, 'completadas.html', {'postits': postits_completados})


@login_required
def detalle_completada(request, tarea_id):
	queryset = PostIt.objects.filter(completada=True)
	if not request.user.is_superuser:
		queryset = queryset.filter(asignado_a=request.user)
	tarea = get_object_or_404(queryset, id=tarea_id)
	return render(request, 'detalle.html', {'tarea': tarea})
