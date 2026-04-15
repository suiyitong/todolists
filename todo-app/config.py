"""应用配置"""
import os

# 数据库配置
DB_PATH = os.path.join(os.path.dirname(__file__), 'todo.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# GUI 配置
WINDOW_TITLE = '待办清单'
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

# 优先级配置
PRIORITY_HIGH = 1
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 3

PRIORITY_NAMES = {
    PRIORITY_HIGH: '高',
    PRIORITY_MEDIUM: '中',
    PRIORITY_LOW: '低'
}

PRIORITY_COLORS = {
    PRIORITY_HIGH: '#FF4444',
    PRIORITY_MEDIUM: '#FFAA00',
    PRIORITY_LOW: '#44AA44'
}

# 默认分类
DEFAULT_CATEGORIES = [
    {'name': '工作', 'color': '#4A90D9'},
    {'name': '个人', 'color': '#9B59B6'},
    {'name': '学习', 'color': '#27AE60'},
    {'name': '购物', 'color': '#E67E22'},
]
