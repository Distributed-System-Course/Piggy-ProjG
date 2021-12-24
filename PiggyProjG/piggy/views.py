# from django.core.checks import messages
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import ListView
import re

import py_eureka_client.eureka_client as eureka_client

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
        context['role'] = ''
        context['uu'] = ''
    
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
    # return HttpResponseRedirect(request.path_info)


def stop_plan(request, plan_id):
    temp = get_object_or_404(Plan, pk=plan_id)
    temp.is_expired = True
    temp.save()
    
    projects = Project.objects.filter(project_group=temp)
    teams = Team.objects.filter(project_group_id=plan_id)

    data = dict()
    data['projects'] = { proj.id: {'max_group_num': proj.max_group_num} for proj in projects }
    data['wishes'] = []

    for team in teams:
        team_wishes = TeamWish.objects.filter(team=team).order_by('priority')
        data['wishes'].append({
                'team_id': team.id,
                'choices': [ wish.project.id for wish in team_wishes ]
            }
        )
    
    print(data)

    try:
        res = eureka_client.do_service('MyApplication', 'grouping/', data=data, return_type="json")
        print(res)
        for team_id in res.keys():
            the_team = get_object_or_404(Team, pk=team_id)
            the_team.project = get_object_or_404(Project, pk=res[team_id])
            the_team.save()
    except:
        pass
    
    # return HttpResponseRedirect(request.path_info)
    return HttpResponseRedirect('/plan/' + str(plan_id) + '/')


def del_project(request, project_id):
    context = get_user_context(request)
    
    project = get_object_or_404(Project, pk=project_id)
    plan = get_object_or_404(Plan, pk=project.project_group.id)
    if context['role'] == 'Professor' and plan.teacher.id == context['uu'].id:
        project.delete()

    return HttpResponseRedirect('/plan/' + str(plan.id) + '/')
    
    
def del_plan(request, plan_id):
    context = get_user_context(request)

    plan = get_object_or_404(Plan, pk=plan_id)
    if context['role'] == 'Professor' and plan.teacher.id == context['uu'].id:
        plan.delete()
        
    return HttpResponseRedirect('/plans/')

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
    
    the_plan = get_object_or_404(Plan, pk=plan_id)
    context['plan'] = the_plan
    
    context['choices'] = context['plan'].project_set.all()
    
    if 'role' in context and context['role'] == 'Student' and not the_plan.is_expired:
        # User must login first, and only student can create team
        # By creating a team under a plan, one also joins in this plan
        # For each plan, students can only join one team 
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


def join_team(request, team_id):
    context = get_user_context(request)
    the_team = get_object_or_404(Team, pk=team_id)
    the_plan = get_object_or_404(Plan, pk=the_team.project_group.id)
    if 'role' in context and context['role'] == 'Student' and not the_plan.is_expired:
        # User must login first, and only student can join team
        # For each plan, students can only join one team 
        # So we must see whether this student is already in a team or not
        already_exist = False
        teams = Team.objects.filter(project_group__id=the_team.project_group.id)
        for team in teams:
            if context['uu'] in team.members.all():
                already_exist = True
                context['err_msg'] = 'You are already in a team which belongs to this plan.'
                break
        if not already_exist:
            the_team.members.add(context['uu'])
            the_team.save()
    else:
        context['err_msg'] = 'Permission denied.'
    
    return render(
        request,
        'piggy/finish.html',
        context,
    )


