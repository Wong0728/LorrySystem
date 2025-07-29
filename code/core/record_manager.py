import os
import traceback
from config.cipher import SimpleCipher
from core.log import logger

ENCRYPTION_KEY = b'xQ9!pL3$kZ8#wR5&vN2^mY7*cU1@qS6%fT4(oJ0)hB9_gD8+eK7-lH6=iO5'

class RecordManager:
    def __init__(self):
        self.config_folder = "ConfigEngine"
        self.record_folder = os.path.join(self.config_folder, "LotteryRecords")
        self.student_folder = os.path.join(self.config_folder, "StudentInfo")
        self.modes = ["模式一", "模式二", "模式三", "模式四", "模式五"]
        self.genders = ["boy", "girl"]
        self.ensure_folders_exist()
        self.used_numbers_cache = {mode: set() for mode in self.modes}
        self.gender_numbers_cache = {gender: set() for gender in self.genders}
        self.student_info_cache = {}
        self.load_all_records()
        self.load_student_info()

    def load_all_records(self):
        for mode in self.modes:
            self.used_numbers_cache[mode] = self.get_used_numbers(mode)
        for gender in self.genders:
            self.gender_numbers_cache[gender] = self.get_gender_numbers(gender)

    def load_student_info(self):
        boy_file = os.path.join(self.student_folder, "boys.txt")
        girl_file = os.path.join(self.student_folder, "girls.txt")
        
        try:
            if os.path.exists(boy_file):
                with open(boy_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            number = int(parts[0])
                            name = " ".join(parts[1:])
                            self.student_info_cache[number] = (name, "♂")
            
            if os.path.exists(girl_file):
                with open(girl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            number = int(parts[0])
                            name = " ".join(parts[1:])
                            self.student_info_cache[number] = (name, "♀")
        except Exception as e:
            logger.log({
                "error": "加载学生信息失败",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })

    def ensure_folders_exist(self):
        os.makedirs(self.record_folder, exist_ok=True)
        os.makedirs(self.student_folder, exist_ok=True)
        
        for mode in self.modes:
            mode_file = os.path.join(self.record_folder, f"{mode}.txt")
            if not os.path.exists(mode_file):
                with open(mode_file, "w") as f:
                    pass
        
        boy_file = os.path.join(self.student_folder, "boys.txt")
        girl_file = os.path.join(self.student_folder, "girls.txt")
        if not os.path.exists(boy_file):
            with open(boy_file, "w", encoding="utf-8") as f:
                pass
        if not os.path.exists(girl_file):
            with open(girl_file, "w", encoding="utf-8") as f:
                pass

    def get_record_file(self, mode):
        return os.path.join(self.record_folder, f"{mode}.txt")

    def get_used_numbers(self, mode):
        try:
            with open(self.get_record_file(mode), "r") as f:
                return set(
                    int(SimpleCipher(ENCRYPTION_KEY).decrypt(line.strip()))
                    for line in f if line.strip()
                )
        except Exception:
            return set()

    def get_gender_numbers(self, gender):
        gender_file = os.path.join(self.student_folder, f"{gender}s.txt")
        try:
            with open(gender_file, "r", encoding="utf-8") as f:
                return set(int(line.strip().split()[0]) for line in f if line.strip())
        except Exception:
            return set()

    def add_record(self, mode, numbers):
        try:
            encrypted_lines = [SimpleCipher(ENCRYPTION_KEY).encrypt(str(num)) for num in numbers]
            with open(self.get_record_file(mode), "a") as f:
                f.write("\n".join(encrypted_lines) + "\n")
            self.used_numbers_cache[mode].update(numbers)
            return True
        except Exception as e:
            logger.log({
                "error": "记录添加失败",
                "mode": mode,
                "numbers": numbers,
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def import_history(self, mode, filepath):
        try:
            imported = set()
            with open(filepath, "r") as f:
                for line in f:
                    num = line.strip()
                    if num.isdigit():
                        imported.add(int(num))
            
            if not imported:
                return False
                
            encrypted_lines = [SimpleCipher(ENCRYPTION_KEY).encrypt(str(num)) for num in imported]
            with open(self.get_record_file(mode), "a") as f:
                f.write("\n".join(encrypted_lines) + "\n")
            
            self.used_numbers_cache[mode].update(imported)
            return True
        except Exception as e:
            logger.log({
                "error": "导入历史记录失败",
                "mode": mode,
                "filepath": filepath,
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def reset_records(self, mode=None):
        try:
            if mode:
                with open(self.get_record_file(mode), "w") as f:
                    pass
                self.used_numbers_cache[mode] = set()
            else:
                for m in self.modes:
                    with open(self.get_record_file(m), "w") as f:
                        pass
                    self.used_numbers_cache[m] = set()
            return True
        except Exception as e:
            logger.log({
                "error": "重置记录失败",
                "mode": mode if mode else "all",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def get_student_info(self, number):
        return self.student_info_cache.get(number, ("", ""))
