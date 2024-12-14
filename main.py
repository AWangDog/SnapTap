from PySide6.QtWidgets import *
from PySide6.QtUiTools import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys, os, configparser, ctypes, pynput, WinKeyBoard, subprocess, signal, tempfile, psutil

version = "1.13"
title = 'SnapTap'

dir_path = os.getcwd() + '\\ui\\'
if os.path.exists(dir_path) and os.path.isdir(dir_path):
    pass
else:
    pids = []
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if process.info['name'] == 'SnapTap.exe':
                dir_path = f'{tempfile.gettempdir()}\\SnapTap_{process.info['pid']}\\ui\\'
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                   break
        except:
            pass

class check():
    """检查类函数
    """
    def is_config(self, config) -> bool:
        """检查Config

        Returns:
            bool: Config数据是否可用
        """
        for i in ['left', 'right', 'up', 'down', 'background', 'run']:
            if config.get(i, 'err') == 'err':
                return False
        for i in ['left', 'right', 'up', 'down']:
            if not self.is_int(config.get(i, False)):
                return False
        for i in ['background', 'run']:
            if not self.is_bool(config.get(i, False)):
                return False
        return True
    
    def is_work(self, config) -> bool:
        """检查是否属于work接受类型

        Returns:
            bool: Config数据是否可用
        """
        for i in ['left', 'right', 'up', 'down']:
            if config.get(i, 'err') == 'err':
                return False
        for i in ['left', 'right', 'up', 'down']:
            if not self.is_int(config.get(i, False)):
                return False
        return True
    
    def is_bool(self, s : str) -> bool:
        """布尔值检查

        Args:
            s (str): 输入布尔值

        Returns:
            bool: 是否是布尔值
        """
        if s == 'True' or s == 'False':
            return True
        return False
        
                
    def is_int(self, s : str) -> bool:
        """数字检查

        Args:
            s (str): 输入数字

        Returns:
            bool: 是否是纯整数
        """
        try:
            int(s)
            return True
        except ValueError:
            pass
        return False
        
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
        create_task_command = [
            'schtasks', '/query',
            '/tn', 'SnapTap'
        ]
        try:
            subprocess.run(create_task_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except subprocess.CalledProcessError as e:
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

class act_config():
    """配置文件类函数
    """
    def readConfig(self) -> dict:
        """读取配置文件

        Returns:
            dict: 配置参数字典
        """
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            return dict(config['DEFAULT'])
        except:
            print('配置文件读取失败')
            return {}

    def writeConfig(self, config : dict) -> None:
        """写入配置文件

        Args:
            config (dict): 配置参数字典
        """
        config_parser = configparser.ConfigParser()
        config_parser['DEFAULT'] = config
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)

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
        VK = WinKeyBoard.type_conversion.fromVK_CODE(key)
        WinKeyBoard.key_controller.PressKey(VK)
        self.liar_key = True

    def release_key(self, key):
        VK = WinKeyBoard.type_conversion.fromVK_CODE(key)
        WinKeyBoard.key_controller.ReleaseKey(VK)
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
        self.setting_ui = QUiLoader().load(f'{dir_path}setting.ui', self)
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
            if check().is_task_exists(title):
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
                
    def hideEvent(self, event):
        self.root.ui.setting.setDisabled(False)
        self.root.setting_action.setDisabled(False)
        super().hideEvent(event)
        
    def showEvent(self, event):
        self.root.ui.setting.setDisabled(True)
        self.root.setting_action.setDisabled(True)
        super().showEvent(event)

class KeyInputEdit(QLineEdit):
    def __init__(self, root):
        super().__init__()
        self.setReadOnly(True)
        self.root = root


    def keyPressEvent(self, event):
        event.ignore()
        self.keyCode = event.nativeVirtualKey()
        self.setText(VK_CODE_to_CHAR(self.keyCode))
        self.root.saveConfig()

    def getKeyCode(self):
        return int(self.keyCode)

    def event(self, event):
        if event.type() in [QEvent.ContextMenu, QEvent.InputMethodQuery]:
            event.ignore()
            return False
        super().event(event)
        return True

def VK_CODE_to_CHAR(VK_CODE): return WinKeyBoard.type_conversion.fromVK_CODE(VK_CODE).get_CHAR()

