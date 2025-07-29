import tkinter as tk
from tkinter import ttk
import sys
import os
import ctypes
import base64
from datetime import datetime
from pathlib import Path
from config.cipher import SimpleCipher
from core.password_manager import ENCRYPTION_KEY

from core.log import logger
logger.log("System started")
try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    import tkinter.messagebox as messagebox
    messagebox.showerror("Error", "Please install tkinterdnd2 module")
    sys.exit(1)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.lottery_app import LotteryApp

def hide_console():
    if sys.platform == "win32":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_console():
    if sys.platform == "win32":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

if __name__ == "__main__":
    try:
        hide_console()
        root = TkinterDnD.Tk()
        style = ttk.Style()
        style.configure("Large.TButton", font=("微软雅黑", 14))
        LotteryApp(root)
        root.mainloop()
    except Exception as e:
        show_console()
        import traceback
        traceback.print_exc()
        input("Program crashed, press Enter to exit...")
