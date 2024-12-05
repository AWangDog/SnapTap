from PySide6.QtWidgets import QApplication, QMessageBox, QLineEdit, QFileDialog, QKeySequenceEdit, QSystemTrayIcon, QMenu, QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QLabel, QSplitter, QTabWidget, QTableView, QHeaderView, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QResizeEvent, QStandardItemModel, QStandardItem, QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, QEvent
import sys, shutil, os, configparser, re, json, keyboard, time, ctypes, pynput

version = "1.4"

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
    def is_oneKey(self, s : str) -> bool:
        """按键检查

        Args:
            s (str): 输入按键

        Returns:
            bool: 是否为纯字母
        """
        if len(s) == 1:
            if s.isalpha():
                return True
        else:
            return False
            
    def is_number(self, s : str) -> bool:
        """数字检查

        Args:
            s (str): 输入数字

        Returns:
            bool: 是否是纯数字
        """
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def is_normal(self, c : dict) -> bool:
        """配置类型检查

        Args:
            c (dict): 配置参数字典

        Returns:
            bool: 是否为可接受类型
        """
        return (self.is_number(c['wait'])
            and self.is_oneKey(c['left'])
            and self.is_oneKey(c['right'])
            and self.is_oneKey(c['up'])
            and self.is_oneKey(c['down']))
        
    def is_temp(self, c : dict) -> bool:
        """临时值检查

        Args:
            c (dict): 配置参数字典

        Returns:
            bool: 是否为临时状态
        """
        return (c['wait'] == '' 
                or c['left'] == ''
                or c['right'] == ''
                or c['up'] == ''
                or c['down'] == ''
                )
        
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


    
class Worker(QThread):
    """主要函数类

    Args:
        QThread (Qthread): QT多线程
    """
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        """主要实现逻辑函数
        """
        self.config = act_config().readConfig()
        self.config = {'left': self.VkKeyScanExA(self.config['left']), 'right': self.VkKeyScanExA(self.config['right']), 'up': self.VkKeyScanExA(self.config['up']), 'down': self.VkKeyScanExA(self.config['down'])}
        self.last_key = [False, False, False, False]
        self.listen_key = [False, False, False, False]
        self.liar_key = False
        self.keyboard_controller = pynput.keyboard.Controller()
        self.key_bind = [self.config['left'], self.config['right'], self.config['up'], self.config['down']]
        self.unkey = [self.config['right'], self.config['left'], self.config['down'], self.config['up']]
        with pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
            
    def VkKeyScanExA(self, character, hwnd=None):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.VkKeyScanExA.argtypes = [ctypes.wintypes.CHAR, ctypes.wintypes.HWND]
        user32.VkKeyScanExA.restype = ctypes.wintypes.BYTE
        try:
            if hwnd is None:
                hwnd = 0
            result = user32.VkKeyScanExA(ctypes.c_char(character.encode('ascii')), hwnd)
            return result
        except:
            return character
    
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
        self.keyboard_controller.press(pynput.keyboard.KeyCode.from_vk(key))
        self.liar_key = True

    def release_key(self, key):
        self.keyboard_controller.release(pynput.keyboard.KeyCode.from_vk(key))
        self.liar_key = True
    
    def to_vk(self, key):
        if type(key) == pynput.keyboard.KeyCode:
            ascii_value = key.vk
            return(ascii_value)
        else:
            return(key)
            
    def stop(self):
        """主要函数多线程停止函数
        """
        self._running = False
        


