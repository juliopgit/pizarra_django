from django.urls import path

from . import views

urlpatterns = [
    path('', views.pizarra, name='pizarra'),
    path('completar/<int:tarea_id>/', views.completar_tarea, name='completar_tarea'),
    path('editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('completadas/', views.historial_completadas, name='historial_completadas'),
    path('completada/<int:tarea_id>/', views.detalle_completada, name='detalle_completada'),
]
