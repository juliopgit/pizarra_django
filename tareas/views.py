from django.shortcuts import get_object_or_404, redirect, render

from .models import PostIt


def pizarra(request):
	if request.method == 'POST':
		v_titulo = request.POST.get('titulo')
		v_contenido = request.POST.get('contenido')
		v_color = request.POST.get('color')

		PostIt.objects.create(titulo=v_titulo, contenido=v_contenido, color=v_color)
		return redirect('pizarra')

	postits_pendientes = PostIt.objects.filter(completada=False).order_by('-creado_el')
	return render(request, 'pizarra.html', {'postits': postits_pendientes})


def completar_tarea(request, tarea_id):
	tarea = get_object_or_404(PostIt, id=tarea_id)
	tarea.completada = True
	tarea.save()
	return redirect('pizarra')


def editar_tarea(request, tarea_id):
	tarea = get_object_or_404(PostIt, id=tarea_id)

	if tarea.completada:
		return redirect('pizarra')

	if request.method == 'POST':
		tarea.titulo = request.POST.get('titulo')
		tarea.contenido = request.POST.get('contenido')
		tarea.color = request.POST.get('color')
		tarea.save()
		return redirect('pizarra')

	return render(request, 'editar.html', {'tarea': tarea})


def eliminar_tarea(request, tarea_id):
	tarea = get_object_or_404(PostIt, id=tarea_id)
	if not tarea.completada:
		tarea.delete()

	return redirect('pizarra')


def historial_completadas(request):
	postits_completados = PostIt.objects.filter(completada=True).order_by('-creado_el')
	return render(request, 'completadas.html', {'postits': postits_completados})


def detalle_completada(request, tarea_id):
	tarea = get_object_or_404(PostIt, id=tarea_id)
	return render(request, 'detalle.html', {'tarea': tarea})
