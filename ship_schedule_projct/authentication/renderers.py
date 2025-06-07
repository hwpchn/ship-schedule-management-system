"""
自定义JSON渲染器
确保中文字符正确显示，不被转义为Unicode编码
"""
import json
from rest_framework.renderers import JSONRenderer


class UnicodeJSONRenderer(JSONRenderer):
    """
    自定义JSON渲染器
    确保中文等Unicode字符正确显示
    """
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        渲染JSON数据，确保中文字符不被转义
        
        Args:
            data: 要渲染的数据
            accepted_media_type: 接受的媒体类型
            renderer_context: 渲染器上下文
            
        Returns:
            bytes: 渲染后的JSON字节串
        """
        if data is None:
            return b''
        
        # 获取缩进设置
        indent = None
        if renderer_context and self.get_indent(renderer_context):
            indent = self.get_indent(renderer_context)
        
        ret = json.dumps(
            data,
            cls=self.encoder_class,
            indent=indent,
            ensure_ascii=False,  # 关键设置：不转义非ASCII字符
            separators=(',', ':') if not indent else (',', ': ')
        )
        
        return ret.encode(self.charset)
    
    def get_indent(self, renderer_context):
        """
        获取JSON缩进设置
        
        Args:
            renderer_context: 渲染器上下文
            
        Returns:
            int|None: 缩进空格数或None
        """
        if renderer_context is None:
            return None
        
        view = renderer_context.get('view')
        request = renderer_context.get('request')
        
        # 在调试模式下或指定indent参数时使用缩进
        if (request and request.query_params.get('indent')) or \
           (hasattr(view, 'json_indent') and view.json_indent):
            return 2
        
        return None 