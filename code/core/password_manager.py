import os
import hashlib

# 用于时间限制文件加密的密钥
ENCRYPTION_KEY = hashlib.sha256(b"lottery_system_secret_key").digest()

class USBDriveManager:
    def __init__(self):
        self.admin_auth = False
        self.user_auth = False
    
    def check_usb_drive(self, drive_path):
        """检查U盘权限"""
        permission_dir = os.path.join(drive_path, "permission")
        
        if not os.path.exists(permission_dir):
            return 0
            
        admin_file = os.path.join(permission_dir, "Administrator.TXT")
        user_file = os.path.join(permission_dir, "User.TXT")
        
        if os.path.exists(admin_file):
            self.admin_auth = True
            return 2  # 管理员权限
            
        if os.path.exists(user_file):
            self.user_auth = True 
            return 1  # 普通用户权限
            
        return 0  # 无权限

    def is_admin_unlocked(self):
        return self.admin_auth
        
    def is_user_unlocked(self):
        return self.user_auth
        
    def reset_auth(self):
        self.admin_auth = False
        self.user_auth = False
        
    def force_user_auth(self, status=True):
        """强制设置用户权限状态"""
        self.user_auth = status
