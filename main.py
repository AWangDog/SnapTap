from PySide6.QtWidgets import QApplication, QMessageBox, QLineEdit, QFileDialog, QDialog, QKeySequenceEdit, QCheckBox, QSystemTrayIcon, QMenu, QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QTabWidget, QTableView, QHeaderView, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QResizeEvent, QStandardItemModel, QStandardItem, QIcon, QAction, QKeySequence
from PySide6.QtCore import Qt, QThread, Signal, QEvent, QFile, QSharedMemory
import sys, shutil, os, configparser, re, json, keyboard, time, ctypes, pynput, win32com.client, subprocess, shlex, warnings, filelock

version = "1.10"

class act_config():
    """配置文件类函数
    """
    def readConfig(self) -> dict:
        """读取配置文件

        Returns:
            dict: 配置参数字典
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        return dict(config['DEFAULT'])

    def writeConfig(self, config : dict) -> None:
        """写入配置文件

        Args:
            config (dict): 配置参数字典
        """
        config_parser = configparser.ConfigParser()
        config_parser['DEFAULT'] = config
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)
    
class check():
    """检查类函数
    """
    def is_admin(self) -> bool:
        """管理员检查

        Returns:
            bool: 是否为管理员运行
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def is_filePath(self, path : str) -> bool:
        """文件检查

        Args:
            path (str): 文件路径

        Returns:
            bool: 文件是否存在
        """
        return os.path.exists(path)
    
    def args_check(self, args : list) -> list:
        """静默启动检查

        Args:
            args (list): 启动参数

        Returns:
            list: 包含的启动参数列表
        """
        args_list = []
        args_list_ = ['background', 'run']
        for arg in args:
            for arg_ in args_list_:
                if self.arg_check(arg, arg_):
                    args_list.append(arg_)
        return args_list
    
    def is_task_exists(self, task_name : str) -> bool:
        """检查任务

        Args:
            task_name (str): 任务名

        Returns:
            bool: 任务是否存在
        """
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        tasks = root_folder.GetTasks(0)
        for task in tasks:
            if task.Name == task_name:
                return True
        return False

    def arg_check(self, arg : str, arg_ : str) -> bool:
        """检查参数

        Args:
            arg (str): 传入参数
            arg_ (str): 参数名

        Returns:
            bool: 传入参数是否为参数名
        """
        return arg == f'--{arg_}' or arg == f'-{arg_}' or arg == f'/{arg_}' or arg == arg_

