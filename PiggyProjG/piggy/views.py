# from django.core.checks import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

from .models import *

def get_user_context(request):
    context = dict()

    try:
        loggedin_user_username = request.session['username']
        role = request.session['role']
        if role == 'student':
            context['uu'] = get_object_or_404(Student, username=loggedin_user_username)
            context['role'] = 'Student'

        elif role == 'professor':
            context['uu'] = get_object_or_404(Teacher, username=loggedin_user_username)
            context['role'] = 'Professor'
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
    temp = get_object_or_404(Plan, pk=plan_id)
    temp.is_expired = False
    temp.save()
    
    return HttpResponseRedirect('/plan/' + str(plan_id) + '/')


def stop_plan(request, plan_id):
    temp = get_object_or_404(Plan, pk=plan_id)
    temp.is_expired = True
    temp.save()
    
    return HttpResponseRedirect('/plan/' + str(plan_id) + '/')


def del_project(request, plan_id, project_id):
    context = get_user_context(request)
    return render(
        request,
        'piggy/edit_plan.html',
        context
    )
    

def kick_out_team(request, plan_id, team_id):
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
    
    context['plan'] = get_object_or_404(Plan, pk=plan_id)
    context['teams'] = Team.objects.filter(project_group_id=plan_id)
    if context['role'] == 'Professor' and context['plan'].teacher.id == context['uu'].id:
        context['flag'] = True

    return render(
        request,
        'piggy/plan_detail.html',
        context
    )


def create_team(request, plan_id):
    context = get_user_context(request)
    
    context['plan'] = get_object_or_404(Plan, pk=plan_id)
    
    context['choices'] = context['plan'].project_set.all()
    
    if 'role' in context and context['role'] == 'Student':
        # User must login first, and only student can create team
        # By creating a team under a plan, one also joins in this plan
        # For each plan, students can only jpin one team 
        # So we must see whether this student is already in a team or not
        already_exist = False
        teams = Team.objects.filter(project_group__id=plan_id)
        for team in teams:
            if context['uu'] in team.members.all():
                already_exist = True
                context['err_msg'] = 'You are already in a team which belongs to this plan.'
                break
        
        # Only when requirements(login & not existed in any team) are satisfied, do post request
        if request.method == "POST" and not already_exist:
            new_team = Team()
            new_team.name = request.POST['team_name']
            project_id = int(request.POST['default_project_id'])
            new_team.project_group = context['plan']
            new_team.project = Project.objects.get(id=project_id)
            new_team.save()
            context['msg'] = 'Team created successfully.'
            new_team.members.add(context['uu'])

    else:
        context['err_msg'] = 'You don\'t have enough permissions.'

    return render(
        request,
        'piggy/create_team.html',
        context,
    )


def projects(request):
    context = get_user_context(request)
    
    context['all_plans'] = Plan.objects.all()
    return render(
        request,
        'piggy/projects.html',
        context,
    )


def project_detail(request, project_id):
    context = get_user_context(request)
    
    project = get_object_or_404(Project, pk=project_id)
    context['project'] = project
    context['max_group_num'] = project.max_group_num
    context['max_team_member_num'] = project.max_team_member_num
    
    return render(
        request, 
        'piggy/project_detail.html', 
        context
    )


def teachers(request):
    context = get_user_context(request)
    
    context['teachers'] = Teacher.objects.all()
    
    return render(
        request,
        'piggy/teachers.html',
        context,
    )