# uiLoader 实例化
uiLoader = QUiLoader()
# 主窗口类
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        # 检查多开状态
        share = QSharedMemory()
        share.setKey(title)
        if share.attach():
            QMessageBox.critical(self, "错误", "程序已经在运行\n请检查托盘图标")
            self.exit(1)
        
        if share.create(1):
            # 加载ui文件
            try:
                self.ui = QUiLoader().load(f'{dir_path}main.ui')
                self.setting = QUiLoader().load(f'{dir_path}Setting.ui')
                self.setting = Setting(self)
                self.tray_icon = QSystemTrayIcon(self)
                self.menu = QMenu()
            except Exception as e:
                QMessageBox.critical(self, "错误", "加载 ui 文件失败！\n请重装软件或检查ui是否存在！")
                self.exit(1)


            # 检查ui控件类型
            err = False
            try:
                if not (type(self.ui.start) == QPushButton
                and type(self.ui.left_layout) == QHBoxLayout
                and type(self.ui.right_layout) == QHBoxLayout
                and type(self.ui.up_layout) == QHBoxLayout
                and type(self.ui.down_layout) == QHBoxLayout
                and type(self.ui.setting) == QPushButton
                and type(self.setting.setting_ui.run_on_windows_startup) == QCheckBox
                and type(self.setting.setting_ui.background) == QCheckBox
                and type(self.setting.setting_ui.run) == QCheckBox
                ):
                    err = True
            except:
                err = True
            if err:
                QMessageBox.critical(self, "错误", "初始化失败！(ui文件损坏)\n请重装软件或检查ui文件！")
                self.exit(1)       

            # 初始化按键输入框
            self.ui.left = KeyInputEdit(self)
            self.ui.right = KeyInputEdit(self)
            self.ui.up = KeyInputEdit(self)
            self.ui.down = KeyInputEdit(self)

            # 初始化托盘图标菜单
            self.start_action = QAction("启用", self)
            self.show_action = QAction("显示", self)
            self.setting_action = QAction("设置", self)
            self.exit_action = QAction("退出", self)

            # 设置窗口图标
            try:
                self.setWindowIcon(QIcon(f'{dir_path}icon.ico'))
                self.setting.setWindowIcon(QIcon(f'{dir_path}setting.ico'))
                self.tray_icon.setIcon(QIcon(f'{dir_path}icon.ico'))
                self.start_action.setIcon(QIcon(f'{dir_path}off.ico'))
                self.show_action.setIcon(QIcon(f'{dir_path}hide.ico'))
                self.setting_action.setIcon(QIcon(f'{dir_path}setting.ico'))
                self.exit_action.setIcon(QIcon(f'{dir_path}exit.ico'))
            except:
                pass


            # 更改主窗口标题
            self.setCentralWidget(self.ui)
            if check().is_admin():
                title_main = f'{title} [管理员]'
            else:
                title_main = f'{title} [非管理员, 某些情况可能无法生效]'

            self.setWindowTitle(title_main)
            if check().is_task_exists(title):
                self.create_run_on_system_startup_task(os.path.abspath(sys.argv[0]))

            # 读取配置文件
            self.config = act_config().readConfig()
            if self.config == {} or not check().is_config(self.config):
                self.reset_config()
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
            
            
            # 初始化主函数
            self.main_worker = Worker()

            # setting 事件
            self.setting.setting_ui.run_on_windows_startup.stateChanged.connect(self.run_on_system_startup)
            self.setting.setting_ui.background.stateChanged.connect(self.save_setting)
            self.setting.setting_ui.run.stateChanged.connect(self.save_setting)
            
            
            # 托盘事件
            self.start_action.triggered.connect(self.toggle)
            self.show_action.triggered.connect(self.show_toggle)
            self.setting_action.triggered.connect(self.setting.toggle)
            self.exit_action.triggered.connect(self.exit)
            self.menu.addAction(self.start_action)
            self.menu.addAction(self.show_action)
            self.menu.addAction(self.setting_action)
            self.menu.addAction(self.exit_action)
            self.tray_icon.setContextMenu(self.menu)
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            self.tray_icon.setToolTip(title)
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
        title_ = ''
        if check().is_admin():
            title_ = f' [管理员]'
        if self.main_worker._running:
            self.main_worker.stop()
            self.ui.start.setText("启用")
            self.start_action.setText("启用")
            try:
                self.setWindowIcon(QIcon(f'{dir_path}icon.ico'))
                self.tray_icon.setIcon(QIcon(f'{dir_path}icon.ico'))
                self.start_action.setIcon(QIcon(f'{dir_path}off.ico'))
                self.tray_icon.setToolTip(title + title_)
            except:
                pass
        else:
            self.config = act_config().readConfig()
            self.write_val()
            if not check().is_config(self.config):
                self.reset_config()
            self.main_worker.run({'left': int(self.config['left']), 'right': int(self.config['right']), 'up': int(self.config['up']), 'down': int(self.config['down'])})
            self.ui.start.setText("停用")
            self.start_action.setText("停用")
            try:
                self.setWindowIcon(QIcon(f'{dir_path}running.ico'))
                self.tray_icon.setIcon(QIcon(f'{dir_path}running.ico'))
                self.start_action.setIcon(QIcon(f'{dir_path}on.ico'))
                self.tray_icon.setToolTip(f'''{title} 已启用{title_}''')# \n上: {VK_CODE_to_CHAR(int(self.config['up']))}; 左: {VK_CODE_to_CHAR(int(self.config['left']))}; 下: {VK_CODE_to_CHAR(int(self.config['down']))}\n右: {VK_CODE_to_CHAR(int(self.config['right']))}
            except:
                pass
                
    def show_toggle(self): # 切换主窗口显示与隐藏  
        """切换主窗口显示与隐藏
        """
        if self.isVisible():
            self.hide()
            self.setting.hide()
            self.show_action.setText("显示")
            try:
                self.show_action.setIcon(QIcon(f'{dir_path}show.ico'))
            except:
                pass
        else:
            self.show()
            self.show_action.setText("隐藏")
            self.setWindowState(Qt.WindowActive)
            self.raise_()
            self.activateWindow()
            try:
                self.show_action.setIcon(QIcon(f'{dir_path}hide.ico'))
            except:
                pass
              
    def on_tray_icon_activated(self, reason): # 左键单击托盘图标切换主窗口显示与隐藏
        """左键单击托盘图标切换主窗口显示与隐藏

        Args:
            reason (reason): 托盘图标操作状态
        """
        if reason == QSystemTrayIcon.Trigger:
            self.show_toggle()
    
    def reset_config(self): # 重置config.ini
        """重置config.ini
        """
        self.config = {'left' : '65', 'right' : '68', 'up' : '87', 'down' :'83', 'version' : version, 'run' : False, 'background' : False}
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
                if not check().is_config(self.config):
                    self.reset_config()
                self.main_worker.run({'left': int(self.config['left']), 'right': int(self.config['right']), 'up': int(self.config['up']), 'down': int(self.config['down'])})

            
    def clean_config(self, config : dict): # 清理无用配置
        """清理无用配置
        """
        config_ = {}
        waste = ['running', 'wait', 'left_name', 'right_name', 'up_name', 'down_name']
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
        self.ui.left.setText(VK_CODE_to_CHAR(int(self.config['left'])))
        self.ui.right.setText(VK_CODE_to_CHAR(int(self.config['right'])))
        self.ui.up.setText(VK_CODE_to_CHAR(int(self.config['up'])))
        self.ui.down.setText(VK_CODE_to_CHAR(int(self.config['down'])))
        pass
        
    def read_val(self) -> dict: # 从窗口控件读取配置参数字典
        """从窗口控件读取配置参数字典

        Returns:
            dict: 配置参数字典
        """
        return {
            'left': self.ui.left.getKeyCode(),
            'right': self.ui.right.getKeyCode(),
            'up': self.ui.up.getKeyCode(),
            'down': self.ui.down.getKeyCode(),
        }
    
    def create_run_on_system_startup_task(self, path): # 创建自启动任务
        """创建自启动任务

        Args:
            path (_type_): 程序路径
        """
        xml_content = rf'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