class Worker(QThread):
    """主要函数类

    Args:
        QThread (Qthread): QT多线程
    """
    def __init__(self):
        super().__init__()
        self._running = False

    def run(self, config):
        """主要实现逻辑函数
        """
        self._running = True
        self.config = config
        self.config = {'left': int(self.config['left']), 'right': int(self.config['right']), 'up': int(self.config['up']), 'down': int(self.config['down'])}
        self.last_key = [False, False, False, False]
        self.listen_key = [False, False, False, False]
        self.liar_key = False
        self.keyboard_controller = pynput.keyboard.Controller()
        self.key_bind = [self.config['left'], self.config['right'], self.config['up'], self.config['down']]
        self.unkey = [self.config['right'], self.config['left'], self.config['down'], self.config['up']]
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.listener = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.daemon = True
        self.listener.start()
    def on_press(self, key):
        if not self._running:
            return False
        if not self.liar_key:
            try:
                if self.to_vk(key) in self.key_bind:
                    for i, v in enumerate(self.key_bind):
                        if self.to_vk(key) == v:
                            self.listen_key[i] = True
                    self.pressing = [((not a) and b) for a, b in zip(self.last_key, self.listen_key)]
                    self.releaseing = [(a and (not b)) for a, b in zip(self.last_key, self.listen_key)]
                    for i in range(4):
                        if self.pressing[i] and [self.listen_key[1], self.listen_key[0], self.listen_key[3], self.listen_key[2]][i]:
                            self.release_key(self.unkey[i])
                        if self.releaseing[i] and [self.listen_key[1], self.listen_key[0], self.listen_key[3], self.listen_key[2]][i]:
                            self.press_key(self.unkey[i])
                    self.last_key = self.listen_key.copy()
            except AttributeError:
                pass
        else:
            self.liar_key = False
    
    def on_release(self, key):
        if not self._running:
            return False
        if not self.liar_key:
            try:
                if self.to_vk(key) in self.key_bind:
                    for i, v in enumerate(self.key_bind):
                        if self.to_vk(key) == v:
                            self.listen_key[i] = False
                    self.pressing = [((not a) and b) for a, b in zip(self.last_key, self.listen_key)]
                    self.releaseing = [(a and (not b)) for a, b in zip(self.last_key, self.listen_key)]
                    for i in range(4):
                        if self.pressing[i] and [self.listen_key[1], self.listen_key[0], self.listen_key[3], self.listen_key[2]][i]:
                            self.release_key(self.unkey[i])
                        if self.releaseing[i] and [self.listen_key[1], self.listen_key[0], self.listen_key[3], self.listen_key[2]][i]:
                            self.press_key(self.unkey[i])
                    self.last_key = self.listen_key.copy()
            except AttributeError:
                pass
        else:
            self.liar_key = False
        
    def press_key(self, key):
        self.keyboard_controller.press(self.from_vk(key))
        self.liar_key = True

    def release_key(self, key):
        self.keyboard_controller.release(self.from_vk(key))
        self.liar_key = True
    
    def to_vk(self, key):
        """按键转keycode

        Args:
            key (pynput.keyboard.KeyCode or other): 按键
        """
        if type(key) == pynput.keyboard.KeyCode:
            ascii_value = key.vk
            return(ascii_value)
        else:
            return(key.value.vk)
        
    def from_vk(self, vk):
        """keycode转按键

        Args:
            vk (int): keycode
        """
        keydict = {
            0x08 : pynput.keyboard.Key.backspace,
            0x09 : pynput.keyboard.Key.tab,
            0x0D : pynput.keyboard.Key.enter,
            0x10 : pynput.keyboard.Key.shift,
            0x11 : pynput.keyboard.Key.ctrl,
            0x12 : pynput.keyboard.Key.alt,
            0x13 : pynput.keyboard.Key.pause,
            0x14 : pynput.keyboard.Key.caps_lock,
            0x1B : pynput.keyboard.Key.esc,
            0x20 : pynput.keyboard.Key.space,
            0x21 : pynput.keyboard.Key.page_up,
            0x22 : pynput.keyboard.Key.page_down,
            0x23 : pynput.keyboard.Key.end,
            0x24 : pynput.keyboard.Key.home,
            0x25 : pynput.keyboard.Key.left,
            0x26 : pynput.keyboard.Key.up,
            0x27 : pynput.keyboard.Key.right,
            0x28 : pynput.keyboard.Key.down,
            0x2C : pynput.keyboard.Key.print_screen,
            0x2D : pynput.keyboard.Key.insert,
            0x2E : pynput.keyboard.Key.delete,
            0x5B : pynput.keyboard.Key.cmd_l,
            0x5C : pynput.keyboard.Key.cmd_r,
            0x5D : pynput.keyboard.Key.menu,
            0x70 : pynput.keyboard.Key.f1,
            0x71 : pynput.keyboard.Key.f2,
            0x72 : pynput.keyboard.Key.f3,
            0x73 : pynput.keyboard.Key.f4,
            0x74 : pynput.keyboard.Key.f5,
            0x75 : pynput.keyboard.Key.f6,
            0x76 : pynput.keyboard.Key.f7,
            0x77 : pynput.keyboard.Key.f8,
            0x78 : pynput.keyboard.Key.f9,
            0x79 : pynput.keyboard.Key.f10,
            0x7A : pynput.keyboard.Key.f11,
            0x7B : pynput.keyboard.Key.f12,
            0x7C : pynput.keyboard.Key.f13,
            0x7D : pynput.keyboard.Key.f14,
            0x7E : pynput.keyboard.Key.f15,
            0x7F : pynput.keyboard.Key.f16,
            0x80 : pynput.keyboard.Key.f17,
            0x81 : pynput.keyboard.Key.f18,
            0x82 : pynput.keyboard.Key.f19,
            0x83 : pynput.keyboard.Key.f20,
            0x84 : pynput.keyboard.Key.f21,
            0x85 : pynput.keyboard.Key.f22,
            0x86 : pynput.keyboard.Key.f23,
            0x87 : pynput.keyboard.Key.f24,
            0x90 : pynput.keyboard.Key.num_lock,
            0x91 : pynput.keyboard.Key.scroll_lock,
            0x90 : pynput.keyboard.Key.num_lock,
            0x97 : pynput.keyboard.Key.media_previous,
            0x98 : pynput.keyboard.Key.media_next,
            0x99 : pynput.keyboard.Key.media_play_pause,
            0x9B : pynput.keyboard.Key.media_volume_mute,
            0x9C : pynput.keyboard.Key.media_volume_down,
            0x9D : pynput.keyboard.Key.media_volume_up,
            0xA0 : pynput.keyboard.Key.shift_l,
            0xA1 : pynput.keyboard.Key.shift_r,
            0xA2 : pynput.keyboard.Key.ctrl_l,
            0xA3 : pynput.keyboard.Key.ctrl_r,
            0xA4 : pynput.keyboard.Key.alt_l,
            0xA5 : pynput.keyboard.Key.alt_r,
            0xAD : pynput.keyboard.Key.media_volume_mute,
            0xAE : pynput.keyboard.Key.media_volume_down,
            0xAF : pynput.keyboard.Key.media_volume_up,
            0xB0 : pynput.keyboard.Key.media_next,
            0xB1 : pynput.keyboard.Key.media_previous,
            0xB3 : pynput.keyboard.Key.media_play_pause
        }
        if vk in keydict:
            return keydict[vk]
        return pynput.keyboard.KeyCode.from_vk(vk)
            
    def stop(self):
        """主要函数多线程停止函数
        """
        self._running = False
        self.listener.stop()
        self.wait()


