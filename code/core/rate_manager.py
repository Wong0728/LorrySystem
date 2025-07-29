import os
import pickle
import json
import random
import traceback
from datetime import datetime
from collections import defaultdict
from core.log import logger

class RateManager:
    def __init__(self):
        self.config_folder = "ConfigEngine"
        self.rate_folder = os.path.join(self.config_folder, "RateSettings")
        self.chain_folder = os.path.join(self.config_folder, "ChainSettings")
        self.pending_target = None  # 待触发的目标号码
        self.ensure_folders_exist()

    def ensure_folders_exist(self):
        os.makedirs(self.rate_folder, exist_ok=True)
        os.makedirs(self.chain_folder, exist_ok=True)

    def set_rate(self, mode, number, rate):
        try:
            rate_file = os.path.join(self.rate_folder, f"{number}.rate")
            data = {
                "mode": mode,
                "number": number,
                "rate": max(1, int(rate)),
                "count": 0,
                "last_draw": None
            }
            with open(rate_file, "wb") as f:
                pickle.dump(data, f)
            return True
        except Exception:
            return False

    def set_chain_rule(self, mode, trigger_number, target_number):
        try:
            chain_file = os.path.join(self.chain_folder, f"{trigger_number}.chain")
            data = {
                "mode": mode,
                "trigger": trigger_number,
                "target": target_number,
                "last_draw": None
            }
            with open(chain_file, "wb") as f:
                pickle.dump(data, f)
            return True
        except Exception:
            return False

    def check_chain(self, mode, drawn_numbers, available_numbers, gender_numbers=None):
        chain_files = [f for f in os.listdir(self.chain_folder) if f.endswith(".chain")]
        triggered = {}
        for filename in chain_files:
            try:
                with open(os.path.join(self.chain_folder, filename), "rb") as f:
                    data = pickle.load(f)
                    if (data["mode"] == mode and 
                        data["trigger"] in drawn_numbers and 
                        data["target"] in available_numbers):
                        if gender_numbers is None or data["target"] in gender_numbers:
                            triggered[data["trigger"]] = {
                                "target_number": data["target"],
                                "last_trigger_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "skip_count": True  # 标记为跳过计数
                            }
                            data["last_draw"] = datetime.now()
                            with open(os.path.join(self.chain_folder, filename), "wb") as f2:
                                pickle.dump(data, f2)
                            # 设置待触发的目标号码
                            self.pending_target = data["target"]
                            print(f"触发连锁规则: {data['trigger']} → {data['target']} (跳过计数)")
            except Exception as e:
                logger.log({
                    "error": "处理连锁文件失败",
                    "filename": filename,
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                })
                continue
        return triggered

    def check_rate(self, mode, available_numbers, gender_numbers=None):
        rate_files = [f for f in os.listdir(self.rate_folder) if f.endswith(".rate")]
        triggered_numbers = []
        rate_info = []
        normal_numbers = available_numbers.copy()
        
        # 处理爆率号码
        for filename in rate_files:
            try:
                with open(os.path.join(self.rate_folder, filename), "rb") as f:
                    data = pickle.load(f)
                    if data["mode"] == mode and data["number"] in available_numbers:
                        if gender_numbers is not None and data["number"] not in gender_numbers:
                            continue
                        
                        # 先检查是否是连锁号码
                        is_chain_target = False
                        if self.pending_target and data["number"] == self.pending_target:
                            is_chain_target = True
                            
                        # 更新计数 (连锁目标号码跳过计数)
                        new_count = data["count"] + (0 if is_chain_target else 1)
                        is_triggered = (new_count % data["rate"]) == 0
                        
                        # 立即保存更新后的计数
                        data["count"] = new_count
                        data["last_draw"] = datetime.now()
                        with open(os.path.join(self.rate_folder, filename), "wb") as f:
                            pickle.dump(data, f)
                        
                        print(f"Rate-controlled number {data['number']} count update: {new_count}/{data['rate']} {'(triggered)' if is_triggered else ''}")
                        
                        rate_info.append({
                            "number": data["number"],
                            "total_attempts": data["rate"],
                            "current_count": new_count,
                            "triggered": is_triggered
                        })
                        
                        if is_triggered:
                            triggered_numbers.append(data["number"])
                        else:
                            # 未触发时从普通号码中移除爆率号码
                            if data["number"] in normal_numbers:
                                normal_numbers.remove(data["number"])
            except Exception as e:
                logger.log({
                    "error": "处理爆率文件失败",
                    "filename": filename,
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                })
                continue
        
        # 抽号优先级: 待触发目标 > 爆率号码 > 普通号码
        if self.pending_target and self.pending_target in available_numbers:
            drawn_number = self.pending_target
            self.pending_target = None  # 清除待触发状态
            print(f"抽中连锁目标号码: {drawn_number}")
            
        elif triggered_numbers:
            drawn_number = random.choice(triggered_numbers)
            print(f"抽中爆率号码: {drawn_number}")
        else:
            drawn_number = random.choice(normal_numbers) if normal_numbers else random.choice(available_numbers)
            print(f"Randomly drawn number: {drawn_number}")
            
        chain_info = self.check_chain(mode, [drawn_number], available_numbers, gender_numbers)
        
        # 改进日志输出
        output = {
            "mode": mode,
            "drawn_number": drawn_number,
            "rate_info": [{
                "number": r["number"],
                "total_attempts": r["total_attempts"],
                "current_count": r["current_count"], 
                "triggered": r["triggered"]
            } for r in rate_info],
            "chain_info": {
                "trigger_status": "triggered" if chain_info else "not triggered",
                "trigger_condition": list(chain_info.keys())[0] if chain_info else None,
                "target_number": list(chain_info.values())[0]["target_number"] if chain_info else None
            } if chain_info else {
                "trigger_status": "not triggered",
                "trigger_condition": None,
                "target_number": None
            },
            "gender_restriction": "none" if gender_numbers is None else "enabled",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print("\n抽号系统日志:")
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
        return [drawn_number]

    def clear_rate_settings(self):
        """清空所有爆率设置"""
        try:
            for filename in os.listdir(self.rate_folder):
                if filename.endswith(".rate"):
                    os.remove(os.path.join(self.rate_folder, filename))
            return True
        except Exception as e:
            logger.log({
                "error": "清空爆率设置失败",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def clear_chain_settings(self):
        """清空所有连锁设置"""
        try:
            for filename in os.listdir(self.chain_folder):
                if filename.endswith(".chain"):
                    os.remove(os.path.join(self.chain_folder, filename))
            return True
        except Exception as e:
            logger.log({
                "error": "清空连锁设置失败",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def get_rate_settings(self):
        """获取所有爆率设置"""
        settings = []
        try:
            # 按模式分组存储
            mode_groups = defaultdict(list)
            
            for filename in os.listdir(self.rate_folder):
                if filename.endswith(".rate"):
                    with open(os.path.join(self.rate_folder, filename), "rb") as f:
                        data = pickle.load(f)
                        mode_groups[data["mode"]].append(
                            (data["number"], data["rate"], data["count"], data["last_draw"])
                        )
            
            # 转换为admin_panel.py期望的格式
            for mode, rules in mode_groups.items():
                settings.append({
                    "mode": mode,
                    "rules": rules
                })
        except Exception as e:
            logger.log({
                "error": "获取爆率设置失败",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
        return settings

    def get_chain_settings(self):
        """获取所有连锁设置"""
        settings = []
        try:
            # 按模式分组存储
            mode_groups = defaultdict(list)
            
            for filename in os.listdir(self.chain_folder):
                if filename.endswith(".chain"):
                    with open(os.path.join(self.chain_folder, filename), "rb") as f:
                        data = pickle.load(f)
                        mode_groups[data["mode"]].append(
                            (data["trigger"], data["target"], data["last_draw"])
                        )
            
            # 转换为admin_panel.py期望的格式
            for mode, rules in mode_groups.items():
                settings.append({
                    "mode": mode,
                    "rules": rules
                })
                
        except Exception as e:
            logger.log({
                "error": "获取连锁设置失败",
                "exception": str(e),
                "traceback": traceback.format_exc()
            })
        return settings
