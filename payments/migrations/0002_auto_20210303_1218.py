# Generated by Django 3.1.6 on 2021-03-03 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='user_sum',
        ),
        migrations.RemoveField(
            model_name='users',
            name='user_wallet_num',
        ),
        migrations.CreateModel(
            name='Wallets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_num', models.CharField(max_length=16)),
                ('wallet_sum', models.IntegerField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.users')),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sum', models.IntegerField()),
                ('destination_wallet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_wallet', to='payments.wallets')),
                ('source_wallet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_wallet', to='payments.wallets')),
            ],
        ),
    ]