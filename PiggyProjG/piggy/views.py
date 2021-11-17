from django.shortcuts import render
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
            'title' : "Welcome",
            'heading': "Welcome!",
            'message' : "Welcome to Piggy.",
            'content' : "Now is " + timezone.localtime().strftime(("%Y/%m/%d, %H:%M:%S")) + "."
        },
    )


def plans(request):
    pass


def plan_detail(request, plan_id):
    pass


def join_plan(request, plan_id):
    pass


def projects(request):
    all_plans = ProjectGroup.objects.all()
    latest_project_list = Project.objects.all()
    return render(
        request,
        'piggy/projects.html',
        {
            'title': 'All Projects',
            'heading': 'All Projects',
            'all_plans': all_plans,
        }
    )


def project_detail(request, project_id):
    pass

