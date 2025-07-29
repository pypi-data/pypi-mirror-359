"""
Google Protobuf 内置类型管理模块
处理内置proto类型的识别和导入语句生成
"""

from typing import Dict, Set, Optional

# 智能导入：同时支持相对导入（包环境）和绝对导入（开发环境）
try:
    # 相对导入（包环境）
    from .logger import logger
except ImportError:
    # 绝对导入（开发环境）
    from utils.logger import logger


class BuiltinProtoManager:
    """Google Protobuf 内置proto类型管理器"""
    
    # 内置类型到proto文件的映射
    _BUILTIN_TYPE_TO_FILE = {
        # Wrapper types - 都在 wrappers.proto 中
        'google.protobuf.BoolValue': 'google/protobuf/wrappers.proto',
        'google.protobuf.Int32Value': 'google/protobuf/wrappers.proto',
        'google.protobuf.Int64Value': 'google/protobuf/wrappers.proto',
        'google.protobuf.UInt32Value': 'google/protobuf/wrappers.proto',
        'google.protobuf.UInt64Value': 'google/protobuf/wrappers.proto',
        'google.protobuf.FloatValue': 'google/protobuf/wrappers.proto',
        'google.protobuf.DoubleValue': 'google/protobuf/wrappers.proto',
        'google.protobuf.StringValue': 'google/protobuf/wrappers.proto',
        'google.protobuf.BytesValue': 'google/protobuf/wrappers.proto',
        
        # Well-known types
        'google.protobuf.Any': 'google/protobuf/any.proto',
        'google.protobuf.Timestamp': 'google/protobuf/timestamp.proto',
        'google.protobuf.Duration': 'google/protobuf/duration.proto',
        'google.protobuf.Empty': 'google/protobuf/empty.proto',
        'google.protobuf.Struct': 'google/protobuf/struct.proto',
        'google.protobuf.Value': 'google/protobuf/struct.proto',
        'google.protobuf.ListValue': 'google/protobuf/struct.proto',
        'google.protobuf.NullValue': 'google/protobuf/struct.proto',
        'google.protobuf.FieldMask': 'google/protobuf/field_mask.proto',
        
        # API types
        'google.protobuf.Api': 'google/protobuf/api.proto',
        'google.protobuf.Method': 'google/protobuf/api.proto',
        'google.protobuf.Mixin': 'google/protobuf/api.proto',
        
        # Type definitions
        'google.protobuf.Type': 'google/protobuf/type.proto',
        'google.protobuf.Field': 'google/protobuf/type.proto',
        'google.protobuf.Enum': 'google/protobuf/type.proto',
        'google.protobuf.EnumValue': 'google/protobuf/type.proto',
        'google.protobuf.Option': 'google/protobuf/type.proto',
        'google.protobuf.Syntax': 'google/protobuf/type.proto',
        
        # Source context
        'google.protobuf.SourceContext': 'google/protobuf/source_context.proto',
    }
    
    def __init__(self, output_dir: str = None):
        """
        初始化内置proto管理器
        
        Args:
            output_dir: 输出目录路径（保留兼容性，但不再使用）
        """
        # 保留参数以维持向后兼容性，但不再需要存储
        pass
    
    def is_builtin_type(self, proto_type: str) -> bool:
        """
        检查是否为内置类型
        
        Args:
            proto_type: proto类型名称
            
        Returns:
            是否为内置类型
        """
        return proto_type in self._BUILTIN_TYPE_TO_FILE
    
    def get_import_path(self, proto_type: str) -> Optional[str]:
        """
        获取内置类型的导入路径
        
        Args:
            proto_type: proto类型名称
            
        Returns:
            导入路径，如果不是内置类型则返回None
        """
        return self._BUILTIN_TYPE_TO_FILE.get(proto_type)
    
    def ensure_builtin_proto_file(self, proto_type: str) -> bool:
        """
        确保内置proto文件可用（现在只检查类型是否为内置类型）
        
        Args:
            proto_type: proto类型名称
            
        Returns:
            是否为内置类型
        """
        is_builtin = self.is_builtin_type(proto_type)
        if is_builtin:
            logger.debug(f"识别到内置proto类型: {proto_type}")
        return is_builtin
    
    def process_dependencies(self, dependencies: Set[str]) -> Dict[str, str]:
        """
        处理依赖列表，返回需要的导入语句映射
        
        Args:
            dependencies: 依赖类型集合
            
        Returns:
            类型名到导入路径的映射
        """
        imports = {}
        
        for dep_type in dependencies:
            if self.is_builtin_type(dep_type):
                import_path = self.get_import_path(dep_type)
                if import_path:
                    imports[dep_type] = import_path
                    logger.debug(f"添加内置类型导入: {dep_type} -> {import_path}")
        
        return imports


# 全局实例（在需要时初始化）
_builtin_manager: Optional[BuiltinProtoManager] = None


def get_builtin_manager(include_dir: str = None, output_dir: str = None) -> BuiltinProtoManager:
    """
    获取全局内置proto管理器实例
    
    Args:
        include_dir: include目录路径（保留兼容性，但不再使用）
        output_dir: 输出目录路径（保留兼容性，但不再使用）
        
    Returns:
        BuiltinProtoManager实例
    """
    global _builtin_manager
    
    if _builtin_manager is None:
        _builtin_manager = BuiltinProtoManager(output_dir)
    
    return _builtin_manager


def reset_builtin_manager():
    """重置全局内置proto管理器（主要用于测试）"""
    global _builtin_manager
    _builtin_manager = None 