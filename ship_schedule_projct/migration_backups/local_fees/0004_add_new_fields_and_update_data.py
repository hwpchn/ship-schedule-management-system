# Generated manually for refactoring LocalFeeRate model
from django.db import migrations, models

def update_existing_records(apps, schema_editor):
    """为现有记录分配唯一的vessel、polCd、podCd值"""
    LocalFeeRate = apps.get_model('local_fees', 'LocalFeeRate')
    
    # 预定义的船名、起运港、目的港组合
    routes = [
        ("EVER GIVEN", "CNSHK", "THBKK"),
        ("MSC GULSUN", "CNSHK", "SGSIN"),
        ("COSCO UNIVERSE", "CNNGB", "THBKK"),
        ("ONE INNOVATION", "CNQZH", "THBKK"),
        ("HAPAG EXPRESS", "CNSHK", "PLGDY"),
        ("MAERSK VIKING", "CNSHK", "NLRTM"),
        ("CMA CGM MARCO", "CNSHK", "USNYC"),
        ("OOCL TOKYO", "CNNGB", "JPTYO"),
        ("EVERGREEN STAR", "CNSHK", "THBKK"),
    ]
    
    records = LocalFeeRate.objects.all()
    for i, record in enumerate(records):
        route_index = i % len(routes)
        vessel, polCd, podCd = routes[route_index]
        
        # 如果同一航线有多条记录，在船名后加序号
        same_route_count = i // len(routes)
        if same_route_count > 0:
            vessel = f"{vessel}_{same_route_count + 1}"
        
        record.vessel = vessel
        record.polCd = polCd
        record.podCd = podCd
        record.save()
        
        print(f"Updated record {record.id}: {vessel} [{polCd}-{podCd}] {record.fee_type.name}")

def reverse_update(apps, schema_editor):
    """回滚操作，恢复默认值"""
    LocalFeeRate = apps.get_model('local_fees', 'LocalFeeRate')
    
    LocalFeeRate.objects.all().update(
        vessel="DEFAULT_VESSEL",
        polCd="CNSHK", 
        podCd="THBKK"
    )

class Migration(migrations.Migration):

    dependencies = [
        ('local_fees', '0003_merge_0002_add_localfeerate_0002_localfeerate'),
    ]

    operations = [
        # Fields already exist, just run data migration to update existing records
        migrations.RunPython(update_existing_records, reverse_update),
    ]
