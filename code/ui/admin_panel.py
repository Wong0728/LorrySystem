import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from collections import defaultdict

class AdminPanel:
    def __init__(self, root, app):
        self.top = tk.Toplevel(root)
        self.app = app
        self.top.title("管理员面板")
        self.top.geometry("700x550")
        self.top.resizable(False, False)
        
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0", font=("微软雅黑", 12))
        style.configure("TButton", font=("微软雅黑", 12), padding=5)
        style.configure("TLabel", background="#f0f0f0", font=("微软雅黑", 12))
        style.configure("TEntry", font=("微软雅黑", 12))
        style.configure("TCombobox", font=("微软雅黑", 12))
        
        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        rate_frame = ttk.Frame(notebook)
        notebook.add(rate_frame, text="爆率设置")
        
        rate_setting_frame = ttk.LabelFrame(rate_frame, text="爆率设置", padding=10)
        rate_setting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rate_setting_frame, text="模式:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.mode_var = tk.StringVar()
        mode_menu = ttk.Combobox(rate_setting_frame, textvariable=self.mode_var, 
                                values=self.app.modes, state="readonly", width=15)
        mode_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        mode_menu.current(0)
        
        ttk.Label(rate_setting_frame, text="学号:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.number_entry = ttk.Entry(rate_setting_frame, width=15)
        self.number_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(rate_setting_frame, text="爆率(抽中频率):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.rate_entry = ttk.Entry(rate_setting_frame, width=15)
        self.rate_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.rate_entry.insert(0, "5")
        
        btn_frame = ttk.Frame(rate_setting_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="设置爆率", command=self.set_rate, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清除模式设置", command=self.clear_mode_rates, width=15).pack(side=tk.LEFT, padx=5)
        
        chain_setting_frame = ttk.LabelFrame(rate_frame, text="连锁爆率设置", padding=10)
        chain_setting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(chain_setting_frame, text="触发学号:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.trigger_entry = ttk.Entry(chain_setting_frame, width=15)
        self.trigger_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(chain_setting_frame, text="目标学号:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.target_entry = ttk.Entry(chain_setting_frame, width=15)
        self.target_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        chain_btn_frame = ttk.Frame(chain_setting_frame)
        chain_btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(chain_btn_frame, text="设置连锁", command=self.set_chain, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(chain_btn_frame, text="清除连锁", command=self.clear_mode_chains, width=15).pack(side=tk.LEFT, padx=5)
        
        time_frame = ttk.Frame(notebook)
        notebook.add(time_frame, text="时间管理")
        
        time_setting_frame = ttk.LabelFrame(time_frame, text="禁止时间段设置", padding=10)
        time_setting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.time_text = tk.Text(time_setting_frame, height=5, width=40, font=("微软雅黑", 12))
        self.time_text.pack(pady=5, padx=5, fill=tk.X)
        self.update_time_display()
        
        btn_frame = ttk.Frame(time_setting_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="添加时间段", command=self.add_time_range, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除时间段", command=self.remove_time_range, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置为默认", command=self.reset_to_default, width=15).pack(side=tk.LEFT, padx=5)
        
        record_frame = ttk.Frame(notebook)
        notebook.add(record_frame, text="记录管理")
        
        record_setting_frame = ttk.LabelFrame(record_frame, text="记录管理", padding=10)
        record_setting_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        
        ttk.Button(record_setting_frame, text="查看爆率设置", 
                  command=self.show_rate_settings).pack(fill=tk.X, pady=5, padx=20)
        ttk.Button(record_setting_frame, text="查看连锁设置", 
                  command=self.show_chain_settings).pack(fill=tk.X, pady=5, padx=20)
        ttk.Button(record_setting_frame, text="重置所有记录", 
                  command=self.reset_all_records).pack(fill=tk.X, pady=5, padx=20)
        ttk.Button(record_setting_frame, text="清除所有爆率", 
                  command=self.clear_all_rates).pack(fill=tk.X, pady=5, padx=20)
        ttk.Button(record_setting_frame, text="清除所有连锁", 
                  command=self.clear_all_chains).pack(fill=tk.X, pady=5, padx=20)
       
        ttk.Button(main_frame, text="返回", command=self.return_to_lottery).pack(pady=10)

    def return_to_lottery(self):
        self.top.destroy()
        self.app.unlock_frame.pack_forget()
        self.app.admin_frame.pack_forget()
        self.app.normal_frame.pack(expand=True, fill=tk.BOTH)
        # 恢复之前的选择状态
        if hasattr(self.app, 'selected_mode') and self.app.selected_mode:
            self.app.mode_dots[self.app.selected_mode].config(text="●")
        if hasattr(self.app, 'selected_gender') and self.app.selected_gender:
            self.app.gender_dots[self.app.selected_gender].config(text="●")
        self.app.update_button_state()

    def check_usb_drive(self):
        drive_path = filedialog.askdirectory(title="选择U盘路径", parent=self.top)
        if drive_path:
            result = self.app.password_manager.check_usb_drive(drive_path)
            if result == 2:
                messagebox.showinfo("成功", "管理员U盘验证成功！", parent=self.top)
                return True
            elif result == 1:
                messagebox.showinfo("成功", "用户U盘验证成功！", parent=self.top)
                return True
            else:
                messagebox.showerror("错误", "未找到有效的权限文件", parent=self.top)
        return False

    def set_rate(self):
        try:
            mode = self.mode_var.get()
            number = int(self.number_entry.get())
            rate = int(self.rate_entry.get())
            
            if not mode or number <= 0 or rate <= 0:
                messagebox.showerror("错误", "请输入有效的模式、学号和爆率")
                return
                
            if self.app.rate_manager.set_rate(mode, number, rate):
                messagebox.showinfo("成功", "爆率设置成功！")
            else:
                messagebox.showerror("错误", "爆率设置失败")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def set_chain(self):
        try:
            mode = self.mode_var.get()
            trigger = int(self.trigger_entry.get())
            target = int(self.target_entry.get())
            
            if not mode or trigger <= 0 or target <= 0:
                messagebox.showerror("错误", "请输入有效的模式、触发学号和目标学号")
                return
                
            if self.app.rate_manager.set_chain_rule(mode, trigger, target):
                messagebox.showinfo("成功", "连锁爆率设置成功！")
            else:
                messagebox.showerror("错误", "连锁爆率设置失败")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def clear_mode_rates(self):
        mode = self.mode_var.get()
        if mode and messagebox.askyesno("确认", f"确定要清除【{mode}】模式的所有爆率设置吗？", parent=self.top):
            if self.app.rate_manager.clear_rate_settings(mode):
                messagebox.showinfo("成功", f"已清除【{mode}】模式的所有爆率设置")
            else:
                messagebox.showerror("错误", "清除失败")

    def clear_mode_chains(self):
        mode = self.mode_var.get()
        if mode and messagebox.askyesno("确认", f"确定要清除【{mode}】模式的所有连锁设置吗？", parent=self.top):
            if self.app.rate_manager.clear_chain_settings(mode):
                messagebox.showinfo("成功", f"已清除【{mode}】模式的所有连锁设置")
            else:
                messagebox.showerror("错误", "清除失败")

    def clear_all_rates(self):
        if messagebox.askyesno("确认", "确定要清除所有爆率设置吗？", parent=self.top):
            if self.app.rate_manager.clear_rate_settings():
                messagebox.showinfo("成功", "已清除所有爆率设置")
            else:
                messagebox.showerror("错误", "清除失败")

    def clear_all_chains(self):
        if messagebox.askyesno("确认", "确定要清除所有连锁设置吗？", parent=self.top):
            if self.app.rate_manager.clear_chain_settings():
                messagebox.showinfo("成功", "已清除所有连锁设置")
            else:
                messagebox.showerror("错误", "清除失败")

    def show_rate_settings(self):
        rate_settings = self.app.rate_manager.get_rate_settings()
        if not rate_settings:
            messagebox.showinfo("爆率设置", "当前没有设置任何爆率规则", parent=self.top)
            return
        
        top = tk.Toplevel(self.top)
        top.title("爆率设置记录")
        top.geometry("650x450")
        
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True)
        
        tree = ttk.Treeview(frame, columns=("number", "rate", "count", "last"), show="headings")
        tree.heading("number", text="学号")
        tree.heading("rate", text="爆率(每N次)")
        tree.heading("count", text="当前计数")
        tree.heading("last", text="上次抽中时间")
        
        tree.column("number", width=100, anchor="center")
        tree.column("rate", width=120, anchor="center")
        tree.column("count", width=100, anchor="center")
        tree.column("last", width=200, anchor="center")
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        for mode_data in rate_settings:
            mode = mode_data['mode']
            parent = tree.insert("", "end", text=f"模式: {mode}", open=True)
            if 'rules' not in mode_data or not mode_data['rules']:
                tree.insert(parent, "end", values=("无爆率设置", "", "", ""))
                continue
            for rule in sorted(mode_data['rules'], key=lambda x: x[0]):
                number, rate, count, last_draw = rule
                last_time = last_draw.strftime("%Y-%m-%d %H:%M:%S") if last_draw else "从未"
                tree.insert(parent, "end", values=(number, rate, count, last_time))
        
        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
    def show_chain_settings(self):
        chain_settings = self.app.rate_manager.get_chain_settings()
        if not chain_settings:
            messagebox.showinfo("连锁设置", "当前没有设置任何连锁规则", parent=self.top)
            return
        
        top = tk.Toplevel(self.top)
        top.title("连锁设置记录")
        top.geometry("650x450")
        
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True)
        
        tree = ttk.Treeview(frame, columns=("trigger", "target", "last"), show="headings")
        tree.heading("trigger", text="触发学号")
        tree.heading("target", text="目标学号")
        tree.heading("last", text="上次触发时间")
        
        tree.column("trigger", width=120, anchor="center")
        tree.column("target", width=120, anchor="center")
        tree.column("last", width=200, anchor="center")
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        for mode_data in chain_settings:
            mode = mode_data['mode']
            parent = tree.insert("", "end", text=f"模式: {mode}", open=True)
            for rule in sorted(mode_data['rules'], key=lambda x: x[0]):
                trigger, target, last_draw = rule
                last_time = last_draw.strftime("%Y-%m-%d %H:%M:%S") if last_draw else "从未"
                tree.insert(parent, "end", values=(trigger, target, last_time))
        
        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="关闭", command=top.destroy).pack(side="right")

    def reset_all_records(self):
        if messagebox.askyesno("确认", "确定要重置所有抽号记录吗？", parent=self.top):
            if self.app.record_manager.reset_records():
                messagebox.showinfo("成功", "所有记录已重置", parent=self.top)
            else:
                messagebox.showerror("错误", "重置记录失败", parent=self.top)

    def update_time_display(self):
        self.time_text.delete(1.0, tk.END)
        ranges = self.app.time_restriction.get_time_ranges()
        for i, r in enumerate(ranges):
            self.time_text.insert(tk.END, f"{i+1}. {r[0]:02d}:{r[1]:02d} - {r[2]:02d}:{r[3]:02d}\n")

    def add_time_range(self):
        try:
            start_h = simpledialog.askinteger("输入", "请输入开始小时 (0-23):", minvalue=0, maxvalue=23, parent=self.top)
            if start_h is None: return
            start_m = simpledialog.askinteger("输入", "请输入开始分钟 (0-59):", minvalue=0, maxvalue=59, parent=self.top)
            if start_m is None: return
            end_h = simpledialog.askinteger("输入", "请输入结束小时 (0-23):", minvalue=0, maxvalue=23, parent=self.top)
            if end_h is None: return
            end_m = simpledialog.askinteger("输入", "请输入结束分钟 (0-59):", minvalue=0, maxvalue=59, parent=self.top)
            if end_m is None: return
            
            ranges = self.app.time_restriction.get_time_ranges()
            ranges.append((start_h, start_m, end_h, end_m))
            self.app.time_restriction.set_time_ranges(ranges)
            self.update_time_display()
        except:
            messagebox.showerror("错误", "无效输入", parent=self.top)

    def remove_time_range(self):
        try:
            index = simpledialog.askinteger("输入", "请输入要删除的时间段编号:", minvalue=1, parent=self.top)
            if index is None: return
            
            ranges = self.app.time_restriction.get_time_ranges()
            if 1 <= index <= len(ranges):
                ranges.pop(index-1)
                self.app.time_restriction.set_time_ranges(ranges)
                self.update_time_display()
            else:
                messagebox.showerror("错误", "无效编号", parent=self.top)
        except:
            messagebox.showerror("错误", "无效输入", parent=self.top)

    def reset_to_default(self):
        if messagebox.askyesno("确认", "确定要重置为默认禁止时间段吗？", parent=self.top):
            self.app.time_restriction.set_time_ranges(self.app.time_restriction.default_ranges)
            self.update_time_display()
