# Generated by Django 4.2.1 on 2023-05-08 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_contact'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.DeleteModel(
            name='Signup',
        ),
    ]
