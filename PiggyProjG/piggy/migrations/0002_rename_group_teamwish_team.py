# Generated by Django 3.2.9 on 2021-11-17 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('piggy', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamwish',
            old_name='group',
            new_name='team',
        ),
    ]