# Generated by Django 5.1.7 on 2025-03-30 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_alter_customuser_options_alter_customuser_nickname_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Message",
        ),
    ]
