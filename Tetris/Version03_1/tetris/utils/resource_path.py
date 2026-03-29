"""工具函数模块"""

from typing import Any
import json
import os
import sys


def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径，支持打包后和开发模式"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe模式：资源在临时目录
        base_path = sys._MEIPASS
    else:
        # 开发模式
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


def get_data_path(filename: str) -> str:
    """获取数据文件路径（如highscore.json），保存在exe所在目录"""
    if getattr(sys, 'frozen', False):
        # 打包后：保存在exe所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发模式：保存在项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, filename)


def load_json_data(filepath: str, key: str = None, default: Any = None) -> Any:
    """加载JSON数据文件"""
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            if key:
                return data.get(key, default)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json_data(filepath: str, data: dict) -> bool:
    """保存JSON数据文件"""
    try:
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception:
        return False