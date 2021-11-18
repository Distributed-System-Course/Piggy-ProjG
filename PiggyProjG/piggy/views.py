from django.core.checks import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from django.http import HttpResponse

from .models import *

# Create your views here.

def index(request):
    return render(
        request,
        'piggy/index.html',  # Relative path from the 'templates' folder to the template file
        {
            'content': "Now is " + timezone.localtime().strftime(("%Y/%m/%d, %H:%M:%S")) + ".",
        }
    )


def plans(request):
    all_plans = Plan.objects.all()
    return render(
        request, 
        'piggy/plans.html', 
        {
            'all_plans': all_plans,
        }
    )


def plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    return render(
        request,
        'piggy/plan_detail.html',
        {
            'plan': plan
        }
    )


def join_plan(request, plan_id):
        return render(
        request,
        'piggy/join_plan.html',
        {
            
        }
    )


def projects(request):
    all_plans = Plan.objects.all()
    return render(
        request,
        'piggy/projects.html',
        {
            'all_plans': all_plans, 
        }
    )


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(
        request, 
        'piggy/project_detail.html', 
        {
            'project': project,
            'max_group_num': project.max_group_num,
            'max_team_member_num': project.max_team_member_num,
        }
    )


def teachers(request):
    teachers = Teacher.objects.all()
    return render(
        request,
        'piggy/teachers.html',
        {
            'teachers': teachers,
        }
    )


def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    return render(
        request,
        'piggy/teacher_detail.html',
        {
            'teacher': teacher,
        }
    )


def team(request, team_id):
    pass


def team_wish(request, team_id):
    MAX_WISH_NUM = 3
    # all projects avalaible for current team

    team = get_object_or_404(Team, pk=team_id)
    if request.method == "POST":
        # TO-DO: permission check
        # check if the project is expired
        if team.project_group.is_expired:
            messages.Error('Your plan no longer allow wish modification.')

        for i in range(1, MAX_WISH_NUM + 1):
            key_name = 'wish' + str(i)
            project_id = int(request.POST[key_name])
            teamwish = TeamWish.objects.get_or_create(team_id=team_id, priority=i)[0]
            teamwish.project = Project.objects.get(id=project_id)
            teamwish.save()
        
        return HttpResponse(redirect('piggy:team_wish', team_id))
    
    choices = team.project_group.project_set.all()

    team_wishes = TeamWish.objects.filter(team_id=team_id)

    wishlist = [""] * MAX_WISH_NUM

    for wish in team_wishes:
        if wish.priority <= MAX_WISH_NUM:
            wishlist[wish.priority - 1] = wish.project.name

    return render(
        request,
        "piggy/team_wish.html",
        {
            'team': team,
            'choices': choices,
            'num_range': range(1, MAX_WISH_NUM + 1),
            'wishlist': wishlist,
        },
    )
