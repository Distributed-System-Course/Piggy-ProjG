from django.urls import path

from . import views

app_name = 'piggy'

urlpatterns = [
    # example: '/', '/index'
    path('', views.index, name='index'),
    
    # example: '/plans/', a.k.a. project groups
    path('plans/', views.plans, name='plans'),
    path('plan/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plan/<int:plan_id>/join/', views.join_plan, name='join_plan'),
    path('plan/<int:plan_id>/start/', views.start_plan, name='start_plan'),
    path('plan/<int:plan_id>/stop/', views.stop_plan, name='stop_plan'),
    
    # example: '/projects/'
    path('projects/', views.projects, name='projects'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),

    # example: '/teacher/'
    path('teachers/', views.teachers, name='teachers'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),

    # example: '/team/'
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/wish/', views.team_wish, name='team_wish'),
    path('team/<int:team_id>/join/', views.join_team, name='join_team'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
