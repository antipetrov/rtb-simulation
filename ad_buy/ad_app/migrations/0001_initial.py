# Generated by Django 2.1.7 on 2019-03-27 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('tag', models.CharField(max_length=255, verbose_name='Тег')),
            ],
        ),
        migrations.AddField(
            model_name='ad',
            name='categories',
            field=models.ManyToManyField(related_name='ads', to='ad_app.Category'),
        ),
    ]