import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
import win32api
import win32file

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    messagebox.showerror("错误", "请安装tkinterdnd2模块")
    raise

class ImportDataPanel(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("数据导入工具")
        self.geometry("500x350")
        self.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("微软雅黑", 12))
        self.style.configure("TButton", font=("微软雅黑", 12))
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        mode_frame = ttk.LabelFrame(main_frame, text="选择导入模式", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="目标模式:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar()
        mode_menu = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                               values=self.app.modes, state="readonly", width=15, font=("微软雅黑", 12))
        mode_menu.pack(side=tk.LEFT, padx=5)
        mode_menu.current(0)
        
        # 新增确认按钮
        self.confirm_btn = ttk.Button(mode_frame, text="确认", command=self.confirm_import, 
                                    state="disabled")
        self.confirm_btn.pack(side=tk.LEFT, padx=5)
        
        drop_frame = ttk.LabelFrame(main_frame, text="拖放文件区域", padding=10)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.drop_label = tk.Label(drop_frame, text="将TXT文件拖放到此区域\n\n(文件内容应为每行一个数字)", 
                                 relief="groove", bg="white", height=8, 
                                 font=("微软雅黑", 12), padx=20, pady=20)
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.bind("<Enter>", self.on_drag_enter)
        self.drop_label.bind("<Leave>", self.on_drag_leave)
        
        # 添加手动选择文件按钮
        select_btn = ttk.Button(drop_frame, text="选择TXT文件", command=self.select_file)
        select_btn.pack(pady=10)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        self.process_btn = ttk.Button(btn_frame, text="处理文件", command=self.process_file, state="disabled")
        self.process_btn.pack(side=tk.LEFT, padx=5)
        self.current_file = None
        ttk.Button(btn_frame, text="关闭", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("等待文件拖入...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="blue", font=("微软雅黑", 12)).pack()
        
        self.after(500, self.check_usb_drives)  # 开始自动检测

    def on_drag_enter(self, event):
        self.drop_label.config(bg="#e6f3ff")
        self.status_var.set("释放鼠标导入文件...")
    
    def on_drag_leave(self, event):
        self.drop_label.config(bg="white")
        self.status_var.set("等待文件拖入...")
    
    def select_file(self):
        """手动选择文件"""
        filepath = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
            
        self.current_file = filepath.replace('\\', '/')
        # 不直接启用处理按钮，等待检测到U盘
        self.status_var.set(f"已选择文件: {os.path.basename(filepath)}")
        self.status_var.set(f"已选择文件: {os.path.basename(filepath)}")
        
        if not filepath.lower().endswith(".txt"):
            self.status_var.set("错误: 只支持TXT文件")
            messagebox.showerror("错误", "只支持TXT格式的文件")
            return
        
        if not self.mode_var.get():
            self.status_var.set("错误: 请先选择模式")
            messagebox.showerror("错误", "请先选择导入模式")
            return
        
        try:
            self.status_var.set("正在导入数据...")
            self.update()
            
            success = self.app.record_manager.import_history(self.mode_var.get(), filepath)
            
            if success:
                self.status_var.set("导入成功!")
                messagebox.showinfo("成功", f"数据已成功导入到【{self.mode_var.get()}】模式")
                self.on_close()
            else:
                self.status_var.set("导入失败")
                messagebox.showerror("错误", "数据导入失败，请检查文件格式")
                
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"导入过程中发生错误: {str(e)}")
    
    def check_usb_drives(self):
        """显示U盘检测状态"""
        self.status_var.set("请点击确认按钮导入文件")
        self.process_btn.config(state="disabled")
    
    # 删除手动选择盘符的相关方法
    # 使用管理员U盘进行数据导入，自动检测直到找到key文件
    
    def on_drop(self, event):
        """处理拖放的文件"""
        filepath = event.data.strip().replace('{', '').replace('}', '')
        if not filepath.lower().endswith('.txt'):
            messagebox.showerror("错误", "只支持TXT格式的文件")
            return
            
        self.current_file = filepath
        filename = os.path.basename(filepath)
        self.drop_label.config(text=f"已拖入文件:\n{filename}\n\n(点击确认按钮处理)")
        self.status_var.set(f"已拖入文件: {filename}")
        if hasattr(self, 'confirm_btn'):
            self.confirm_btn.config(state="normal")

    def process_file(self):
        """处理已拖入的文件"""
        if not self.current_file:
            messagebox.showerror("错误", "没有可处理的文件")
            return
            
        if not self.mode_var.get():
            messagebox.showerror("错误", "请先选择导入模式")
            return
            
        try:
            self.status_var.set("正在处理文件...")
            self.update()
            
            success = self.app.record_manager.import_history(self.mode_var.get(), self.current_file)
            
            if success:
                self.status_var.set("处理成功!")
                messagebox.showinfo("成功", f"数据已成功导入到【{self.mode_var.get()}】模式")
                self.on_close()
            else:
                self.status_var.set("处理失败")
                messagebox.showerror("错误", "数据处理失败")
                
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")

    def confirm_import(self):
        """确认导入文件"""
        if not self.current_file:
            messagebox.showerror("错误", "没有可处理的文件")
            return
            
        if not self.mode_var.get():
            messagebox.showerror("错误", "请先选择导入模式")
            return
            
        # 检测管理员U盘
        drives = [d for d in win32api.GetLogicalDriveStrings().split('\x00') if d]
        removable_drives = [d for d in drives if win32file.GetDriveType(d) == win32file.DRIVE_REMOVABLE]
        
        for drive in removable_drives:
            admin_key_path = os.path.join(drive, "permission\\Administrator.txt")
            if os.path.exists(admin_key_path):
                try:
                    self.status_var.set("正在处理文件...")
                    self.update()
                    
                    success = self.app.record_manager.import_history(self.mode_var.get(), self.current_file)
                    
                    if success:
                        self.status_var.set("导入成功!")
                        messagebox.showinfo("成功", f"数据已成功导入到【{self.mode_var.get()}】模式")
                        self.on_close()
                    else:
                        self.status_var.set("导入失败")
                        messagebox.showerror("错误", "数据导入失败，请检查文件格式")
                    return
                    
                except Exception as e:
                    self.status_var.set(f"错误: {str(e)}")
                    messagebox.showerror("错误", f"导入过程中发生错误: {str(e)}")
                    return
        
        messagebox.showerror("错误", "未检测到管理员U盘，请插入管理员U盘后重试")
        return  # 保持当前界面

    def on_close(self):
        self.app.password_manager.reset_auth()
        self.destroy()
