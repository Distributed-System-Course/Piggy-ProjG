from django.urls import path

from . import views

urlpatterns = [
    # example: '/', '/index'
    path('', views.index, name='index'),
    
    # example: '/plans/', a.k.a. project groups
    path('plans/', views.plans, name='plans'),
    path('plans/<int:plan_id>', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/join', views.join_plan, name='join_plan'),
    
    # example: '/projects/'
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>', views.project_detail, name='project_detail'),
]
