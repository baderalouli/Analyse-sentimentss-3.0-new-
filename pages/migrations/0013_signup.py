# Generated by Django 4.2.1 on 2023-05-10 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_delete_signup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('Email', models.EmailField(max_length=255)),
                ('password', models.CharField(max_length=50)),
                ('comfir_password', models.CharField(max_length=50)),
            ],
        ),
    ]
