"""数据库管理器 - 使用 sqlite3"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from .models import Category, Todo
from config import DB_PATH, DEFAULT_CATEGORIES


class DBManager:
    """数据库管理类"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """初始化数据库，创建表和默认数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建分类表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT DEFAULT '#4A90D9',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建待办事项表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority INTEGER DEFAULT 2,
                    completed BOOLEAN DEFAULT 0,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
                )
            ''')
            
            conn.commit()
            
            # 检查是否需要插入默认分类
            cursor.execute('SELECT COUNT(*) FROM categories')
            if cursor.fetchone()[0] == 0:
                for cat_data in DEFAULT_CATEGORIES:
                    cursor.execute(
                        'INSERT INTO categories (name, color) VALUES (?, ?)',
                        (cat_data['name'], cat_data['color'])
                    )
                conn.commit()
    
    def _row_to_category(self, row) -> Category:
        """将数据库行转换为 Category 对象"""
        return Category(
            id=row['id'],
            name=row['name'],
            color=row['color'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
    
    def _row_to_todo(self, row) -> Todo:
        """将数据库行转换为 Todo 对象"""
        return Todo(
            id=row['id'],
            title=row['title'],
            description=row['description'] or '',
            priority=row['priority'],
            completed=bool(row['completed']),
            due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            category_id=row['category_id'],
            category_name=row['category_name'] if 'category_name' in row.keys() else None,
            category_color=row['category_color'] if 'category_color' in row.keys() else None
        )
    
    # ========== 分类操作 ==========
    
    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM categories ORDER BY name')
            return [self._row_to_category(row) for row in cursor.fetchall()]
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """根据ID获取分类"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            row = cursor.fetchone()
            return self._row_to_category(row) if row else None
    
    def add_category(self, name: str, color: str = '#4A90D9') -> Category:
        """添加新分类"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO categories (name, color) VALUES (?, ?)',
                (name, color)
            )
            conn.commit()
            category_id = cursor.lastrowid
            return self.get_category_by_id(category_id)
    
    def update_category(self, category_id: int, name: str = None, color: str = None) -> bool:
        """更新分类"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if name and color:
                cursor.execute(
                    'UPDATE categories SET name = ?, color = ? WHERE id = ?',
                    (name, color, category_id)
                )
            elif name:
                cursor.execute(
                    'UPDATE categories SET name = ? WHERE id = ?',
                    (name, category_id)
                )
            elif color:
                cursor.execute(
                    'UPDATE categories SET color = ? WHERE id = ?',
                    (color, category_id)
                )
            else:
                return False
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_category(self, category_id: int) -> bool:
        """删除分类"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ========== 待办事项操作 ==========
    
    def get_all_todos(self, category_id: int = None, completed: bool = None, 
                      search_keyword: str = None) -> List[Todo]:
        """获取待办事项列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT t.*, c.name as category_name, c.color as category_color
                FROM todos t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE 1=1
            '''
            params = []
            
            if category_id is not None:
                query += ' AND t.category_id = ?'
                params.append(category_id)
            
            if completed is not None:
                query += ' AND t.completed = ?'
                params.append(1 if completed else 0)
            
            if search_keyword:
                query += ' AND (t.title LIKE ? OR t.description LIKE ?)'
                params.extend([f'%{search_keyword}%', f'%{search_keyword}%'])
            
            query += ' ORDER BY t.completed, t.priority, t.created_at DESC'
            
            cursor.execute(query, params)
            return [self._row_to_todo(row) for row in cursor.fetchall()]
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        """根据ID获取待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT t.*, c.name as category_name, c.color as category_color
                   FROM todos t
                   LEFT JOIN categories c ON t.category_id = c.id
                   WHERE t.id = ?''',
                (todo_id,)
            )
            row = cursor.fetchone()
            return self._row_to_todo(row) if row else None
    
    def add_todo(self, title: str, description: str = '', priority: int = 2,
                 category_id: int = None, due_date: datetime = None) -> Todo:
        """添加新待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            due_date_str = due_date.isoformat() if due_date else None
            
            cursor.execute(
                '''INSERT INTO todos (title, description, priority, category_id, due_date)
                   VALUES (?, ?, ?, ?, ?)''',
                (title, description, priority, category_id, due_date_str)
            )
            conn.commit()
            todo_id = cursor.lastrowid
            return self.get_todo_by_id(todo_id)
    
    def update_todo(self, todo_id: int, title: str = None, description: str = None,
                    priority: int = None, category_id: int = None, 
                    due_date: datetime = None, completed: bool = None) -> bool:
        """更新待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title is not None:
                updates.append('title = ?')
                params.append(title)
            if description is not None:
                updates.append('description = ?')
                params.append(description)
            if priority is not None:
                updates.append('priority = ?')
                params.append(priority)
            if category_id is not None:
                updates.append('category_id = ?')
                params.append(category_id)
            if due_date is not None:
                updates.append('due_date = ?')
                params.append(due_date.isoformat())
            if completed is not None:
                updates.append('completed = ?')
                params.append(1 if completed else 0)
            
            if not updates:
                return False
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(todo_id)
            
            query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def toggle_todo_completed(self, todo_id: int) -> bool:
        """切换待办事项完成状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE todos SET completed = NOT completed, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (todo_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_todo(self, todo_id: int) -> bool:
        """删除待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_todo_stats(self) -> dict:
        """获取待办事项统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM todos')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM todos WHERE completed = 1')
            completed = cursor.fetchone()[0]
            
            return {
                'total': total,
                'completed': completed,
                'pending': total - completed
            }