<RegistrationInfo>
    <Author>SnapTap</Author>
    <Description>SnapTap开机自启动</Description>
    <URI>\SnapTap</URI>
</RegistrationInfo>
<Triggers>
    <LogonTrigger>
    <Enabled>true</Enabled>
    </LogonTrigger>
</Triggers>
<Principals>
    <Principal id="Author">
    <LogonType>InteractiveToken</LogonType>
    <RunLevel>HighestAvailable</RunLevel>
    </Principal>
</Principals>
<Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
    <StopOnIdleEnd>true</StopOnIdleEnd>
    <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
</Settings>
<Actions Context="Author">
    <Exec>
    <Command>{path}</Command>
    <Arguments>--run --background</Arguments>
    <WorkingDirectory>{os.path.dirname(path)}</WorkingDirectory>
    </Exec>
</Actions>
</Task>
'''
        
        create_task_command = [
            'schtasks', '/create',
            '/tn', 'SnapTap',
            '/xml', "task.xml",
            '/f'
        ]
        try:
            subprocess.run(create_task_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            with open("task.xml", "w", encoding="utf-16") as xml_file:
                xml_file.write(xml_content)
            os.remove("task.xml")
        except:
            pass
        
    def run_on_system_startup(self): # 注册开机自启动
        """注册开机自启动
        """
        if self.setting.setting_ui.run_on_windows_startup.isChecked():
            self.create_run_on_system_startup_task(os.path.abspath(sys.argv[0]))
        else:
            create_task_command = [
                'schtasks', '/delete',
                '/tn', 'SnapTap',
                '/f'
            ]
            try:
                subprocess.run(create_task_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass

    def closeEvent(self, event): # 覆写窗口关闭逻辑
        """覆写窗口关闭逻辑

        Args:
            event (event): event
        """
        self.exit(2)
        super().closeEvent(event)
    
    def exit(self, event = 0): # 关闭程序前的动作
        """关闭程序前的动作
        """
        if event == 1:
            pid = os.getpid()
            os.kill(pid, signal.SIGTERM)
        if self.setting.isVisible():
            self.setting.close()
        if self.main_worker._running:
            self.main_worker.stop()
        self.saveConfig()
        if event == 0:
            pid = os.getpid()
            os.kill(pid, signal.SIGTERM)

if __name__ == '__main__':
    # 启动程序
    app = QApplication(sys.argv)
    main_window = Main()
