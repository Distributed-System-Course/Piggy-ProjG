# Generated by Django 3.2.8 on 2021-12-04 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('piggy', '0003_auto_20211119_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='description',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]