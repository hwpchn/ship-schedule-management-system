from rest_framework import serializers
from .models import (
    VesselSchedule, 
    VesselInfoFromCompany
)


class VesselScheduleSerializer(serializers.ModelSerializer):
    """船舶航线序列化器"""
    
    class Meta:
        model = VesselSchedule
        fields = '__all__'
        read_only_fields = ['id']
    
    def validate(self, data):
        """数据验证"""
        # 获取现有实例数据（用于更新时的验证）
        if self.instance:
            # 更新时，合并现有数据和新数据
            pol_cd = data.get('polCd', self.instance.polCd)
            pod_cd = data.get('podCd', self.instance.podCd)
            vessel = data.get('vessel', self.instance.vessel)
            voyage = data.get('voyage', self.instance.voyage)
        else:
            # 创建时，直接使用提供的数据
            pol_cd = data.get('polCd')
            pod_cd = data.get('podCd')
            vessel = data.get('vessel')
            voyage = data.get('voyage')
        
        # 验证起运港和目的港不能相同
        if pol_cd and pod_cd and pol_cd == pod_cd:
            raise serializers.ValidationError("起运港和目的港不能相同")
        
        # 验证船名和航次不能为空（仅在创建时或明确提供时检查）
        if not self.instance:  # 创建时
            if not vessel:
                raise serializers.ValidationError("船名不能为空")
            if not voyage:
                raise serializers.ValidationError("航次不能为空")
        else:  # 更新时
            if 'vessel' in data and not vessel:
                raise serializers.ValidationError("船名不能为空")
            if 'voyage' in data and not voyage:
                raise serializers.ValidationError("航次不能为空")
            
        return data


class VesselScheduleListSerializer(serializers.ModelSerializer):
    """船舶航线列表序列化器（简化版）"""
    
    class Meta:
        model = VesselSchedule
        fields = [
            'id', 'vessel', 'voyage', 'polCd', 'podCd', 'pol', 'pod',
            'eta', 'etd', 'status', 'data_version', 'fetch_date'
        ]


class VesselScheduleCreateSerializer(serializers.ModelSerializer):
    """船舶航线创建序列化器"""
    
    class Meta:
        model = VesselSchedule
        fields = '__all__'
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """创建船舶航线记录"""
        # 如果没有提供fetch_timestamp，使用当前时间戳
        if not validated_data.get('fetch_timestamp'):
            import time
            validated_data['fetch_timestamp'] = int(time.time())
        
        # 如果没有提供fetch_date，使用当前时间
        if not validated_data.get('fetch_date'):
            from django.utils import timezone
            validated_data['fetch_date'] = timezone.now()
            
        return super().create(validated_data)


class VesselInfoFromCompanySerializer(serializers.ModelSerializer):
    """船舶额外信息序列化器"""
    
    class Meta:
        model = VesselInfoFromCompany
        fields = '__all__'
        read_only_fields = ['id']
    
    def validate(self, data):
        """数据验证"""
        # 验证价格不能为负数
        if data.get('price') is not None and data['price'] < 0:
            raise serializers.ValidationError("价格不能为负数")
            
        return data


class GroupedScheduleSerializer(serializers.Serializer):
    """分组航线序列化器（用于共舱分组API）"""
    
    # 基础航线信息
    id = serializers.IntegerField()
    vessel = serializers.CharField()
    voyage = serializers.CharField()
    polCd = serializers.CharField()
    podCd = serializers.CharField()
    pol = serializers.CharField()
    pod = serializers.CharField()
    eta = serializers.CharField()
    etd = serializers.CharField()
    routeEtd = serializers.CharField()
    carriercd = serializers.CharField()
    totalDuration = serializers.CharField()
    shareCabins = serializers.JSONField()


class GroupInfoSerializer(serializers.Serializer):
    """分组信息序列化器"""
    
    group_id = serializers.CharField()
    cabins_count = serializers.IntegerField()
    carrier_codes = serializers.ListField(child=serializers.CharField())
    plan_open = serializers.ListField(child=serializers.CharField())
    plan_duration = serializers.CharField()
    schedules = GroupedScheduleSerializer(many=True)


class CabinGroupingResponseSerializer(serializers.Serializer):
    """共舱分组API响应序列化器"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.JSONField())

