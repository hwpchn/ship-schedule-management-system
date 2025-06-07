"""
本地费用序列化器
简化版本
"""
from rest_framework import serializers
from .models import LocalFee


class LocalFeeSerializer(serializers.ModelSerializer):
    """
    本地费用序列化器
    """
    class Meta:
        model = LocalFee
        fields = [
            'id', 'polCd', 'podCd', 'carriercd', 'name', 'unit_name',
            'price_20gp', 'price_40gp', 'price_40hq', 'price_per_bill',
            'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LocalFeeQuerySerializer(serializers.ModelSerializer):
    """
    本地费用查询结果序列化器
    按照前端要求的格式输出
    """
    名称 = serializers.CharField(source='name', read_only=True)
    单位 = serializers.CharField(source='unit_name', read_only=True)
    币种 = serializers.CharField(source='currency', read_only=True)
    
    class Meta:
        model = LocalFee
        fields = [
            'id', '名称', '单位', 'price_20gp', 'price_40gp', 
            'price_40hq', 'price_per_bill', '币种'
        ]
    
    def to_representation(self, instance):
        """
        自定义输出格式
        """
        ret = super().to_representation(instance)
        
        # 重新组织字段名称和格式
        formatted_ret = {
            'id': ret['id'],
            '名称': ret['名称'],
            '单位': ret['单位'] or '箱型',
            '20GP': str(ret['price_20gp']) if ret['price_20gp'] else None,
            '40GP': str(ret['price_40gp']) if ret['price_40gp'] else None,
            '40HQ': str(ret['price_40hq']) if ret['price_40hq'] else None,
            '单票价格': str(ret['price_per_bill']) if ret['price_per_bill'] else None,
            '币种': ret['币种']
        }
        
        return formatted_ret
