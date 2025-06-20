# Generated by Django 4.2.7 on 2025-05-23 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VesselSchedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('polCd', models.CharField(max_length=10, verbose_name='起运港五字码')),
                ('podCd', models.CharField(max_length=10, verbose_name='目的港五字码')),
                ('vessel', models.CharField(max_length=100, verbose_name='船名')),
                ('voyage', models.CharField(max_length=50, verbose_name='航次')),
                ('data_version', models.IntegerField(verbose_name='数据版本号')),
                ('fetch_timestamp', models.BigIntegerField(verbose_name='数据抓取的Unix时间戳')),
                ('fetch_date', models.DateTimeField(verbose_name='格式化的日期时间')),
                ('status', models.SmallIntegerField(default=1, verbose_name='数据状态：1-有效，0-无效')),
                ('routeCd', models.CharField(blank=True, max_length=50, null=True, verbose_name='航线服务名称')),
                ('routeEtd', models.CharField(blank=True, max_length=20, null=True, verbose_name='计划离港班期')),
                ('carriercd', models.CharField(blank=True, max_length=20, null=True, verbose_name='船公司英文名')),
                ('isReferenceCarrier', models.CharField(blank=True, max_length=5, null=True, verbose_name='是否主船东')),
                ('imo', models.CharField(blank=True, max_length=20, null=True, verbose_name='国际海事组织号码')),
                ('shipAgency', models.CharField(blank=True, max_length=100, null=True, verbose_name='船代')),
                ('pol', models.CharField(blank=True, max_length=100, null=True, verbose_name='起运港英文名')),
                ('polTerminal', models.CharField(blank=True, max_length=100, null=True, verbose_name='起运港码头')),
                ('polTerminalCd', models.CharField(blank=True, max_length=20, null=True, verbose_name='起运港码头代码')),
                ('pod', models.CharField(blank=True, max_length=100, null=True, verbose_name='目的港英文名')),
                ('podTerminal', models.CharField(blank=True, max_length=100, null=True, verbose_name='目的港码头')),
                ('podTerminalCd', models.CharField(blank=True, max_length=20, null=True, verbose_name='目的港码头代码')),
                ('eta', models.CharField(blank=True, max_length=30, null=True, verbose_name='计划到港日期')),
                ('etd', models.CharField(blank=True, max_length=30, null=True, verbose_name='计划离港日期')),
                ('totalDuration', models.CharField(blank=True, max_length=10, null=True, verbose_name='预计航程')),
                ('bookingCutoff', models.CharField(blank=True, max_length=30, null=True, verbose_name='截订舱时间')),
                ('cyOpen', models.CharField(blank=True, max_length=30, null=True, verbose_name='进港时间')),
                ('cyClose', models.CharField(blank=True, max_length=30, null=True, verbose_name='截港时间')),
                ('customCutoff', models.CharField(blank=True, max_length=30, null=True, verbose_name='截放行')),
                ('cutOff', models.CharField(blank=True, max_length=30, null=True, verbose_name='截申报')),
                ('siCutoff', models.CharField(blank=True, max_length=30, null=True, verbose_name='截单时间')),
                ('vgmCutoff', models.CharField(blank=True, max_length=30, null=True, verbose_name='截VGM时间')),
                ('isTransit', models.CharField(blank=True, max_length=5, null=True, verbose_name='是否中转')),
                ('transitPortEn', models.CharField(blank=True, max_length=100, null=True, verbose_name='中转1港口名')),
                ('transitPortCd', models.CharField(blank=True, max_length=10, null=True, verbose_name='中转1港口代码')),
                ('vesselAfterTransit', models.CharField(blank=True, max_length=100, null=True, verbose_name='中转1船名')),
                ('voyageAfterTransit', models.CharField(blank=True, max_length=50, null=True, verbose_name='中转1航次')),
                ('secondTransitPortEn', models.CharField(blank=True, max_length=100, null=True, verbose_name='中转2港口名')),
                ('secondTransitPortCd', models.CharField(blank=True, max_length=10, null=True, verbose_name='中转2港口代码')),
                ('secondVesselAfterTransit', models.CharField(blank=True, max_length=100, null=True, verbose_name='中转2船名')),
                ('secondVoyageAfterTransit', models.CharField(blank=True, max_length=50, null=True, verbose_name='中转2航次')),
                ('shareCabins', models.TextField(blank=True, null=True, verbose_name='共舱结果集')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注信息')),
                ('ext_field1', models.CharField(blank=True, max_length=255, null=True, verbose_name='扩展字段1')),
                ('ext_field2', models.CharField(blank=True, max_length=255, null=True, verbose_name='扩展字段2')),
                ('ext_field3', models.TextField(blank=True, null=True, verbose_name='扩展字段3')),
            ],
            options={
                'verbose_name': '船舶航线',
                'verbose_name_plural': '船舶航线',
                'db_table': 'vessel_schedule',
                'unique_together': {('polCd', 'podCd', 'vessel', 'voyage', 'data_version')},
            },
        ),
    ]
