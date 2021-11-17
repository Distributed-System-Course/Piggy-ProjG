from django.db import models

# Create your models here.

class Teacher(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)

    def __str__(self):
        return "{}({})".format(self.name, self.username)


class Student(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)
    rank = models.IntegerField(default=0)
    
    def __str__(self):
        return "{}({})".format(self.name, self.username)


class ProjectGroup(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return "{}({})".format(self.name, self.teacher)


class Project(models.Model):
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    max_group_num = models.IntegerField(default=5)
    max_team_member_num = models.IntegerField(default=5)
    
    def __str__(self):
        return "{}({})".format(self.name, self.project_group)


class Team(models.Model):
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    members = models.ManyToManyField(Student)

    def __str__(self):
        return "{}: {} ({})".format(self.name, self.project, self.project_group)


class TeamWish(models.Model):
    group = models.ForeignKey(Team, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField()
    
    def __str__(self):
        return "{} #{} {} ({})".format(self.group, self.priority, self.project)