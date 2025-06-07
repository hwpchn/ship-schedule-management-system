# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_add_user_avatar'),
    ]

    operations = [
        # 为User表添加性能索引 (MySQL兼容语法)
        migrations.RunSQL(
            """
            CREATE INDEX idx_auth_user_email ON auth_user (email);
            """,
            reverse_sql="DROP INDEX idx_auth_user_email ON auth_user;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_auth_user_is_active ON auth_user (is_active);
            """,
            reverse_sql="DROP INDEX idx_auth_user_is_active ON auth_user;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX idx_auth_user_date_joined ON auth_user (date_joined);
            """,
            reverse_sql="DROP INDEX idx_auth_user_date_joined ON auth_user;"
        ),
        
        # 为Permission表添加性能索引
        migrations.RunSQL(
            """
            CREATE INDEX idx_auth_permission_code ON auth_custom_permission (code);
            """,
            reverse_sql="DROP INDEX idx_auth_permission_code ON auth_custom_permission;"
        ),
        
        # 为Role表添加性能索引
        migrations.RunSQL(
            """
            CREATE INDEX idx_auth_role_name ON auth_role (name);
            """,
            reverse_sql="DROP INDEX idx_auth_role_name ON auth_role;"
        ),
    ]
