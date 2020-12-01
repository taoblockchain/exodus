# Generated by Django 3.0.10 on 2020-11-17 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaoReceived',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('txid', models.CharField(max_length=100)),
                ('tot_amt', models.DecimalField(decimal_places=8, max_digits=14)),
                ('tot_fee', models.DecimalField(decimal_places=8, max_digits=14)),
                ('confirmations', models.IntegerField(default=0)),
                ('comment', models.CharField(max_length=100)),
                ('blocktime', models.IntegerField(default=0)),
                ('account', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=14)),
                ('fee', models.DecimalField(decimal_places=8, max_digits=14)),
                ('last_update', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaoSent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amt', models.DecimalField(decimal_places=8, max_digits=14)),
                ('tao_rec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.TaoReceived')),
            ],
        ),
    ]
