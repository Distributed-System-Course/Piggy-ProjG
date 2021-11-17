from django.db import models

# Create your models here.

class Teacher(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)


class Student(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)


class ProjectGroup(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)


class Project(models.Model):
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    detail = models.CharField(max_length=500)
    max_group = models.IntegerField(default=5)
