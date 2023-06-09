# Generated by Django 4.2.2 on 2023-06-09 15:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_from_user', to=settings.AUTH_USER_MODEL, verbose_name='...')),
                ('like_to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_to_user', to=settings.AUTH_USER_MODEL, verbose_name='...')),
            ],
        ),
    ]
