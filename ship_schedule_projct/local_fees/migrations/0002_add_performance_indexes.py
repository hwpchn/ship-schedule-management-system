# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_fees', '0001_initial'),
    ]

    operations = [
        # 为LocalFee表添加性能索引 (MySQL兼容语法)
        migrations.RunSQL(
            """
            CREATE INDEX idx_local_fee_pol_pod ON local_fee (polCd, podCd);
            """,
            reverse_sql="DROP INDEX idx_local_fee_pol_pod ON local_fee;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_local_fee_name ON local_fee (name);
            """,
            reverse_sql="DROP INDEX idx_local_fee_name ON local_fee;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_local_fee_currency ON local_fee (currency);
            """,
            reverse_sql="DROP INDEX idx_local_fee_currency ON local_fee;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_local_fee_carriercd ON local_fee (carriercd);
            """,
            reverse_sql="DROP INDEX idx_local_fee_carriercd ON local_fee;"
        ),
    ]
