# Generated by Django 5.0.4 on 2024-04-24 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="department",
            name="department_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
