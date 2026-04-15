"""待办事项表单对话框"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import PRIORITY_NAMES, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW


class TodoFormDialog:
    """待办事项添加/编辑对话框"""
    
    def __init__(self, parent, db_manager, todo=None, category_id=None):
        """
        初始化对话框
        :param parent: 父窗口
        :param db_manager: 数据库管理器
        :param todo: 待编辑的待办事项（None表示新建）
        :param category_id: 默认选中的分类ID
        """
        self.parent = parent
        self.db_manager = db_manager
        self.todo = todo
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('编辑待办' if todo else '添加待办')
        self.dialog.geometry('450x400')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_data(category_id)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        padding = {'padx': 10, 'pady': 5}
        
        # 标题
        ttk.Label(self.dialog, text='标题:').grid(row=0, column=0, sticky='w', **padding)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(self.dialog, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=0, column=1, sticky='ew', **padding)
        
        # 分类
        ttk.Label(self.dialog, text='分类:').grid(row=1, column=0, sticky='w', **padding)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.dialog, textvariable=self.category_var, 
                                           state='readonly', width=37)
        self.category_combo.grid(row=1, column=1, sticky='ew', **padding)
        
        # 优先级
        ttk.Label(self.dialog, text='优先级:').grid(row=2, column=0, sticky='w', **padding)
        self.priority_var = tk.IntVar(value=PRIORITY_MEDIUM)
        priority_frame = ttk.Frame(self.dialog)
        priority_frame.grid(row=2, column=1, sticky='w', **padding)
        
        ttk.Radiobutton(priority_frame, text='高', variable=self.priority_var, 
                       value=PRIORITY_HIGH).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text='中', variable=self.priority_var,
                       value=PRIORITY_MEDIUM).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text='低', variable=self.priority_var,
                       value=PRIORITY_LOW).pack(side='left', padx=5)
        
        # 截止日期
        ttk.Label(self.dialog, text='截止日期:').grid(row=3, column=0, sticky='w', **padding)
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(self.dialog, textvariable=self.due_date_var, width=30)
        self.due_date_entry.grid(row=3, column=1, sticky='w', **padding)
        ttk.Label(self.dialog, text='(YYYY-MM-DD)').grid(row=3, column=1, sticky='e', padx=10)
        
        # 描述
        ttk.Label(self.dialog, text='描述:').grid(row=4, column=0, sticky='nw', **padding)
        self.desc_text = tk.Text(self.dialog, width=35, height=8, wrap='word')
        self.desc_text.grid(row=4, column=1, sticky='nsew', **padding)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.dialog, orient='vertical', command=self.desc_text.yview)
        scrollbar.grid(row=4, column=2, sticky='ns')
        self.desc_text['yscrollcommand'] = scrollbar.set
        
        # 按钮区域
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=15)
        
        ttk.Button(btn_frame, text='保存', command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='取消', command=self.cancel).pack(side='left', padx=5)
        
        # 配置网格权重
        self.dialog.columnconfigure(1, weight=1)
        self.dialog.rowconfigure(4, weight=1)
    
    def load_data(self, default_category_id=None):
        """加载数据"""
        # 加载分类列表
        categories = self.db_manager.get_all_categories()
        self.category_map = {cat.name: cat.id for cat in categories}
        self.category_combo['values'] = list(self.category_map.keys())
        
        if self.todo:
            # 编辑模式 - 填充现有数据
            self.title_var.set(self.todo.title)
            self.priority_var.set(self.todo.priority)
            self.desc_text.insert('1.0', self.todo.description or '')
            
            if self.todo.due_date:
                self.due_date_var.set(self.todo.due_date.strftime('%Y-%m-%d'))
            
            if self.todo.category_id:
                for name, cid in self.category_map.items():
                    if cid == self.todo.category_id:
                        self.category_var.set(name)
                        break
        else:
            # 新建模式
            if default_category_id:
                for name, cid in self.category_map.items():
                    if cid == default_category_id:
                        self.category_var.set(name)
                        break
    
    def save(self):
        """保存数据"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror('错误', '请输入标题', parent=self.dialog)
            return
        
        description = self.desc_text.get('1.0', 'end-1c').strip()
        priority = self.priority_var.get()
        
        # 获取分类ID
        category_name = self.category_var.get()
        category_id = self.category_map.get(category_name)
        
        # 解析日期
        due_date = None
        date_str = self.due_date_var.get().strip()
        if date_str:
            try:
                due_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror('错误', '日期格式不正确，请使用 YYYY-MM-DD 格式', 
                                   parent=self.dialog)
                return
        
        self.result = {
            'title': title,
            'description': description,
            'priority': priority,
            'category_id': category_id,
            'due_date': due_date
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """取消"""
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并等待结果"""
        self.parent.wait_window(self.dialog)
        return self.result
