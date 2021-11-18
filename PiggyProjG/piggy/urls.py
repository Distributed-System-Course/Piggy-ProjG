from django.urls import path

from . import views

app_name = 'piggy'

urlpatterns = [
    # example: '/', '/index'
    path('', views.index, name='index'),
    
    # example: '/plans/', a.k.a. project groups
    path('plans/', views.plans, name='plans'),
    path('plan/<int:plan_id>', views.plan_detail, name='plan_detail'),
    path('plan/<int:plan_id>/join', views.join_plan, name='join_plan'),
    
    # example: '/projects/'
    path('projects/', views.projects, name='projects'),
    path('project/<int:project_id>', views.project_detail, name='project_detail'),

    # example: '/teacher/'
    path('teachers/', views.teachers, name='teachers'),
    path('teacher/<int:teacher_id>', views.teacher_detail, name='teacher_detail'),

]
