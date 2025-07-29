import tkinter as tk
from tkinter import font, ttk, simpledialog, messagebox, filedialog
import random
import os
import pickle
from datetime import datetime
import win32api
import win32file
from core.password_manager import USBDriveManager
from core.record_manager import RecordManager
from core.rate_manager import RateManager
from config.time_manager import TimeRestriction
from ui.admin_panel import AdminPanel
from ui.import_panel import ImportDataPanel

class LotteryApp:
    def __init__(self, root):
        from core.log import LogManager
        self.logger = LogManager(debug_mode=True)
        
        self.root = root
        self.root.title("智能抽号系统")
        self.logger.log("Initializing lottery application")
        
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.root.option_add("*Font", default_font)
        
        self.password_manager = USBDriveManager()
        self.record_manager = RecordManager()
        self.rate_manager = RateManager()
        self.time_restriction = TimeRestriction()
        
        self.modes = self.record_manager.modes
        self.genders = self.record_manager.genders
        
        self.base_width = 650
        self.base_height = 500
        self.root.geometry(f"{self.base_width}x{self.base_height}")
        self.root.minsize(self.base_width, self.base_height)
        
        self.blinking = False
        self.numbers_to_show = []
        self.current_number_index = 0
        self.selected_mode = None
        self.selected_gender = None
        self.admin_mode = False
        self.chain_triggered = False
        
        self.base_size = 16
        self.result_base_size = 120
        self.name_font_size = 24
        self.base_font = font.Font(family="微软雅黑", size=self.base_size, weight="bold")
        self.result_font = font.Font(family="微软雅黑", size=self.result_base_size, weight="bold")
        self.name_font = font.Font(family="微软雅黑", size=self.name_font_size)
        
        # 先创建所有界面
        self.create_normal_interface() 
        self.create_admin_interface()
        self.create_unlock_interface()
        
        # 确保所有界面都创建好后，再决定显示哪个
        if self.time_restriction.is_time_allowed() or self.password_manager.is_user_unlocked():
            self.enter_normal_mode()
        else:
            self.unlock_frame.pack(pady=50)
            self.check_usb_drive()  # 开始自动检测
        
        self.root.after(1000, self.periodic_check)

    def create_unlock_interface(self):
        self.unlock_frame = ttk.Frame(self.root, padding=20)
        
        title_label = ttk.Label(self.unlock_frame, text="智能抽号系统", 
                              font=("微软雅黑", 24, "bold"))
        title_label.pack(pady=20)
        
        unlock_frame = ttk.Frame(self.unlock_frame)
        unlock_frame.pack(pady=10)
        
        self.usb_btn = ttk.Button(unlock_frame, text="检测U盘中...", 
                                command=self.check_usb_drive, 
                                style="Large.TButton")
        self.usb_btn.pack(side=tk.LEFT, padx=5)
        self.drive_frame = ttk.LabelFrame(self.unlock_frame)  # 提前创建盘符选择框
        self.attempt_count = 0
        self.max_attempts = 5
        self.drive_buttons = []
        self.check_usb_drive()  # 自动开始检测

    def create_normal_interface(self):
        self.normal_frame = ttk.Frame(self.root)
        
        self.mode_frame = ttk.Frame(self.normal_frame)
        self.mode_dots = {}
        
        ttk.Label(self.mode_frame, text="选择模式：", 
                 font=self.base_font).pack(side=tk.LEFT)
        
        for mode in self.modes:
            dot = tk.Label(self.mode_frame, text="○", font=("Arial", 16),
                          cursor="hand2")
            dot.pack(side=tk.LEFT, padx=8)
            dot.bind("<Button-1>", lambda e, m=mode: self.toggle_mode(m))
            self.mode_dots[mode] = dot
            ttk.Label(self.mode_frame, text=mode, font=("微软雅黑", 12)).pack(side=tk.LEFT)
        
        self.mode_frame.pack(side=tk.TOP, pady=5)

        control_frame = ttk.Frame(self.normal_frame)
        
        ttk.Label(control_frame, text="最大号码：", 
                font=self.base_font).grid(row=0, column=0, padx=5)
        self.max_num_entry = ttk.Entry(control_frame, font=self.base_font, width=8)
        self.max_num_entry.grid(row=0, column=1, padx=5)
        self.max_num_entry.insert(0, "50")
        
        ttk.Label(control_frame, text="抽号数量：", 
                font=self.base_font).grid(row=0, column=2, padx=5)
        self.quantity_entry = ttk.Entry(control_frame, font=self.base_font, width=5)
        self.quantity_entry.grid(row=0, column=3, padx=5)
        self.quantity_entry.insert(0, "1")
        
        self.gender_dots = {}
        gender_frame = ttk.Frame(control_frame)
        
        # 检查是否有男生数据
        has_boys = len(self.record_manager.gender_numbers_cache.get("boy", [])) > 0
        self.gender_dots["boy"] = tk.Label(gender_frame, text="○", fg="blue" if has_boys else "gray", 
                                         font=("Arial", 16), cursor="hand2" if has_boys else "arrow")
        self.gender_dots["boy"].pack(side=tk.LEFT)
        if has_boys:
            self.gender_dots["boy"].bind("<Button-1>", lambda e: self.toggle_gender("boy"))
        ttk.Label(gender_frame, text="男生", font=("微软雅黑", 12), foreground="blue" if has_boys else "gray").pack(side=tk.LEFT, padx=2)
        
        # 检查是否有女生数据
        has_girls = len(self.record_manager.gender_numbers_cache.get("girl", [])) > 0
        self.gender_dots["girl"] = tk.Label(gender_frame, text="○", fg="red" if has_girls else "gray", 
                                          font=("Arial", 16), cursor="hand2" if has_girls else "arrow")
        self.gender_dots["girl"].pack(side=tk.LEFT)
        if has_girls:
            self.gender_dots["girl"].bind("<Button-1>", lambda e: self.toggle_gender("girl"))
        ttk.Label(gender_frame, text="女生", font=("微软雅黑", 12), foreground="red" if has_girls else "gray").pack(side=tk.LEFT, padx=2)
        gender_frame.grid(row=0, column=4, padx=10)
        
        control_frame.pack(side=tk.TOP, pady=10)

        self.btn = ttk.Button(self.normal_frame, text="开始抽号", command=self.start_lottery, style="Large.TButton")
        self.btn.pack(pady=15)

        result_frame = ttk.Frame(self.normal_frame)
        
        self.result = ttk.Label(result_frame, text="", font=self.result_font,
                              anchor="center", justify="center")
        self.result.pack(expand=True, fill=tk.X)
        
        self.name_label = ttk.Label(result_frame, text="", font=self.name_font,
                                  anchor="center", justify="center")
        self.name_label.pack(expand=True, fill=tk.X)
        
        result_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        status_frame = ttk.Frame(self.normal_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.dev_dot = tk.Label(status_frame, text="•", font=("Arial", 24),
                               fg="red", cursor="hand2")
        self.dev_dot.pack(side=tk.RIGHT, padx=10)
        self.dev_dot.bind("<Button-1>", self.show_dev_info)
        
        self.status_label = ttk.Label(status_frame, text="普通模式", font=("微软雅黑", 12))
        self.status_label.pack(side=tk.LEFT)

    def create_admin_interface(self):
        self.admin_frame = ttk.Frame(self.root)
        
        btn_frame = ttk.Frame(self.admin_frame)
        ttk.Button(btn_frame, text="管理员设置", command=self.show_admin_panel, style="Large.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="返回", command=lambda: self.return_to_unlock(from_admin=True), style="Large.TButton").pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=10)
        
        status_frame = ttk.Frame(self.admin_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.admin_status = ttk.Label(status_frame, text="管理员模式", 
                                    foreground="red", font=("微软雅黑", 12))
        self.admin_status.pack(side=tk.LEFT)

    def check_usb_drive(self):
        """自动检测U盘并验证权限文件"""
        self.usb_btn.config(state="disabled")  # 禁用按钮防止重复点击
        self.auto_check_usb_drive()

    def auto_check_usb_drive(self):
        """自动检测U盘"""
        drives = [d for d in win32api.GetLogicalDriveStrings().split('\x00') if d]
        removable_drives = [d for d in drives if win32file.GetDriveType(d) == win32file.DRIVE_REMOVABLE]
        
        for drive in removable_drives:
            result = self.password_manager.check_usb_drive(drive)
            if result == 2:
                self.enter_admin_mode()
                return
            elif result == 1:
                self.enter_normal_mode()
                return
        
        self.attempt_count += 1
        if self.attempt_count >= self.max_attempts:
            self.show_all_drives(drives)
        else:
            self.usb_btn.config(text=f"检测中... ({self.attempt_count}/{self.max_attempts})")
            self.root.after(1000, self.auto_check_usb_drive)

    def show_all_drives(self, drives):
        """显示所有盘符供手动选择"""
        self.clear_drive_buttons()
        
        self.drive_frame.config(text="请选择包含key文件的盘符")
        self.drive_frame.pack(pady=10)
        
        for drive in drives:
            btn = ttk.Button(self.drive_frame, text=drive, 
                           command=lambda d=drive: self.on_drive_selected(d))
            btn.pack(side=tk.LEFT, padx=5)
            self.drive_buttons.append(btn)
        
        self.usb_btn.config(text="自动检测失败")
        # 继续检测新插入的U盘
        self.root.after(2000, self.continue_check_new_drives)

    def continue_check_new_drives(self):
        """继续检测新插入的U盘"""
        current_drives = [d for d in win32api.GetLogicalDriveStrings().split('\x00') if d]
        removable_drives = [d for d in current_drives if win32file.GetDriveType(d) == win32file.DRIVE_REMOVABLE]
        
        # 如果有新增的U盘，重新开始自动检测
        if len(removable_drives) > len(self.drive_buttons):
            self.clear_drive_buttons()
            self.drive_frame.pack_forget()
            self.attempt_count = 0
            self.auto_check_usb_drive()
        else:
            # 继续每2秒检查一次
            self.root.after(2000, self.continue_check_new_drives)

    def clear_drive_buttons(self):
        """清除所有盘符按钮"""
        for btn in self.drive_buttons:
            btn.destroy()
        self.drive_buttons = []

    def on_drive_selected(self, drive):
        """处理盘符选择"""
        self.usb_btn.config(state="disabled", text=f"正在验证{drive}...")
        self.root.update()
        
        result = self.password_manager.check_usb_drive(drive)
        if result == 2:
            self.enter_admin_mode()
        elif result == 1:
            self.enter_normal_mode()
        else:
            messagebox.showerror("错误", "未找到有效的权限文件")
        
        self.drive_frame.pack_forget()
        self.usb_btn.config(state="normal", text="验证U盘")

    def check_time_restriction(self):
        # 管理员模式自动拥有所有权限
        if self.admin_mode:
            return True
        # 普通模式需要检查用户U盘或时间限制
        return self.password_manager.is_user_unlocked() or self.time_restriction.is_time_allowed()

    def periodic_check(self):
        try:
            if not self.admin_mode:
                current_allowed = self.time_restriction.is_time_allowed()
                user_unlocked = self.password_manager.is_user_unlocked()
                
                # 如果当前在抽号界面且时间不可用，立即返回验证界面
                if (self.normal_frame.winfo_ismapped() and 
                    not current_allowed and 
                    not user_unlocked):
                    if not hasattr(self, '_last_unlock_time') or \
                       (datetime.now() - self._last_unlock_time).total_seconds() > 5:
                        self._last_unlock_time = datetime.now()
                        self.return_to_unlock()
                    return
                
                # 如果当前在验证界面但时间可用或已解锁，进入抽号界面
                elif (self.unlock_frame.winfo_ismapped() and 
                      (current_allowed or user_unlocked)):
                    if not hasattr(self, '_last_normal_time') or \
                       (datetime.now() - self._last_normal_time).total_seconds() > 5:
                        self._last_normal_time = datetime.now()
                        self.enter_normal_mode()
                    return
                    
                # 如果已经从管理员界面返回并且处于normal模式，不再重复触发
                elif (self.normal_frame.winfo_ismapped() and
                      hasattr(self, '_from_admin') and self._from_admin):
                    # 额外检查当前界面状态
                    if not self.unlock_frame.winfo_ismapped():
                        return
                    
                # 如果当前在normal模式且有用户权限，不再返回
                elif (self.normal_frame.winfo_ismapped() and
                      user_unlocked):
                    return
                    
        except Exception as e:
            self.logger.log(f"Periodic check error: {str(e)}")
        finally:
            self.root.after(1000, self.periodic_check)

    def return_to_unlock(self, from_admin=False):
        self.admin_mode = False
        self.unlock_frame.pack_forget()
        self.admin_frame.pack_forget()
        
        if from_admin:
            # 从管理员界面返回，直接进入normal模式
            self._from_admin = True  # 标记来自管理员界面
            self.password_manager.reset_auth()
            self.password_manager.force_user_auth(True)  # 使用正式方法强制设置用户权限
            self.normal_frame.pack(expand=True, fill=tk.BOTH)
            self.logger.log("Admin returning to normal interface")
        else:
            # 正常返回unlock界面
            self._from_admin = False  # 清除标记
            self.unlock_frame.pack(pady=50)
            self.logger.log("Returning to unlock interface")
        
        # 强制重置界面状态
        self.selected_mode = None
        self.selected_gender = None
        
        # 重置所有模式选择点
        for mode in self.modes:
            self.mode_dots[mode].config(text="○")
        
        # 重置性别选择点
        for gender in self.genders:
            self.gender_dots[gender].config(text="○")
            
        # 强制刷新界面并更新按钮状态
        self.root.update()
        self.update_button_state()

    def enter_normal_mode(self):
        self.admin_mode = False
        self.unlock_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.normal_frame.pack(expand=True, fill=tk.BOTH)
        self._from_admin = False  # 确保清除管理员标志
        self.update_button_state()

    def enter_admin_mode(self):
        self.admin_mode = True
        self.unlock_frame.pack_forget()
        self.normal_frame.pack_forget()
        self.admin_frame.pack(expand=True, fill=tk.BOTH)

    def toggle_mode(self, mode):
        if not self.check_time_restriction():
            return
            
        if self.selected_mode == mode:
            self.mode_dots[mode].config(text="○")
            self.selected_mode = None
        else:
            if self.selected_mode:
                self.mode_dots[self.selected_mode].config(text="○")
            self.mode_dots[mode].config(text="●")
            self.selected_mode = mode
        self.update_button_state()

    def toggle_gender(self, gender):
        if not self.check_time_restriction():
            return
            
        if self.selected_gender == gender:
            self.gender_dots[gender].config(text="○")
            self.selected_gender = None
        else:
            if self.selected_gender:
                self.gender_dots[self.selected_gender].config(text="○")
            self.gender_dots[gender].config(text="●")
            self.selected_gender = gender
        self.update_button_state()

    def update_button_state(self):
        try:
            valid_max = self.max_num_entry.get().isdigit() and 1 <= int(self.max_num_entry.get()) <= 100
            valid_quantity = self.quantity_entry.get().isdigit() and 1 <= int(self.quantity_entry.get()) <= 5
            ready = all([
                valid_max,
                valid_quantity,
                self.selected_mode is not None,
                not self.blinking,
                self.check_time_restriction()
            ])
            
            self.btn.state(['!disabled' if ready else 'disabled'])
        except:
            self.btn.state(['disabled'])

    def start_lottery(self):
        if not self.check_time_restriction():
            return
            
        if not self.selected_mode:
            return
        
        try:
            max_num = int(self.max_num_entry.get())
            quantity = int(self.quantity_entry.get())
            if not (1 <= max_num <= 100) or not (1 <= quantity <=5):
                return
        except:
            return
        
        # 初始化可用号码(不检查是否重复)
        available = set(range(1, max_num+1))
        gender_numbers = None
        if self.selected_gender:
            gender_numbers = self.record_manager.gender_numbers_cache[self.selected_gender]
            available = available & gender_numbers
        
        self.numbers_to_show = []
        remaining = quantity
        temp_available = list(available)

        i = 0
        while i < remaining and temp_available:
            # 优先检查连锁规则
            if self.numbers_to_show:
                last_num = self.numbers_to_show[-1]
                chain_dict = self.rate_manager.check_chain(
                    self.selected_mode,
                    [last_num],
                    temp_available,
                    gender_numbers
                )
                # 强制应用连锁规则(如果目标号码符合性别要求)
                if last_num in chain_dict:
                    target_num = chain_dict[last_num]["目标号码"]
                    if gender_numbers is None or target_num in gender_numbers:
                        self.numbers_to_show.append(target_num)
                        temp_available.remove(target_num)
                        i += 1
                        continue

            # 其次检查爆率设置
            adjusted = self.rate_manager.check_rate(
                self.selected_mode, 
                temp_available,
                gender_numbers
            )
            if adjusted:
                selected = random.choice(adjusted)
                self.numbers_to_show.append(selected)
                temp_available.remove(selected)
                i += 1
                continue

            # 最后随机选择
            if gender_numbers:
                available = [n for n in temp_available if n in gender_numbers]
            else:
                available = temp_available.copy()
                
            if available:
                selected = random.choice(available)
                self.numbers_to_show.append(selected)
                temp_available.remove(selected)
                i += 1

        if self.numbers_to_show:
            self.record_manager.add_record(self.selected_mode, self.numbers_to_show)
            # 模式名称映射
            mode_mapping = {
                "模式一": "Mode1",
                "模式二": "Mode2", 
                "模式三": "Mode3",
                "模式四": "Mode4",
                "模式五": "Mode5"
            }
            mode_en = mode_mapping.get(self.selected_mode, self.selected_mode)
            
            # 生成JSON格式日志
            log_data = {
                "mode": mode_en,
                "drawn_numbers": self.numbers_to_show,
                "rate_info": [],
                "chain_info": {
                    "trigger_status": "not triggered",
                    "trigger_condition": None,
                    "target_number": None
                },
                "gender_restriction": self.selected_gender or "none",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.logger.log(log_data)
            
            # 记录学生信息 (JSON格式)
            student_logs = []
            for num in self.numbers_to_show:
                name, gender = self.record_manager.get_student_info(num)
                if name:
                    gender_en = "Male" if gender == "♂" else "Female" if gender == "♀" else "Unknown"
                    student_logs.append({
                        "number": num,
                        "name": name,
                        "gender": gender_en
                    })
            
            if student_logs:
                self.logger.log({
                    "students": student_logs,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # 确保前后端一致，重新从rate_manager获取实际抽中号码
            final_numbers = []
            for num in self.numbers_to_show:
                rate_files = [f for f in os.listdir(self.rate_manager.rate_folder) 
                            if f.endswith(".rate")]
                for filename in rate_files:
                    try:
                        with open(os.path.join(self.rate_manager.rate_folder, filename), "rb") as f:
                            data = pickle.load(f)
                            if data["number"] == num and data["mode"] == self.selected_mode:
                                data["count"] = 0 if data["count"] >= data["rate"] else data["count"]
                                final_numbers.append(num)
                                break
                    except:
                        continue
            
            self.numbers_to_show = final_numbers if final_numbers else self.numbers_to_show
        
        self.current_number_index = 0
        self.btn.state(['disabled'])
        if quantity == 1:
            self.run_single_animation(max_num)
        else:
            self.run_multi_animation()

    def run_single_animation(self, max_num):
        if not self.numbers_to_show:
            self.logger.log("Error: No numbers to show in animation")
            return
            
        self.blinking = True
        start_time = datetime.now()
        self.animate_number(max_num, start_time)

    def animate_number(self, max_num, start_time):
        elapsed = (datetime.now() - start_time).total_seconds()
        if elapsed < 2.0:
            random_num = random.randint(1, max_num)
            self.result.config(text=str(random_num))
            name, gender = self.record_manager.get_student_info(random_num)
            self.name_label.config(text=f"{name} {gender}" if name else "", 
                                 foreground="black")
            if gender == "♂":
                text = self.name_label.cget("text")
                if "♂" in text:
                    self.name_label.config(text=text.replace("♂", "♂"))
            elif gender == "♀":
                text = self.name_label.cget("text")
                if "♀" in text:
                    self.name_label.config(text=text.replace("♀", "♀"))
            self.root.after(100, lambda: self.animate_number(max_num, start_time))
        else:
            final_num = self.numbers_to_show[0]
            self.result.config(text=str(final_num))
            name, gender = self.record_manager.get_student_info(final_num)
            self.name_label.config(text=f"{name} {gender}" if name else "", 
                                 foreground="black")
            if gender == "♂":
                text = self.name_label.cget("text")
                if "♂" in text:
                    self.name_label.config(text=text.replace("♂", "♂"))
            elif gender == "♀":
                text = self.name_label.cget("text")
                if "♀" in text:
                    self.name_label.config(text=text.replace("♀", "♀"))
            self.blinking = False
            self.update_button_state()

    def run_multi_animation(self):
        self.blinking = True
        self.show_next_number()

    def show_next_number(self):
        if self.current_number_index < len(self.numbers_to_show):
            num = self.numbers_to_show[self.current_number_index]
            self.result.config(text=str(num))
            name, gender = self.record_manager.get_student_info(num)
            self.name_label.config(text=f"{name} {gender}" if name else "", 
                                 foreground="black")
            if gender == "♂":
                text = self.name_label.cget("text")
                if "♂" in text:
                    self.name_label.config(text=text.replace("♂", "♂"))
            elif gender == "♀":
                text = self.name_label.cget("text")
                if "♀" in text:
                    self.name_label.config(text=text.replace("♀", "♀"))
            self.current_number_index += 1
            self.root.after(600, self.show_next_number)
        else:
            self.blinking = False
            self.update_button_state()
            if self.selected_gender:
                self.gender_dots[self.selected_gender].config(text="○")
                self.selected_gender = None
            self.update_button_state()

    def show_admin_panel(self):
        panel = AdminPanel(self.root, self)
        panel.top.transient(self.root)  # 确保弹窗显示在主窗口之上
        panel.top.grab_set()  # 模态窗口

    def show_dev_info(self, event=None):
        # 管理员模式直接打开导入界面
        if self.admin_mode:
            self.logger.log("Admin mode opening import panel")
            panel = ImportDataPanel(self.root, self)
            panel.transient(self.root)
            panel.grab_set()
        elif self.password_manager.is_user_unlocked():
            self.logger.log("User mode opening import panel")
            panel = ImportDataPanel(self.root, self)
            panel.transient(self.root)
            panel.grab_set()
        else:
            self.logger.log("Attempted to open import panel without verified USB")
            messagebox.showerror("错误", "请先验证用户U盘")
