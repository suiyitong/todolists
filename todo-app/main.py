#!/usr/bin/env python3
"""
待办清单桌面应用
使用 Python + tkinter + SQLite 实现
"""
import sys
import os

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import MainWindow


def main():
    """程序入口"""
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