# uiLoader 实例化
uiLoader = QUiLoader()
# 主窗口类
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        # 加载 ui 文件
        try:
            self.ui = QUiLoader().load('ui\\main.ui')
            self.warning = QUiLoader().load('ui\\warning.ui')
        except:
            QMessageBox.critical(self, "错误", "加载 ui 文件失败！\n请重装软件或检查ui是否存在！")
            sys.exit(1)

        err = False
        try:
            if not (type(self.ui.wait) == QLineEdit
            and type(self.ui.left) == QKeySequenceEdit
            and type(self.ui.right) == QKeySequenceEdit
            and type(self.ui.up) == QKeySequenceEdit
            and type(self.ui.down) == QKeySequenceEdit
            and type(self.ui.start) == QPushButton
            and type(self.warning.sure) == QPushButton
            and type(self.warning.reset) == QPushButton
            and type(self.warning.label) == QLabel
            and type(self.ui.label) == QLabel
            ):
                err = True
        except:
            err = True
        if err:
            QMessageBox.critical(self, "错误", "初始化失败！(ui文件损坏)\n请重装软件或检查ui文件！")
            sys.exit(1)

        self.setCentralWidget(self.ui)
        if check().is_admin():
            self.setWindowTitle("SnapTap [管理员]")
        else:
            self.setWindowTitle("SnapTap [非管理员, 某些情况可能无法生效]")

        self.warning.setWindowTitle("警告")
        self.warning.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMinMaxButtonsHint)
        
        try:
            self.setWindowIcon(QIcon("ui\\icon.ico"))
            self.warning.setWindowIcon(QIcon("ui\\warning.ico"))
        except:
            pass
        
        # 托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("ui\\icon.ico"))
        self.menu = QMenu()
        self.start_action = QAction("启用", self)
        self.show_action = QAction("隐藏", self)
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
        
        # 读取配置文件
        self.config = act_config().readConfig()
        if self.config == {}:
            self.reset_config()
            self.config = act_config().readConfig()
        self.write_val(self.config)
        if float(self.config.get('version', '0') != version):
            self.config['version'] = version
        act_config().writeConfig(self.config)
        if self.config.get('running', '0') == '0':
            self.config['running'] = '1'
        act_config().writeConfig(self.config)
            
        # 设置窗口大小
        self.setMaximumHeight(68)
        self.setMaximumWidth(583)
        self.setMinimumHeight(68)
        self.setMinimumWidth(280)

        # 设置事件
        self.ui.wait.textChanged.connect(self.saveConfig)
        self.ui.left.keySequenceChanged.connect(self.saveConfig)
        self.ui.right.keySequenceChanged.connect(self.saveConfig)
        self.ui.up.keySequenceChanged.connect(self.saveConfig)
        self.ui.down.keySequenceChanged.connect(self.saveConfig)

        # 按钮事件
        self.ui.start.clicked.connect(self.toggle)
        self.thread = Worker()
        
        # warning 事件
        self.warning.sure.clicked.connect(self.warning_close)
        self.warning.reset.clicked.connect(self.reset_config)

    def toggle(self):
        if self.thread.isRunning():
            self.thread.stop()
            self.ui.start.setText("启用")
            self.start_action.setText("启用")
            try:
                self.setWindowIcon(QIcon("ui\\icon.ico"))
                self.tray_icon.setIcon(QIcon("ui\\icon.ico"))
            except:
                pass
        else:
            self.write_val(act_config().readConfig())
            self.thread = Worker()
            self.thread.start()
            self.ui.start.setText("停用")
            self.start_action.setText("停用")
            try:
                self.setWindowIcon(QIcon("ui\\running.ico"))
                self.tray_icon.setIcon(QIcon("ui\\running.ico"))
            except:
                pass
            
    def warning_close(self):
        self.warning.hide()
        self.ui.setDisabled(False)
        self.menu.setDisabled(False)
    
    def reset_config(self):
        self.warning_close()
        self.config = {'wait' : 0.1, 'left' : 'a', 'right' : 'd', 'up' : 'w', 'down' :'s', 'version' : version, 'running' : '1'}
        act_config().writeConfig(self.config)
        self.write_val(self.config)

    def saveConfig(self):
        for k, v in self.read_val().items():
            self.config[k] = v
        if check().is_normal(self.config) and not check().is_temp(self.config):
            act_config().writeConfig(self.config)
            if self.thread.isRunning():
                self.thread.stop()
                self.thread = Worker()
                self.thread.start()
        elif not check().is_temp(self.config):
            self.ui.setDisabled(True)
            self.menu.setDisabled(True)
            self.warning.show()
            self.write_val(act_config().readConfig())

        
    def write_val(self, config : dict):
        """将配置参数字典写入窗口控件

        Args:
            config (dict): 配置参数字典
        """
        self.ui.wait.setText(str(config['wait']))
        self.ui.left.setKeySequence(config['left'])
        self.ui.right.setKeySequence(config['right'])
        self.ui.up.setKeySequence(config['up'])
        self.ui.down.setKeySequence(config['down'])
        
    def read_val(self) -> dict:
        """从窗口控件读取配置参数字典

        Returns:
            dict: 配置参数字典
        """
        return {
            'wait': self.ui.wait.text(),
            'left': self.ui.left.keySequence().toString(),
            'right': self.ui.right.keySequence().toString(),
            'up': self.ui.up.keySequence().toString(),
            'down': self.ui.down.keySequence().toString()
        }
        
    def on_tray_icon_activated(self, reason):
        """左键单击托盘图标切换主窗口显示与隐藏

        Args:
            reason (reason): 托盘图标操作状态
        """
        if reason == QSystemTrayIcon.Trigger:
            self.show_toggle()
                
    def show_toggle(self):
        """切换主窗口显示与隐藏
        """
        if self.isVisible():
            self.hide()
            self.show_action.setText("显示")
        else:
            self.show()
            self.show_action.setText("隐藏")
    
    def closeEvent(self, event):
        """覆写窗口关闭逻辑

        Args:
            event (event): event
        """
        self.exit(1)
        super().closeEvent(event)
    
    def exit(self, event = 0):
        """关闭程序前的动作
        """
        self.warning.close()
        self.thread.stop()
        self.config['running'] = 0
        self.saveConfig()
        if event == 0:
            sys.exit()
        
    
            
# 启动程序
app = QApplication(sys.argv)
main_window = Main()
main_window.show()
sys.exit(app.exec())
