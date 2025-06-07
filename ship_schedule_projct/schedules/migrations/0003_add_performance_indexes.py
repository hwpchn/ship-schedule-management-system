# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_vesselinfofromcompany'),
    ]

    operations = [
        # 为VesselSchedule添加性能索引 (MySQL兼容语法)
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_pol_pod ON vessel_schedule (polCd, podCd);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_pol_pod ON vessel_schedule;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_data_version ON vessel_schedule (data_version);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_data_version ON vessel_schedule;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_carrier ON vessel_schedule (carriercd);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_carrier ON vessel_schedule;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_vessel_voyage ON vessel_schedule (vessel, voyage);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_vessel_voyage ON vessel_schedule;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_status ON vessel_schedule (status);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_status ON vessel_schedule;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_schedule_fetch_date ON vessel_schedule (fetch_date);
            """,
            reverse_sql="DROP INDEX idx_vessel_schedule_fetch_date ON vessel_schedule;"
        ),
        
        # 为VesselInfoFromCompany添加性能索引
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_info_pol_pod ON vessel_info_from_company (polCd, podCd);
            """,
            reverse_sql="DROP INDEX idx_vessel_info_pol_pod ON vessel_info_from_company;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_info_carrier ON vessel_info_from_company (carrierCd);
            """,
            reverse_sql="DROP INDEX idx_vessel_info_carrier ON vessel_info_from_company;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_vessel_info_vessel_voyage ON vessel_info_from_company (vessel, voyage);
            """,
            reverse_sql="DROP INDEX idx_vessel_info_vessel_voyage ON vessel_info_from_company;"
        ),
    ]
