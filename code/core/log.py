import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from config.cipher import SimpleCipher
from config.cipher import ENCRYPTION_KEY

class LogManager:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.log_dir = Path("logs") if debug_mode else None
        self.log_file = self.log_dir / "system.log" if debug_mode else None
        self.cipher = SimpleCipher(ENCRYPTION_KEY)
        
        if debug_mode:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message):
        if not self.debug_mode:
            return
            
        if isinstance(message, dict):  # JSON格式日志
            log_data = message
        else:  # 文本格式日志
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_data = {"message": f"[{timestamp}] {message}"}
        
        # 打印到终端
        print(json.dumps(log_data, indent=2, ensure_ascii=False))
        # 明文存储到文件
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    json.dump(log_data, f, ensure_ascii=False)
                    f.write("\n")
            except Exception as e:
                print(f"Logging failed: {str(e)}")
    
    def read_logs(self):
        if not self.log_file.exists():
            return "No logs found"
            
        with open(self.log_file, "r", encoding="utf-8") as f:
            logs = []
            for line in f:
                try:
                    decrypted = self.cipher.decrypt(line.strip())
                    logs.append(decrypted)
                except:
                    continue
            return "\n".join(logs)

logger = LogManager(False)  # 设置为False关闭调试模式
