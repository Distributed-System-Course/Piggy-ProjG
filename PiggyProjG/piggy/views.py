from django.core.checks import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from django.http import HttpResponse

from .models import *

# Create your views here.

def get_user_context(request):
    context = dict()

    try:
        username = request.session['username']
        role = request.session['role']
        if role == 'student':
            context['uu'] = get_object_or_404(Student, username=username)
            context['role'] = 'Student'
            context['is_student'] = True
            context['is_professor'] = False

        elif role == 'Professor':
            context['uu'] = get_object_or_404(Teacher, username=username)
            context['role'] = 'Professor'
            context['is_student'] = False
            context['is_professor'] = True
    except:
        pass
    
    return context


def index(request):
    context = get_user_context(request)

    return render(
        request,
        'piggy/index.html',  # Relative path from the 'templates' folder to the template file
        context
    )


def start_plan(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    try:
        username = request.session['username']
        if plan.teacher.username == username:
            plan.is_expired = False
        return HttpResponseRedirect('piggy:plan', plan_id)
    except:
        return HttpResponse('Permission denied.')


def stop_plan(request, plan_id):
    pass

def plans(request):
    context = get_user_context(request)
    all_plans = Plan.objects.all()
    context['all_plans'] = all_plans
    return render(
        request, 
        'piggy/plans.html', 
        context
    )


def plan_detail(request, plan_id):
    context = get_user_context(request)
    
    plan = get_object_or_404(Plan, pk=plan_id)
    teams = Team.objects.filter(project_group_id=plan_id)
    context['plan'] = plan
    context['teams'] = teams

    return render(
        request,
        'piggy/plan_detail.html',
        context
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
    context = get_user_context(request)
    context['all_plans'] = all_plans
    return render(
        request,
        'piggy/projects.html',
        context,
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
    context = get_user_context(request)
    context['teachers'] = teachers
    return render(
        request,
        'piggy/teachers.html',
        context,
    )


def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    all_plans = Plan.objects.filter(teacher_id=teacher_id)
    return render(
        request,
        'piggy/teacher_detail.html',
        {
            'teacher': teacher,
            'all_plans': all_plans
        }
    )


def team_detail(request, team_id):
    context = get_user_context(request)
    team = get_object_or_404(Team, pk=team_id)
    context['team'] = team
    return render(
        request,
        'piggy/team_detail.html',
        context
    )


def join_team(request, team_id):
    context = get_user_context(request)
    team = get_object_or_404(Team, pk=team_id)
    try:
        if context['is_student']:
            team.members.objects.add(context['uu'])
            team.save()
        return HttpResponse(redirect('piggy:team', team_id))
    except:
        return HttpResponse('Permission denied.')
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

def login(request):
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']

        if role == 'student':
            matches = Student.objects.filter(username=username)
        elif role == 'professor':
            matches = Teacher.objects.filter(username=username)

        if len(matches) == 0:
            return render(
                request, 'piggy/login.html', 
                {'msg': 'Username doesn\'t exist.'}
            )
        else:
            if password == matches[0].password:
                request.session['role'] = role
                request.session['username'] = matches[0].username
                messages.Info('Log in successfully.')
                return render(
                    request, 'piggy/login.html', 
                    {'msg': 'Log in successfully.'}
                )
            else:
                return render(
                    request, 'piggy/login.html', 
                    {'msg': 'Wrong password.'}
                )
    else:
        return render(
            request, 'piggy/login.html', {}
        )

def logout(request):
    try:
        del request.session['username']
        del request.session['role']
    except KeyError:
        return HttpResponse("You haven't logged in yet.")
    return HttpResponse("Logged out successfully.")
