"""数据模型"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Category:
    """任务分类模型"""
    id: int
    name: str
    color: str = '#4A90D9'
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class Todo:
    """待办任务模型"""
    id: int
    title: str
    description: str = ''
    priority: int = 2  # 1-高, 2-中, 3-低
    completed: bool = False
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'category_color': self.category_color
        }
