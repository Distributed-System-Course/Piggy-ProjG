from django.db import models

# Create your models here.

class Teacher(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    resume = models.CharField(max_length=150)

    def __str__(self):
        return "{}".format(self.name, self.username)


class Student(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=150)
    rank = models.IntegerField(default=0)
    email = models.CharField(max_length=150)
    resume = models.CharField(max_length=150)
    
    def __str__(self):
        return "{}".format(self.name, self.username)


class Plan(models.Model):
    """
    A plan may contain several projects, and is owned by a teacher.
    While a plan is not expired, team in this plan can modify their wishes.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    is_expired = models.BooleanField(default=False)
    description = models.CharField(max_length=500)

    def __str__(self):
        return "{} ({})".format(self.name, self.teacher)


class Project(models.Model):
    project_group = models.ForeignKey(Plan, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    max_group_num = models.IntegerField(default=5)
    max_team_member_num = models.IntegerField(default=5)
    
    def __str__(self):
        return "{} in {}".format(self.name, self.project_group)


class Team(models.Model):
    project_group = models.ForeignKey(Plan, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    members = models.ManyToManyField(Student)

    def __str__(self):
        return "{} @ {}".format(self.name, self.project_group)


class TeamWish(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField()
    
    def __str__(self):
        return "{} #{} {}".format(self.team.name, self.priority, self.project)