class Setting(QDialog):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.setting_ui = QUiLoader().load('ui\\setting.ui', self)
        self.setWindowTitle("设置")
        # 设置窗口大小
        self.setMaximumHeight(84)
        self.setMaximumWidth(115)
        self.setMinimumHeight(84)
        self.setMinimumWidth(115)

    def closeEvent(self, event):
        self.toggle()
        event.ignore()
    
    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            if check().is_task_exists('SnapTap'):
                self.setting_ui.run_on_windows_startup.setCheckState(Qt.Checked)
                self.root.create_run_on_system_startup_task(os.path.abspath(sys.argv[0]))
            else:
                self.setting_ui.run_on_windows_startup.setCheckState(Qt.Unchecked)
            if not check().is_admin():
                self.setting_ui.run_on_windows_startup.setDisabled(True)
                self.setting_ui.run_on_windows_startup.setText("开机自动运行(需要管理员权限)")
                self.setMaximumWidth(210)
                self.setMinimumWidth(210)
            config = act_config().readConfig()
            if config.get('background', False) == 'True':
                self.setting_ui.background.setCheckState(Qt.Checked)
            else:
                self.setting_ui.background.setCheckState(Qt.Unchecked)
            if config.get('run', False) == 'True':
                self.setting_ui.run.setCheckState(Qt.Checked)
            else:
                self.setting_ui.run.setCheckState(Qt.Unchecked)

class KeyInputEdit(QLineEdit):
    keyPressed = Signal(QKeySequence)
    
    def __init__(self, root):
        super().__init__()
        self.setReadOnly(True)
        self.root = root
        
    def keyPressEvent(self, event):
        event.ignore()
        self.key = event.key()
        self.keyCode = event.nativeVirtualKey()
        self.keyStr = QKeySequence(self.key).toString()
        self.setText(self.keyStr)
        self.root.saveConfig()
        
    def setTextOfKeyCode(self, keyCode):
        keyStr = QKeySequence(int(keyCode)).toString()
        self.setText(keyStr)
        
    def getKeyCode(self):
        return int(self.keyCode)
    
    def getKeyName(self):
        return self.keyStr
    
    def getKey(self):
        return self.key

