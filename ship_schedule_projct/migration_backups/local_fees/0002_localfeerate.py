# Generated manually to add LocalFeeRate model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('local_fees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalFeeRate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(default='箱型', max_length=50, verbose_name='单位名称')),
                ('price_20gp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='20GP价格')),
                ('price_40gp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='40GP价格')),
                ('price_40hq', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='40HQ价格')),
                ('price_per_bill', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='每票价格')),
                ('port_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='港口代码')),
                ('route_code', models.CharField(blank=True, max_length=50, null=True, verbose_name='航线代码')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否有效')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='local_fees.currency', verbose_name='货币')),
                ('fee_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='local_fees.feetype', verbose_name='费用类型')),
            ],
            options={
                'verbose_name': '本地费用费率',
                'verbose_name_plural': '本地费用费率',
                'db_table': 'local_fee_rate',
            },
        ),
    ]
