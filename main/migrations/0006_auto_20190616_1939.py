# Generated by Django 2.2.2 on 2019-06-16 11:39

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0005_auto_20190615_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postvote',
            name='is_shared',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='postvote',
            name='vote_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='topic',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='topicvote',
            name='is_shared',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='topicvote',
            name='vote_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='postvote',
            name='vote_type',
            field=models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')]),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=80, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
        migrations.AlterField(
            model_name='topicvote',
            name='vote_type',
            field=models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')]),
        ),
    ]
