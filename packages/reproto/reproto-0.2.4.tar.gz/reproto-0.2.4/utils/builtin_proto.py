"""
Google Protobuf 内置类型管理模块
处理内置proto文件的检测、拷贝和导入语句生成
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Set, Optional

# 智能导入：同时支持相对导入（包环境）和绝对导入（开发环境）
try:
    # 相对导入（包环境）
    from .logger import logger
except ImportError:
    # 绝对导入（开发环境）
    from utils.logger import logger


def find_include_directory() -> Optional[Path]:
    """
    查找include目录，支持开发环境和安装包环境
    
    Returns:
        include目录的路径，如果找不到则返回None
    """
    # 尝试多个可能的位置
    possible_locations = [
        # 1. 相对于当前文件的位置（开发环境）
        Path(__file__).parent.parent / "include",
        
        # 2. 相对于包安装位置（安装包环境）
        Path(__file__).parent.parent.parent / "include",
        
        # 3. 在site-packages中的位置
        Path(__file__).parent / "include",
        
        # 4. 使用pkg_resources查找（如果可用）
    ]
    
    # 尝试使用pkg_resources（推荐方式）
    try:
        import pkg_resources
        try:
            include_path = Path(pkg_resources.resource_filename('reproto', 'include'))
            if include_path.exists():
                possible_locations.insert(0, include_path)
        except (pkg_resources.DistributionNotFound, FileNotFoundError):
            pass
    except ImportError:
        pass
    
    # 尝试使用importlib.resources（Python 3.9+推荐方式）
    try:
        import importlib.resources as resources
        try:
            # 对于Python 3.9+
            if hasattr(resources, 'files'):
                include_ref = resources.files('reproto') / 'include'
                if include_ref.is_dir():
                    possible_locations.insert(0, Path(str(include_ref)))
        except Exception:
            pass
    except ImportError:
        pass
    
    # 按优先级检查每个位置
    for location in possible_locations:
        if location.exists() and location.is_dir():
            # 验证这确实是包含proto文件的include目录
            wrappers_file = location / "google" / "protobuf" / "wrappers.proto"
            if wrappers_file.exists():
                logger.debug(f"找到include目录: {location}")
                return location
    
    logger.error("无法找到include目录")
    return None


class BuiltinProtoManager:
    """Google Protobuf 内置proto文件管理器"""
    
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
    
    # 需要拷贝的所有内置proto文件列表
    _ALL_BUILTIN_PROTO_FILES = [
        'google/protobuf/any.proto',
        'google/protobuf/api.proto',
        'google/protobuf/compiler/plugin.proto',
        'google/protobuf/cpp_features.proto',
        'google/protobuf/descriptor.proto',
        'google/protobuf/duration.proto',
        'google/protobuf/empty.proto',
        'google/protobuf/field_mask.proto',
        'google/protobuf/go_features.proto',
        'google/protobuf/java_features.proto',
        'google/protobuf/source_context.proto',
        'google/protobuf/struct.proto',
        'google/protobuf/timestamp.proto',
        'google/protobuf/type.proto',
        'google/protobuf/wrappers.proto',
    ]
    
    def __init__(self, include_dir: str, output_dir: str):
        """
        初始化内置proto管理器
        
        Args:
            include_dir: include目录路径
            output_dir: 输出目录路径
        """
        self.include_dir = Path(include_dir)
        self.output_dir = Path(output_dir)
        self._copied_files: Set[str] = set()
        self._all_builtins_copied: bool = False  # 标记是否已拷贝所有内置文件
    
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
    
    def copy_all_builtin_proto_files(self) -> bool:
        """
        一次性拷贝所有内置proto文件
        
        Returns:
            是否成功拷贝所有文件
        """
        if self._all_builtins_copied:
            logger.debug("所有内置proto文件已拷贝，跳过")
            return True
            
        logger.info("🚀 开始拷贝所有Google Protobuf内置文件...")
        
        success_count = 0
        total_count = len(self._ALL_BUILTIN_PROTO_FILES)
        
        for proto_file in self._ALL_BUILTIN_PROTO_FILES:
            # 源文件路径
            source_file = self.include_dir / proto_file
            if not source_file.exists():
                logger.error(f"❌ 内置proto文件不存在: {source_file} - 这将导致Google protobuf内置类型无法使用！")
                continue
            
            # 目标文件路径
            target_file = self.output_dir / proto_file
            
            # 创建目标目录
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # 拷贝文件
                shutil.copy2(source_file, target_file)
                self._copied_files.add(proto_file)
                success_count += 1
                logger.debug(f"📄 拷贝内置文件: {proto_file}")
            except Exception as e:
                logger.error(f"拷贝内置proto文件失败: {source_file} -> {target_file}, 错误: {e}")
        
        self._all_builtins_copied = True
        logger.info(f"✅ 成功拷贝 {success_count}/{total_count} 个Google Protobuf内置文件")
        
        return success_count == total_count
    
    def ensure_builtin_proto_file(self, proto_type: str) -> bool:
        """
        确保内置proto文件存在于输出目录中
        新逻辑：第一次遇到内置依赖时，拷贝所有内置proto文件，后续直接返回成功
        
        Args:
            proto_type: proto类型名称
            
        Returns:
            是否成功处理
        """
        if not self.is_builtin_type(proto_type):
            return False
        
        # 如果还没拷贝过所有内置文件，现在就拷贝
        if not self._all_builtins_copied:
            logger.info(f"检测到内置依赖 {proto_type}，触发拷贝所有Google Protobuf内置文件")
            return self.copy_all_builtin_proto_files()
        
        # 如果已经拷贝过了，直接返回成功（避免重复拷贝）
        import_path = self.get_import_path(proto_type)
        if import_path and import_path in self._copied_files:
            return True
        
        # 兜底：如果某种原因文件没有在全量拷贝中处理，使用原有的单个拷贝逻辑
        return self._copy_single_builtin_file(proto_type)
    
    def _copy_single_builtin_file(self, proto_type: str) -> bool:
        """
        拷贝单个内置proto文件（原有逻辑，作为兜底）
        
        Args:
            proto_type: proto类型名称
            
        Returns:
            是否成功拷贝
        """
        import_path = self.get_import_path(proto_type)
        if not import_path:
            return False
        
        # 如果已经拷贝过，直接返回
        if import_path in self._copied_files:
            return True
        
        # 源文件路径
        source_file = self.include_dir / import_path
        if not source_file.exists():
            logger.error(f"内置proto文件不存在: {source_file}")
            return False
        
        # 目标文件路径
        target_file = self.output_dir / import_path
        
        # 创建目标目录
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 拷贝文件
            shutil.copy2(source_file, target_file)
            self._copied_files.add(import_path)
            logger.info(f"📄 拷贝内置proto文件: {import_path}")
            return True
        except Exception as e:
            logger.error(f"拷贝内置proto文件失败: {source_file} -> {target_file}, 错误: {e}")
            return False
    
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
                if import_path and self.ensure_builtin_proto_file(dep_type):
                    imports[dep_type] = import_path
        
        return imports
    
    def get_copied_files(self) -> Set[str]:
        """
        获取已拷贝的文件列表
        
        Returns:
            已拷贝文件路径的集合
        """
        return self._copied_files.copy()


# 全局实例（在需要时初始化）
_builtin_manager: Optional[BuiltinProtoManager] = None


def get_builtin_manager(include_dir: str = None, output_dir: str = None) -> BuiltinProtoManager:
    """
    获取全局内置proto管理器实例
    
    Args:
        include_dir: include目录路径（可选，如果不提供会自动查找）
        output_dir: 输出目录路径（首次调用时必需）
        
    Returns:
        BuiltinProtoManager实例
    """
    global _builtin_manager
    
    if _builtin_manager is None:
        if output_dir is None:
            raise ValueError("首次调用get_builtin_manager时必须提供output_dir")
        
        # 如果没有提供include_dir，自动查找
        if include_dir is None:
            include_path = find_include_directory()
            if include_path is None:
                raise ValueError("无法找到include目录，请手动指定include_dir参数")
            include_dir = str(include_path)
        
        _builtin_manager = BuiltinProtoManager(include_dir, output_dir)
    
    return _builtin_manager


def reset_builtin_manager():
    """重置全局内置proto管理器（主要用于测试）"""
    global _builtin_manager
    _builtin_manager = None 