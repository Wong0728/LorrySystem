# LorrySystem
一个功能强大抽号软件（python）。


## 系统概述
视频：https://www.bilibili.com/video/BV1Wz89znEcU
可加我QQ讨论：3026688767


## 系统架构
```
抽号系统
├── main.py                # 主程序入口
├── config/                # 配置模块
│   ├── cipher.py          # 加密模块
│   ├── time_manager.py    # 时间管理
├── core/                  # 核心逻辑
│   ├── log.py             # 日志系统
│   ├── password_manager.py # 权限管理
│   ├── rate_manager.py    # 抽号频率控制
│   ├── record_manager.py  # 记录管理
├── ui/                    # 用户界面
│   ├── admin_panel.py     # 管理员面板
│   ├── import_panel.py    # 数据导入面板
│   ├── lottery_app.py     # 主应用程序
├── ConfigEngine/          # 数据存储
│   ├── LotteryRecords/    # 抽号记录
│   ├── RateSettings/      # 抽号频率设置
│   ├── StudentInfo/       # 学生信息
│   ├── TimeRestrictions/  # 时间限制
```

## 模块功能说明

### 1. 核心模块
- **main.py**: 程序入口，初始化GUI界面
- **config/cipher.py**: 提供简单加密/解密功能
- **config/time_manager.py**: 管理禁止抽号的时间段
- **core/log.py**: 日志
- **core/password_manager.py**: U盘权限验证
- **core/rate_manager.py**: 管理抽号频率和连锁规则
- **core/record_manager.py**: 管理抽号记录和学生信息

### 2. UI模块
- **ui/lottery_app.py**: 主应用程序界面
- **ui/admin_panel.py**: 管理员设置面板
- **ui/import_panel.py**: 数据导入面板

## 主要功能

### 1. 抽号功能
系统提供5种抽号模式：
- 模式一至模式五，每种模式的计数分开计算，确保在同一模式内抽到号码不重不漏。

【黑幕】抽号算法优先级：
1. 性别（若有）
2. 连锁规则
3. 爆率控制
4. 随机选择

### 2. 学生信息管理
- 学生名单存储在`ConfigEngine/StudentInfo/`目录
  - 男生名单：boys.txt (格式：学号 姓名)
  - 女生名单：girls.txt (格式：学号 姓名)
- 抽号显示方式：
  - 均为黑色学号
  - 姓名：黑色小号字体显示在学号下方，旁边有红/蓝色♂，♀

### 3. 抽号记录
- 所有抽号记录保存在`ConfigEngine/LotteryRecords/`目录
- 按模式分类存储为.txt文件
- 记录使用SimpleCipher加密

### 4. 抽号频率控制
- **爆率设置**：控制特定号码的抽中频率
- **连锁规则**：当特定号码被抽中时触发目标号码
- 设置存储在`ConfigEngine/RateSettings/`和`ConfigEngine/ChainSettings/`

### 5. 权限管理
- **管理员权限**：需要U盘根目录包含`permission\Administrator.txt`
- **普通用户权限**：需要U盘根目录包含`permission\User.txt`
- **权限功能**：
  - 管理员：所有功能
  - 普通用户：基本抽号功能

### 6. 数据导入
1. 插入管理员U盘
2. 选择导入模式
3. 拖放或选择TXT文件(每行一个数字)
4. 点击"处理文件"按钮完成导入

### 7. 时间限制
默认禁止时间段：
- 1:00-7:25
- 8:25-8:35  
- 9:20-9:40
- 10:20-11:30
- 11:10-11:20
- 11:10-17:20  
- 15:00-16:15
- 16:50-17:05
- 17:35-23:59
TimeRestrictions的加密密钥：lottery_system_secret_key

### 8. 日志
- 日志文件：`logs/system.log`

## 系统要求
- Python3
- 需要U盘权限验证
- 依赖库：tkinterdnd2, pywin32 

## 使用注意事项
1. 抽号前请确保学生名单已导入
2. 抽号记录不可手动修改
3. 注意时间限制规则
4. 爆率设置需谨慎使用