def quit_team(request, team_id):
    context = get_user_context(request)
    the_team = get_object_or_404(Team, pk=team_id)
    the_plan = get_object_or_404(Plan, pk=the_team.project_group.id)

    if 'role' in context and context['role'] == 'Student' and not the_plan.is_expired:
        # User must login first, and can only quit from the team they are alreay in
        # So we must see whether this student is already in a team or not
        already_exist = False
        if context['uu'] in the_team.members.all():
            the_team.members.remove(context['uu'])
            the_team.save()
            if len(the_team.members.all()) == 0:
                the_team.delete()
        else:
            context['err_msg'] = 'You don\'t belong to this team.'
    else:
        context['err_msg'] = 'Permission denied.'
    
    return render(
        request,
        'piggy/finish.html',
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
    
    context['plan'] = get_object_or_404(Plan, pk=context['project'].project_group.id)

    if context['role'] == 'Professor' and context['plan'].teacher.id == context['uu'].id:
        context['flag'] = True
            
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
    if context['uu'] != '':
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
    context = get_user_context(request)
    if context['uu'] != '':
        return HttpResponseRedirect('/')
    
    context['draft'] = {}
    context['message'] = []
    
    if request.method == 'POST':
        context['draft']['role'] = request.POST['role']
        context['draft']['name'] = request.POST['name']
        context['draft']['username'] = request.POST['username']

        context['draft']['password1'] = request.POST['password1']
        context['draft']['password2'] = request.POST['password2']
        
        if len(context['draft']['name']) > 150 or len(context['draft']['name']) == 0:
            if len(context['draft']['name']) > 150:
                context['message'].append('Name is too long!')
            else:
                context['message'].append('Name can\'t be empty!')

        if len(context['draft']['username']) > 150 or len(context['draft']['username']) == 0:
            if len(context['draft']['username']) > 150:
                context['message'].append('Username is too long!')
            else:
                context['message'].append('Username can\'t be empty!')
        
        if context['draft']['role'] == 'student':
            matches = Student.objects.filter(username=context['draft']['username'])
        elif context['draft']['role'] == 'professor':
            matches = Teacher.objects.filter(username=context['draft']['username'])

        if len(matches) != 0:
            context['message'].append('Username already exist.')
            
        if context['draft']['password1'] != context['draft']['password2'] or \
                len(context['draft']['password1']) > 128 or \
                len(context['draft']['password1']) == 0:
            context['message'].append('Password Error!')
        
        if len(context['message']) == 0:
            if context['draft']['role'] == 'student':
                new = Student()
            elif context['draft']['role'] == 'professor':
                new = Teacher()
            new.name = context['draft']['name']
            new.username = context['draft']['username']
            new.password = context['draft']['password1']
            new.save()
            
            if context['draft']['role'] == 'student':
                context['uu'] = get_object_or_404(Student, username=context['draft']['username'])
                context['role'] = 'Student'
            elif context['draft']['role'] == 'professor':
                context['uu'] = get_object_or_404(Teacher, username=context['draft']['username'])
                context['role'] = 'Professor'
            context['draft'] = {}
            context['message'].append('Register Successfully!')
            
    return render(
        request,
        'piggy/register.html',
        context,
    )
        
        
def dashboard(request):
    context = get_user_context(request)
    if context['uu'] == '':
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
    if context['uu'] == '':
        return HttpResponseRedirect('/')
    
    if request.method == 'POST':
        role = context['role']
        post_name = request.POST['name']
        post_username = request.POST['username']
        post_password1 = request.POST['password1']
        post_password2 = request.POST['password2']
        post_email = request.POST['email']
        post_resume = request.POST['resume']
        context['message'] = []
        
        if len(post_name) > 150 or len(post_name) == 0:
            if len(post_name) > 150:
                context['message'].append('Name is too long!')
            else:
                context['message'].append('Name can\'t be empty')

        if len(post_username) > 150 or len(post_username) == 0:
            if len(post_username) > 150:
                context['message'].append('Username is too long!')
            else:
                context['message'].append('Username can\'t be empty!')

        if len(context['message']) == 0:
            if role == 'Student':
                matches = Student.objects.filter(username=post_username)
            elif role == 'Professor':
                matches = Teacher.objects.filter(username=post_username)

            if len(matches) != 0 and context['uu'].username != post_username:
                context['message'].append('Username already exist.')

            if len(context['message']) == 0:
                if post_password1 == post_password2 and 0 < len(post_password1) <= 128:
                    context['uu'].name = post_name
                    context['uu'].username = post_username
                    context['uu'].password = post_password1
                    context['uu'].emial = post_email
                    context['uu'].resume = post_resume
                    context['uu'].save()
                    request.session['username'] = post_username
                    context['message'].append('Infomation updated!')

                else:
                    if len(post_password1) == 0:
                        context['message'].append('Password can\'t be empty!')
                    elif len(post_password1) > 128:
                        context['message'].append('Password is too long!')
                    else:
                        context['message'].append('Passwords don\'t match!')

    return render(
        request,
        'piggy/edit_profile.html',
        context,
    )
    
    
def edit_plan(request, plan_id):
    context = get_user_context(request)
    
    context['plan'] = get_object_or_404(Plan, pk=plan_id)
    context['message'] = []
    
    if context['role'] == 'Professor' and context['plan'].teacher.id == context['uu'].id:
        if request.method == 'POST':
            post_name = request.POST['plan_name']
            post_description = request.POST['plan_description']
            post_status = request.POST['plan_status']
            
            if len(post_name) > 150 or len(post_name) == 0:
                if len(post_name) > 150:
                    context['message'].append('Name is too long!')
                else:
                    context['message'].append('Name can\'t be empty')
                    
            if len(post_description) > 150 or len(post_description) == 0:
                if len(post_description) > 150:
                    context['message'].append('Description is too long!')
                else:
                    context['message'].append('Descrption can\'t be empty')
            
            if len(context['message']) == 0:
                context['plan'].name = post_name
                context['plan'].description = post_description
                context['plan'].is_expired = post_status
                context['plan'].save()
                del context['plan']
                context['message'].append('Infomation updated!')
        else:
            context['teams'] = Team.objects.filter(project_group_id=plan_id)
            
        context['plan'] = get_object_or_404(Plan, pk=plan_id)
        
        return render(
            request,
            'piggy/edit_plan.html',
            context
        )
            
    else:
        return HttpResponseRedirect('/plan/' + str(plan_id) + '/')
        
def edit_project(request, project_id):
    context = get_user_context(request)
    
    context['project'] = get_object_or_404(Project, pk=project_id)
    context['plan'] = get_object_or_404(Plan, pk=context['project'].project_group.id)
    context['message'] = []
    
    if context['role'] != 'Professor' or context['plan'].teacher.id != context['uu'].id:
        return HttpResponseRedirect('/project/' + str(project_id) + '/')

    if request.method == 'POST':
        post_name = request.POST['project_name']
        post_description = request.POST['project_description']
        post_max_group_num = request.POST['project_max_group_num']
        post_max_team_member_num = request.POST['project_max_team_member_num']
        
        if len(post_name) > 150 or len(post_name) == 0:
            if len(post_name) > 150:
                context['message'].append('Name is too long!')
            else:
                context['message'].append('Name can\'t be empty')
                
        if len(post_description) > 150 or len(post_description) == 0:
            if len(post_description) > 150:
                context['message'].append('Description is too long!')
            else:
                context['message'].append('Descrption can\'t be empty')
                
        if int(post_max_group_num) <= 0:
            context['message'].append('Max Group Num Error!')
        
        if int(post_max_team_member_num) <= 0:
            context['message'].append('Max Team Member Num Error!')
        
        if len(context['message']) == 0:
            context['project'].name = post_name
            context['project'].description = post_description
            context['project'].max_group_num  = post_max_group_num
            context['project'].max_team_member_num = post_max_team_member_num
            context['project'].save()
            del context['project']
            context['message'].append('Infomation updated!')
    
    context['project'] = get_object_or_404(Project, pk=project_id)
    
    return render(
        request,
        'piggy/edit_project.html',
        context,
    )
        
def add_plan(request):
    context = get_user_context(request)
    if context['uu'] == '' or context['role'] != 'Professor':
        return HttpResponseRedirect('/')
    
    context['draft'] = {}
    context['message'] = []
    
    if request.method == 'POST':
        context['draft']['name'] = request.POST['plan_name']
        context['draft']['description'] = request.POST['plan_description']
        
        if len(context['draft']['name']) > 150 or len(context['draft']['name']) == 0:
            if len(context['draft']['name']) > 150:
                context['message'].append('Name is too long!')
            else:
                context['message'].append('Name can\'t be empty!')
        
        if len(Plan.objects.filter(name=context['draft']['name'], teacher=context['uu'].id)) != 0:
            context['message'].append('Plan have already exist!')
            
        if len(context['draft']['description']) > 500 or len(context['draft']['description']) == 0:
            if len(context['draft']['description']) > 500:
                context['message'].append('Description is too long!')
            else:
                context['message'].append('Description can\'t be empty!')
        
        if len(context['message']) == 0:
            new = Plan()
            new.teacher = context['uu']
            new.name = context['draft']['name']
            new.is_expired = False
            new.description = context['draft']['description']
            new.save()
            context['message'].append('Add Plan Successfully!')
    
    return render(
        request,
        'piggy/add_plan.html',
        context,
    )


def add_project(request, plan_id):
    context = get_user_context(request)
    context['plan'] = get_object_or_404(Plan, pk=plan_id)
    
    if context['role'] != 'Professor' or context['plan'].teacher.id != context['uu'].id:
        return HttpResponseRedirect('/plan/' + str(plan_id) + '/')

    context['draft'] = {}
    context['message'] = []
    
    if request.method == 'POST':
        context['draft']['name'] = request.POST['project_name']
        context['draft']['description'] = request.POST['project_description']
        context['draft']['max_group_num'] = request.POST['project_max_group_num']
        context['draft']['max_team_member_num'] = request.POST['project_max_team_member_num']

        if len(context['draft']['name']) > 150 or len(context['draft']['name']) == 0:
            if len(context['draft']['name']) > 150:
                context['message'].append('Name is too long!')
            else:
                context['message'].append('Name can\'t be empty!')
                
        if len(Project.objects.filter(name=context['draft']['name'], project_group=context['plan'])) != 0:
            context['message'].append('Project have already exist!')
            
        if len(context['draft']['description']) > 500 or len(context['draft']['description']) == 0:
            if len(context['draft']['description']) > 500:
                context['message'].append('Description is too long!')
            else:
                context['message'].append('Description can\'t be empty!')
        
        if len(context['message']) == 0:
            new = Project()
            new.project_group = context['plan']
            new.name = context['draft']['name']
            new.description = context['draft']['description']
            new.max_group_num = context['draft']['max_group_num']
            new.max_team_member_num = context['draft']['max_team_member_num']
            new.save()
            context['message'].append('Add Project Successfully!')
            
    return render(
        request,
        'piggy/add_project.html',
        context,
    )
    

# class SearchProjectsView(ListView):
#     model = Project
#     template_name = 'piggy/search_projects.html'
    
#     def get_queryset(self) -> QuerySet[Project]:
#         query = self.request.GET.get('q')
#         object_list = Project.objects.filter(
#             Q(name__icontains=query) | Q(description__icontains=query)
#         )
#         return object_list


def search_projects(request):
    context = get_user_context(request)
    
    context['draft'] = {}
    context['message'] = []
    context['object_list'] = {}
    
    if request.method == 'GET':
        query = request.GET.get('q', '')
        context['draft']['q'] = query
        if len(query) > 0:
            context['object_list'] = Project.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
    
    return render(
        request,
        'piggy/search_projects.html',
        context,
    )

