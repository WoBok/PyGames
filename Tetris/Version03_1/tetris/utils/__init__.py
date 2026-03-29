"""工具函数模块"""

from .resource_path import (
    get_resource_path,
    get_data_path,
    load_json_data,
    save_json_data,
)

__all__ = [
    'get_resource_path',
    'get_data_path',
    'load_json_data',
    'save_json_data',
]