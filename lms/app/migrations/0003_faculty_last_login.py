# Generated by Django 5.0.4 on 2024-04-25 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_alter_department_department_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="faculty",
            name="last_login",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