def teacher_detail(request, teacher_id):
    context = get_user_context(request)
    context['teacher'] = get_object_or_404(Teacher, pk=teacher_id)
    context['all_plans'] = Plan.objects.filter(teacher_id=teacher_id)
    
    return render(
        request,
        'piggy/teacher_detail.html',
        context
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
    context = get_user_context(request)
    if context != {}:
        return HttpResponseRedirect('/')
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
                return HttpResponseRedirect('/')
            else:
                return render(
                    request, 'piggy/login.html', 
                    {'msg': 'Wrong password.'}
                )
    else:
        return render(
            request, 'piggy/login.html',
        )


def logout(request):
    try:
        del request.session['username']
        del request.session['role']
    except KeyError:
        context = {"info": "You haven't logged in yet."}
        return render(
            request,
            'piggy/logout.html',
            context
        )
    return HttpResponseRedirect('/')


def register(request):
    if request.method == 'POST':
        role = request.POST['role']
        name = request.POST['name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if len(name) > 150 or len(name) == 0:
            return render(
                request,
                'piggy/register.html',
                {'msg': "Name illegal!"}
            )

        if len(username) > 150 or len(username) == 0:
            return render(
                request,
                'piggy/register.html', 
                {'msg': 'Username illegal!'}
            )
        
        if role == 'student':
            matches = Student.objects.filter(username=username)
        elif role == 'professor':
            matches = Teacher.objects.filter(username=username)

        if len(matches) != 0:
            return render(
                request, 
                'piggy/register.html', 
                {'msg': 'Username already exist.'}
            )
        else:
            if password1 == password2 and 0 < len(password1) <= 128:
                if role == 'student':
                    new = Student()
                elif role == 'professor':
                    new = Teacher()
                new.name = name
                new.username = username
                new.password = password1
                new.save()
                context = {}
                
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
                
                return render(
                    request,
                    'piggy/index.html',
                    context
                )
            else:
                return render(
                    request,
                    'piggy/register.html',
                    {'msg': 'Password Error!'}
                )
    else:
        return render(
            request,
            'piggy/register.html'
        )
        
        
def dashboard(request):
    context = get_user_context(request)
    if context == {}:
        return HttpResponseRedirect('/')
    
    if context['role'] == 'Professor':
        context['all_plans'] = Plan.objects.filter(teacher_id=context['uu'].id)
    
    return render(
        request,
        'piggy/dashboard.html',
        context,
    )
    
    
def edit_profile(request):
    context = get_user_context(request)
    if context == {}:
        return HttpResponseRedirect('/')
    
    if request.method == 'POST':
        role = context['role']
        post_name = request.POST['name']
        post_username = request.POST['username']
        post_password1 = request.POST['password1']
        post_password2 = request.POST['password2']
        post_email = request.POST['email']
        post_resume = request.POST['resume']
        
        if len(post_name) > 150 or len(post_name) == 0:
            if len(post_name) > 150:
                context['msg'] = 'Name is too long!'
            else:
                context['msg'] = 'Name can\'t be empty'

        elif len(post_username) > 150 or len(post_username) == 0:
            if len(post_username) > 150:
                context['msg'] = 'Username is too long!'
            else:
                context['msg'] = 'Username can\'t be empty!'

        else:
            if role == 'Student':
                matches = Student.objects.filter(username=post_username)
            elif role == 'Professor':
                matches = Teacher.objects.filter(username=post_username)

            if len(matches) != 0 and context['uu'].username != post_username:
                context['msg'] = 'Username already exist.'

            else:
                if post_password1 == post_password2 and 0 < len(post_password1) <= 128:
                    context['uu'].name = post_name
                    context['uu'].username = post_username
                    context['uu'].password = post_password1
                    context['uu'].emial = post_email
                    context['uu'].resume = post_resume
                    context['uu'].save()
                    request.session['username'] = post_username
                    context['msg'] = 'Infomation updated!'

                else:
                    if len(post_password1) == 0:
                        context['msg'] = 'Password can\'t be empty!'
                    elif len(post_password1) > 128:
                        context['msg'] = 'Password is too long!'
                    else:
                        context['msg'] = 'Passwords don\'t match!'

    return render(
        request,
        'piggy/edit_profile.html',
        context,
    )
    
    
def edit_plan(request, plan_id):
    context = get_user_context(request)
    
    context['plan'] = get_object_or_404(Plan, pk=plan_id)
    
    if context['role'] == 'Professor' and context['plan'].teacher.id == context['uu'].id:
        
        context['teams'] = Team.objects.filter(project_group_id=plan_id)
        
        return render(
            request,
            'piggy/edit_plan.html',
            context
        )
    else:
        return HttpResponseRedirect('/')
        