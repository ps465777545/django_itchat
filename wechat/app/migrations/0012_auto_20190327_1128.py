# Generated by Django 2.1.5 on 2019-03-27 11:28

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0011_auto_20190325_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouping',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联用户'),
        ),
        migrations.AddField(
            model_name='groups_name',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联用户'),
        ),
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联用户'),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 27, 11, 28, 11, 833343), verbose_name='任务添加时间'),
        ),
        migrations.AlterField(
            model_name='wechat_friend',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 27, 11, 28, 11, 835889), verbose_name='添加时间'),
        ),
        migrations.AlterModelTable(
            name='wechat_friend',
            table='wechat_friend',
        ),
    ]
