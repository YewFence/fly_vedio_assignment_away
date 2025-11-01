"""
自动化视频观看框架
提供浏览器管理、认证管理和视频操作功能
"""

from .browser import BrowserManager
from .auth import AuthManager
from .video import VideoManager

__all__ = ['BrowserManager', 'AuthManager', 'VideoManager']
