# Generated manually for local_fees simple model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LocalFee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('polCd', models.CharField(max_length=10, verbose_name='起运港五字码')),
                ('podCd', models.CharField(max_length=10, verbose_name='目的港五字码')),
                ('carriercd', models.CharField(blank=True, max_length=20, null=True, verbose_name='船公司英文名')),
                ('name', models.CharField(max_length=100, verbose_name='费用类型名称')),
                ('unit_name', models.CharField(default='箱型', max_length=50, verbose_name='单位名称')),
                ('price_20gp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='20GP价格')),
                ('price_40gp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='40GP价格')),
                ('price_40hq', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='40HQ价格')),
                ('price_per_bill', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='每票价格')),
                ('currency', models.CharField(blank=True, max_length=20, null=True, verbose_name='货币')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '本地费用',
                'verbose_name_plural': '本地费用',
                'db_table': 'local_fee',
            },
        ),
        migrations.AlterUniqueTogether(
            name='localfee',
            unique_together={('carriercd', 'polCd', 'podCd', 'name')},
        ),
    ]