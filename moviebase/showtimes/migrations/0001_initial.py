# Generated by Django 2.2.5 on 2019-09-06 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('movielist', '0002_auto_20190904_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cinema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Screening',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('cinema', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='showtimes.Cinema')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='movielist.Movie')),
            ],
        ),
        migrations.AddField(
            model_name='cinema',
            name='movies',
            field=models.ManyToManyField(through='showtimes.Screening', to='movielist.Movie'),
        ),
    ]
