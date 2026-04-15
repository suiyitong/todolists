"""主窗口"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, PRIORITY_NAMES, PRIORITY_COLORS
from database import DBManager
from .todo_form import TodoFormDialog
from .category_dialog import CategoryDialog


class MainWindow:
    """应用程序主窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.minsize(700, 450)
        
        # 初始化数据库
        self.db_manager = DBManager()
        
        # 当前筛选状态
        self.current_category_id = None
        self.current_filter = 'all'  # all, completed, pending
        
        self.create_widgets()
        self.refresh_categories()
        self.refresh_todos()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text='+ 新建待办', command=self.add_todo).pack(side='left', padx=5)
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)
        ttk.Button(toolbar, text='管理分类', command=self.manage_categories).pack(side='left', padx=5)
        
        # 主内容区（左右分割）
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 左侧分类面板
        left_frame = ttk.LabelFrame(paned, text='分类', padding=5)
        paned.add(left_frame, weight=1)
        
        self.category_listbox = tk.Listbox(left_frame, selectmode='single', height=20)
        self.category_listbox.pack(fill='both', expand=True)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        ttk.Button(left_frame, text='刷新', command=self.refresh_categories).pack(fill='x', pady=5)
        
        # 右侧任务列表面板
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # 筛选栏
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text='筛选:').pack(side='left', padx=5)
        self.filter_var = tk.StringVar(value='all')
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                    values=['全部', '已完成', '未完成'], 
                                    state='readonly', width=10)
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelect>>', self.on_filter_change)
        
        ttk.Label(filter_frame, text='搜索:').pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side='left', padx=5)
        ttk.Button(filter_frame, text='搜索', command=self.refresh_todos).pack(side='left', padx=5)
        ttk.Button(filter_frame, text='清除', command=self.clear_search).pack(side='left', padx=5)
        
        # 任务列表
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('title', 'category', 'priority', 'due_date', 'completed')
        self.todo_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                     height=15, selectmode='browse')
        
        self.todo_tree.heading('title', text='标题')
        self.todo_tree.heading('category', text='分类')
        self.todo_tree.heading('priority', text='优先级')
        self.todo_tree.heading('due_date', text='截止日期')
        self.todo_tree.heading('completed', text='状态')
        
        self.todo_tree.column('title', width=200)
        self.todo_tree.column('category', width=80)
        self.todo_tree.column('priority', width=60)
        self.todo_tree.column('due_date', width=100)
        self.todo_tree.column('completed', width=60)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient='vertical', command=self.todo_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient='horizontal', command=self.todo_tree.xview)
        self.todo_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.todo_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 绑定事件
        self.todo_tree.bind('<Double-1>', self.edit_todo)
        self.todo_tree.bind('<Button-3>', self.show_context_menu)
        
        # 按钮区域
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text='标记完成/未完成', command=self.toggle_completed).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='编辑', command=self.edit_todo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='删除', command=self.delete_todo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='刷新列表', command=self.refresh_todos).pack(side='right', padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value='就绪')
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(fill='x', side='bottom')
    
    def refresh_categories(self):
        """刷新分类列表"""
        self.category_listbox.delete(0, tk.END)
        self.category_listbox.insert(tk.END, '全部')
        
        categories = self.db_manager.get_all_categories()
        self.category_map = {'全部': None}
        
        for cat in categories:
            self.category_listbox.insert(tk.END, cat.name)
            self.category_map[cat.name] = cat.id
    
    def on_category_select(self, event):
        """分类选择事件"""
        selection = self.category_listbox.curselection()
        if selection:
            category_name = self.category_listbox.get(selection[0])
            self.current_category_id = self.category_map.get(category_name)
            self.refresh_todos()
    
    def on_filter_change(self, event):
        """筛选条件改变"""
        filter_text = self.filter_var.get()
        if filter_text == '全部':
            self.current_filter = 'all'
        elif filter_text == '已完成':
            self.current_filter = 'completed'
        else:
            self.current_filter = 'pending'
        self.refresh_todos()
    
    def clear_search(self):
        """清除搜索"""
        self.search_var.set('')
        self.refresh_todos()
    
    def refresh_todos(self):
        """刷新待办列表"""
        # 清空列表
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        
        # 获取筛选条件
        completed = None
        if self.current_filter == 'completed':
            completed = True
        elif self.current_filter == 'pending':
            completed = False
        
        search_keyword = self.search_var.get().strip() or None
        
        # 加载待办事项
        todos = self.db_manager.get_all_todos(
            category_id=self.current_category_id,
            completed=completed,
            search_keyword=search_keyword
        )
        
        self.todo_items = {}  # item -> id 映射
        
        for todo in todos:
            status = '已完成' if todo.completed else '未完成'
            priority_text = PRIORITY_NAMES.get(todo.priority, '中')
            due_date = todo.due_date.strftime('%Y-%m-%d') if todo.due_date else ''
            category_name = todo.category.name if todo.category else '未分类'
            
            values = (
                todo.title,
                category_name,
                priority_text,
                due_date,
                status
            )
            
            item = self.todo_tree.insert('', 'end', values=values)
            self.todo_items[item] = todo.id
            
            # 根据优先级设置颜色标签
            tag = f'priority_{todo.priority}'
            if not self.todo_tree.tag_has(tag):
                color = PRIORITY_COLORS.get(todo.priority, '#000000')
                self.todo_tree.tag_configure(tag, foreground=color)
            self.todo_tree.item(item, tags=(tag,))
            
            # 已完成项目灰色显示
            if todo.completed:
                self.todo_tree.item(item, tags=(tag, 'completed'))
                if not self.todo_tree.tag_has('completed'):
                    self.todo_tree.tag_configure('completed', foreground='gray')
        
        # 更新状态栏
        stats = self.db_manager.get_todo_stats()
        self.status_var.set(f'共 {stats["total"]} 项 | 已完成 {stats["completed"]} 项 | 待办 {stats["pending"]} 项')
    
    def add_todo(self):
        """添加待办事项"""
        dialog = TodoFormDialog(self.root, self.db_manager, 
                               category_id=self.current_category_id)
        result = dialog.show()
        
        if result:
            self.db_manager.add_todo(**result)
            self.refresh_todos()
    
    def edit_todo(self, event=None):
        """编辑待办事项"""
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个待办事项')
            return
        
        item = selection[0]
        todo_id = self.todo_items.get(item)
        todo = self.db_manager.get_todo_by_id(todo_id)
        
        if todo:
            dialog = TodoFormDialog(self.root, self.db_manager, todo=todo)
            result = dialog.show()
            
            if result:
                self.db_manager.update_todo(todo_id, **result)
                self.refresh_todos()
    
    def delete_todo(self):
        """删除待办事项"""
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个待办事项')
            return
        
        item = selection[0]
        todo_id = self.todo_items.get(item)
        todo_title = self.todo_tree.item(item, 'values')[0]
        
        if messagebox.askyesno('确认', f'确定要删除 "{todo_title}" 吗？'):
            self.db_manager.delete_todo(todo_id)
            self.refresh_todos()
    
    def toggle_completed(self):
        """切换完成状态"""
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个待办事项')
            return
        
        item = selection[0]
        todo_id = self.todo_items.get(item)
        
        self.db_manager.toggle_todo_completed(todo_id)
        self.refresh_todos()
    
    def manage_categories(self):
        """管理分类"""
        dialog = CategoryDialog(self.root, self.db_manager)
        dialog.show()
        self.refresh_categories()
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.todo_tree.identify_row(event.y)
        if item:
            self.todo_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label='编辑', command=self.edit_todo)
            menu.add_command(label='标记完成/未完成', command=self.toggle_completed)
            menu.add_separator()
            menu.add_command(label='删除', command=self.delete_todo)
            menu.post(event.x_root, event.y_root)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()
