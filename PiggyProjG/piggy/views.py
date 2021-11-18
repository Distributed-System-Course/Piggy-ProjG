from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages


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
    all_plans = ProjectGroup.objects.all()
    return render(
        request, 
        'piggy/plans.html', 
        {
            'all_plans': all_plans,
        }
    )


def plan_detail(request, plan_id):
    plan = get_object_or_404(ProjectGroup, pk=plan_id)
    return render(
        request,
        'piggy/plan_detail.html',
        {
            'plan': plan
        }
    )

@login_required
def join_plan(request, plan_id):
        return render(
        request,
        'piggy/join_plan.html',
        {
            
        }
    )


def projects(request):
    all_plans = ProjectGroup.objects.all()
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

def register(request):
    print('jb1')
    if request.method == "POST":
        print("jb")
        form = NewUserForm(request.POST)
        # print(form)
        if form.is_valid():
            print('jbdx')
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("piggy:index")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        pass
    form = NewUserForm()
    print('jb2')
    return render(
        request,
        'piggy/register.html',
        {
            "register_form": form,
        }
    )