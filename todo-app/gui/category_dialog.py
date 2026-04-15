"""分类管理对话框"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser


class CategoryDialog:
    """分类管理对话框"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('管理分类')
        self.dialog.geometry('400x350')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.refresh_list()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        padding = {'padx': 10, 'pady': 5}
        
        # 添加新分类区域
        add_frame = ttk.LabelFrame(self.dialog, text='添加新分类', padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(add_frame, text='名称:').grid(row=0, column=0, sticky='w')
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(add_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        self.color_var = tk.StringVar(value='#4A90D9')
        self.color_btn = tk.Button(add_frame, text='选择颜色', 
                                   bg=self.color_var.get(),
                                   command=self.choose_color)
        self.color_btn.grid(row=0, column=2, padx=5)
        
        ttk.Button(add_frame, text='添加', command=self.add_category).grid(row=0, column=3, padx=5)
        
        # 分类列表
        list_frame = ttk.LabelFrame(self.dialog, text='现有分类', padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('name', 'color')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                height=8, selectmode='browse')
        
        self.tree.heading('name', text='名称')
        self.tree.heading('color', text='颜色')
        self.tree.column('name', width=150)
        self.tree.column('color', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 按钮区域
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text='删除选中', command=self.delete_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='关闭', command=self.dialog.destroy).pack(side='right', padx=5)
        
        # 绑定双击编辑颜色
        self.tree.bind('<Double-1>', self.edit_color)
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(color=self.color_var.get(), title='选择颜色')[1]
        if color:
            self.color_var.set(color)
            self.color_btn.configure(bg=color)
    
    def add_category(self):
        """添加分类"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror('错误', '请输入分类名称', parent=self.dialog)
            return
        
        try:
            self.db_manager.add_category(name, self.color_var.get())
            self.name_var.set('')
            self.refresh_list()
        except Exception as e:
            messagebox.showerror('错误', f'添加分类失败: {e}', parent=self.dialog)
    
    def refresh_list(self):
        """刷新分类列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 加载分类
        categories = self.db_manager.get_all_categories()
        self.category_items = {}  # 存储 item -> id 映射
        
        for cat in categories:
            item = self.tree.insert('', 'end', values=(cat.name, ''))
            # 在颜色列显示色块
            self.tree.set(item, 'color', cat.color)
            # 设置行颜色
            self.tree.tag_configure(f'color_{cat.id}', background=cat.color)
            self.category_items[item] = cat.id
    
    def delete_category(self):
        """删除分类"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个分类', parent=self.dialog)
            return
        
        item = selection[0]
        category_id = self.category_items.get(item)
        category_name = self.tree.item(item, 'values')[0]
        
        if messagebox.askyesno('确认', f'确定要删除分类 "{category_name}" 吗？\n该分类下的任务将变为未分类。',
                              parent=self.dialog):
            try:
                self.db_manager.delete_category(category_id)
                self.refresh_list()
            except Exception as e:
                messagebox.showerror('错误', f'删除分类失败: {e}', parent=self.dialog)
    
    def edit_color(self, event):
        """双击编辑颜色"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        category_id = self.category_items.get(item)
        current_color = self.tree.set(item, 'color')
        
        color = colorchooser.askcolor(color=current_color, title='选择新颜色')[1]
        if color:
            try:
                self.db_manager.update_category(category_id, color=color)
                self.refresh_list()
            except Exception as e:
                messagebox.showerror('错误', f'更新颜色失败: {e}', parent=self.dialog)
    
    def show(self):
        """显示对话框"""
        self.parent.wait_window(self.dialog)