# uiLoader 实例化
uiLoader = QUiLoader()
# 主窗口类
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        # 检查多开状态
        share = QSharedMemory()
        share.setKey("Snaptap")
        if share.attach():
            QMessageBox.critical(self, "错误", "程序已经在运行\n请检查托盘图标")
            sys.exit(3)
        
        if share.create(1):
            # 加载ui文件
            try:
                self.ui = QUiLoader().load('ui\\main.ui')
                self.warning = QUiLoader().load('ui\\warning.ui')
                self.setting = QUiLoader().load('ui\\Setting.ui')
                self.setting = Setting(self)
                self.tray_icon = QSystemTrayIcon(self)
                self.menu = QMenu()
            except:
                QMessageBox.critical(self, "错误", "加载 ui 文件失败！\n请重装软件或检查ui是否存在！")
                sys.exit(1)


            # 检查ui控件类型
            err = False
            try:
                if not (type(self.ui.start) == QPushButton
                and type(self.ui.left_layout) == QHBoxLayout
                and type(self.ui.right_layout) == QHBoxLayout
                and type(self.ui.up_layout) == QHBoxLayout
                and type(self.ui.down_layout) == QHBoxLayout
                and type(self.ui.setting) == QPushButton
                and type(self.warning.sure) == QPushButton
                and type(self.warning.reset) == QPushButton
                and type(self.setting.setting_ui.run_on_windows_startup) == QCheckBox
                and type(self.setting.setting_ui.background) == QCheckBox
                and type(self.setting.setting_ui.run) == QCheckBox
                ):
                    err = True
            except:
                err = True
            if err:
                QMessageBox.critical(self, "错误", "初始化失败！(ui文件损坏)\n请重装软件或检查ui文件！")
                sys.exit(2)        
                
            
            # 初始化按键输入框
            self.ui.left = KeyInputEdit(self)
            self.ui.right = KeyInputEdit(self)
            self.ui.up = KeyInputEdit(self)
            self.ui.down = KeyInputEdit(self)


            # 设置窗口图标
            try:
                self.setWindowIcon(QIcon("ui\\icon.ico"))
                self.warning.setWindowIcon(QIcon("ui\\warning.ico"))
                self.setting.setWindowIcon(QIcon("ui\\setting.ico"))
                self.tray_icon.setIcon(QIcon("ui\\icon.ico"))
            except:
                pass


            # 更改主窗口标题
            self.setCentralWidget(self.ui)
            if check().is_admin():
                self.setWindowTitle("SnapTap [管理员]")
                if check().is_task_exists('SnapTap'):
                    self.create_run_on_system_startup_task(os.path.abspath(sys.argv[0]))
            else:
                self.setWindowTitle("SnapTap [非管理员, 某些情况可能无法生效]")


            # 更改警告窗口标题与警告窗口属性
            self.warning.setWindowTitle("警告")
            self.warning.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMinMaxButtonsHint)

            
            # 读取配置文件
            self.config = act_config().readConfig()
            if self.config == {} or self.config.get('left_name', None) == None:
                self.reset_config()
                self.config = act_config().readConfig()
            self.write_val()
            if float(self.config.get('version', '0') != version):
                self.config['version'] = version
            self.config = self.clean_config(self.config)
            act_config().writeConfig(self.config)
            
                
            # 设置窗口大小
            self.setMaximumHeight(68)
            self.setMaximumWidth(583)
            self.setMinimumHeight(68)
            self.setMinimumWidth(280)


            # 设置主窗口事件
            self.ui.setting.clicked.connect(self.setting.toggle)
            self.ui.start.clicked.connect(self.toggle)
            self.ui.left_layout.addWidget(self.ui.left)
            self.ui.right_layout.addWidget(self.ui.right)
            self.ui.up_layout.addWidget(self.ui.up)
            self.ui.down_layout.addWidget(self.ui.down)
            self.ui.left.keyCode = self.config.get('left', 65)
            self.ui.right.keyCode = self.config.get('right', 68)
            self.ui.up.keyCode = self.config.get('up', 87)
            self.ui.down.keyCode = self.config.get('down', 83)
            self.ui.left.keyStr = self.config.get('left_name', 'A')
            self.ui.right.keyStr = self.config.get('right_name', 'D')
            self.ui.up.keyStr = self.config.get('up_name', 'W')
            self.ui.down.keyStr = self.config.get('down_name', 'S')
            
            
            # 初始化主函数
            self.main_worker = Worker()
            
            
            # warning 事件
            self.warning.sure.clicked.connect(self.warning_close)
            self.warning.reset.clicked.connect(self.reset_config)
            
            
            # setting 事件
            self.setting.setting_ui.run_on_windows_startup.stateChanged.connect(self.run_on_system_startup)
            self.setting.setting_ui.background.stateChanged.connect(self.save_setting)
            self.setting.setting_ui.run.stateChanged.connect(self.save_setting)
            
            
            # 托盘事件
            self.start_action = QAction("启用", self)
            self.show_action = QAction("显示", self)
            self.exit_action = QAction("退出", self)
            self.start_action.triggered.connect(self.toggle)
            self.show_action.triggered.connect(self.show_toggle)
            self.exit_action.triggered.connect(self.exit)
            self.menu.addAction(self.start_action)
            self.menu.addAction(self.show_action)
            self.menu.addAction(self.exit_action)
            self.tray_icon.setContextMenu(self.menu)
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            self.tray_icon.show()
            
            
            # 处理启动参数
            if 'run' in check().args_check(sys.argv):
                self.toggle()
            elif self.config.get('run', False) == 'True':
                self.toggle()
            else:
                if not self.config.get('run', False) == 'True':
                    self.config['run'] = False
            show = True
            if 'background' in check().args_check(sys.argv):
                show = False
            elif self.config.get('background', False) == 'True':
                show = False
            else:
                if not self.config.get('background', False) == 'True':
                    self.config['background'] = False
            if show:
                self.show_toggle()
            act_config().writeConfig(self.config)
            sys.exit(app.exec())


    def toggle(self): # 主函数启用/停用切换函数
        """主函数启用/停用切换函数
        """
        if self.main_worker._running:
            self.main_worker.stop()
            self.ui.start.setText("启用")
            self.start_action.setText("启用")
            try:
                self.setWindowIcon(QIcon("ui\\icon.ico"))
                self.tray_icon.setIcon(QIcon("ui\\icon.ico"))
            except:
                pass
        else:
            self.config = act_config().readConfig()
            self.write_val()
            self.main_worker.run(self.config)
            self.ui.start.setText("停用")
            self.start_action.setText("停用")
            try:
                self.setWindowIcon(QIcon("ui\\running.ico"))
                self.tray_icon.setIcon(QIcon("ui\\running.ico"))
            except:
                pass
                
    def show_toggle(self): # 切换主窗口显示与隐藏  
        """切换主窗口显示与隐藏
        """
        if self.isVisible():
            self.hide()
            self.setting.hide()
            self.show_action.setText("显示")
        else:
            self.show()
            self.show_action.setText("隐藏")
            self.setWindowState(Qt.WindowActive)
            self.raise_()
            self.activateWindow()
              
    def on_tray_icon_activated(self, reason): # 左键单击托盘图标切换主窗口显示与隐藏
        """左键单击托盘图标切换主窗口显示与隐藏

        Args:
            reason (reason): 托盘图标操作状态
        """
        if reason == QSystemTrayIcon.Trigger:
            self.show_toggle()
            
    def warning_close(self): # 警告窗口关闭
        """警告窗口关闭
        """
        self.warning.hide()
        self.ui.setDisabled(False)
        self.menu.setDisabled(False)
    
    def reset_config(self): # 重置config.ini
        """重置config.ini
        """
        self.warning_close()
        self.config = {'left' : '65', 'left_name' : 'A', 'right' : '68', 'right_name' : 'D', 'up' : '87', 'up_name' : 'W', 'down' :'83', 'down_name' :'S', 'version' : version, 'run' : False, 'background' : False}
        act_config().writeConfig(self.config)
        self.write_val()

    def saveConfig(self): # 保存config.ini
        """保存config.ini
        """
        for k, v in self.read_val().items():
            self.config[k] = v
            act_config().writeConfig(self.config)
            if self.main_worker._running:
                self.main_worker.stop()
                self.main_worker.run(self.config)
            
    def clean_config(self, config : dict): # 清理无用配置
        """清理无用配置
        """
        config_ = {}
        waste = ['running', 'wait']
        for k, v in config.items():
            if not k in waste:
                config_[k] = v
        return config_
            
    def save_setting(self): # 保存设置到config
        """保存设置到config
        """
        self.config = act_config().readConfig()
        self.config['background'] = str(self.setting.setting_ui.background.isChecked())
        self.config['run'] = str(self.setting.setting_ui.run.isChecked())
        act_config().writeConfig(self.config)

    def write_val(self): # 将配置参数字典写入窗口控件
        """将配置参数字典写入窗口控件
        """
        self.ui.left.setText(self.config['left_name'])
        self.ui.right.setText(self.config['right_name'])
        self.ui.up.setText(self.config['up_name'])
        self.ui.down.setText(self.config['down_name'])
        pass
        
    def read_val(self) -> dict: # 从窗口控件读取配置参数字典
        """从窗口控件读取配置参数字典

        Returns:
            dict: 配置参数字典
        """
        return {
            'left': self.ui.left.getKeyCode(),
            'left_name': self.ui.left.getKeyName(),
            'right': self.ui.right.getKeyCode(),
            'right_name': self.ui.right.getKeyName(),
            'up': self.ui.up.getKeyCode(),
            'up_name': self.ui.up.getKeyName(),
            'down': self.ui.down.getKeyCode(),
            'down_name': self.ui.down.getKeyName()
        }
            
    def create_run_on_system_startup_task(self, path): # 创建自启动任务
        """创建自启动任务

        Args:
            path (_type_): 程序路径
        """
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.NewTask(0)
            task.RegistrationInfo.Description = 'Snaptap开机自启动'
            task.RegistrationInfo.Author = "SnapTap"
            task.Principal.LogonType = 3
            task.Principal.RunLevel = 1
            trigger = task.Triggers.Create(9)
            trigger.Enabled = True
            exec_command = task.Actions.Create(0)
            exec_command.Path = path
            exec_command.Arguments = '--run --background'
            exec_command.WorkingDirectory = os.path.dirname(path)
            task.Settings.DisallowStartIfOnBatteries = False
            task.Settings.StopIfGoingOnBatteries = True
            task.Settings.AllowHardTerminate = True
            task.Settings.StartWhenAvailable = False
            task.Settings.Enabled = True
            task.Settings.Hidden = False
            task.Settings.ExecutionTimeLimit = 'PT0S'
            task.Settings.Priority = 7
            scheduler.GetFolder('\\').RegisterTaskDefinition('\\SnapTap',task,6,None,None,3,None)
        except:
            pass
        
    def run_on_system_startup(self): # 注册开机自启动
        """注册开机自启动
        """
        if self.setting.setting_ui.run_on_windows_startup.isChecked():
            self.create_run_on_system_startup_task(os.path.abspath(sys.argv[0]))
        else:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            scheduler.GetFolder('\\').DeleteTask('SnapTap', 0)

    def closeEvent(self, event): # 覆写窗口关闭逻辑
        """覆写窗口关闭逻辑

        Args:
            event (event): event
        """
        self.exit(1)
        super().closeEvent(event)
    
    def exit(self, event = 0): # 关闭程序前的动作
        """关闭程序前的动作
        """
        self.warning.close()
        self.setting.setting_ui.close()
        if self.main_worker._running:
            self.main_worker.stop()
        self.saveConfig()
        if event == 0:
            sys.exit()

if __name__ == '__main__':
    # 启动程序
    app = QApplication(sys.argv)
    main_window = Main()
