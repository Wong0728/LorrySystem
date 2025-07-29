import os
from datetime import datetime, time
from config.cipher import SimpleCipher
from core.password_manager import ENCRYPTION_KEY
class TimeRestriction:
    def __init__(self):
        self.config_folder = "ConfigEngine"
        self.time_folder = os.path.join(self.config_folder, "TimeRestrictions")
        self.time_file = os.path.join(self.time_folder, "time_ranges.enc")
        self.ensure_folders_exist()
        
        self.default_ranges = [
            (1, 0, 7, 25), (8, 25, 8, 35),
            (9, 20, 9, 40), (10, 20, 11, 30),
            (11, 10, 11, 20),(11, 10, 17, 20),
            (15, 0, 16, 15), (16, 50, 17, 5),
            (17, 35, 23, 59)
        ]
        self.load_or_create_time_restriction()

    def ensure_folders_exist(self):
        os.makedirs(self.time_folder, exist_ok=True)

    def load_or_create_time_restriction(self):
        if not os.path.exists(self.time_file):
            self.save_time_ranges(self.default_ranges)
        else:
            try:
                with open(self.time_file, "r") as f:
                    encrypted = f.read()
                    decrypted = SimpleCipher(ENCRYPTION_KEY).decrypt(encrypted)
                    ranges = []
                    for line in decrypted.splitlines():
                        if line.strip():
                            parts = line.strip().split()
                            if len(parts) == 4:
                                ranges.append(tuple(map(int, parts)))
                    self.time_ranges = ranges
            except:
                self.save_time_ranges(self.default_ranges)

    def save_time_ranges(self, ranges):
        lines = []
        for r in ranges:
            lines.append(f"{r[0]} {r[1]} {r[2]} {r[3]}")
        content = "\n".join(lines)
        encrypted = SimpleCipher(ENCRYPTION_KEY).encrypt(content)
        with open(self.time_file, "w") as f:
            f.write(encrypted)
        self.time_ranges = ranges

    def is_time_allowed(self):
        now = datetime.now().time()
        for r in self.time_ranges:
            start_time = time(hour=r[0], minute=r[1])
            end_time = time(hour=r[2], minute=r[3])
            if start_time <= end_time:
                if start_time <= now <= end_time:
                    return False
            else:
                if now >= start_time or now <= end_time:
                    return False
        return True

    def get_time_ranges(self):
        return self.time_ranges

    def set_time_ranges(self, ranges):
        self.save_time_ranges(ranges)
