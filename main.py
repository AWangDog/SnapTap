from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QSystemTrayIcon, QMenu, QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QLabel, QSplitter, QTabWidget, QTableView, QHeaderView, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QResizeEvent, QStandardItemModel, QStandardItem, QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, QEvent
import sys, shutil, os, configparser, re, json, keyboard, time

    # 读取配置文件
def readConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    wait = config['DEFAULT']['wait']
    left = config['DEFAULT']['left']
    right = config['DEFAULT']['right']
    up = config['DEFAULT']['up']
    down = config['DEFAULT']['down']
    return {'wait' : wait, 'left' : left, 'right' : right, 'up' : up, 'down' : down}

# 写入配置文件
def writeConfig(config):
    config_parser = configparser.ConfigParser()
    config_parser['DEFAULT'] = config
    with open('config.ini', 'w') as configfile:
        config_parser.write(configfile)
        
def is_oneKey(s):
    if len(s) == 1:
        return True
    else:
        if ',' in s:
            return False
        else:
            return True
        
def is_number(s):
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

# 线程类
class Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        config = readConfig()
        key = [config['left'], config['right'], config['down'], config['up']]
        unkey = [config['right'], config['left'], config['up'], config['down']]
        last_key = [False, False, False, False]
        
        if (is_number(config['wait'])
        and is_oneKey(config['left'])
        and is_oneKey(config['right'])
        and is_oneKey(config['up'])
        and is_oneKey(config['down'])
        ):
            while self._running:
                now = [keyboard.is_pressed(k) for k in key]
                pressing = [((not a) and b) for a, b in zip(last_key, now)]
                releaseing = [(a and (not b)) for a, b in zip(last_key, now)]
                for i in range(4):
                    if pressing[i] and keyboard.is_pressed(unkey[i]):
                        keyboard.release(unkey[i])
                    if releaseing[i] and keyboard.is_pressed(unkey[i]):
                        keyboard.press(unkey[i])
                last_key = [keyboard.is_pressed(k) for k in key]
                time.sleep(float(config['wait']))
        else:
            QMessageBox.warning(None, "错误", "配置有误，请检查输入！")

    def stop(self):
        self._running = False

# uiLoader 实例化
uiLoader = QUiLoader()
# 主窗口类
class Main(QMainWindow):
    def __init__(self):
        try:
            self.config = readConfig()
        except:
            self.config = {'wait' : 0.001, 'left' : 'a', 'right' : 'd', 'up' : 'w', 'down' :'s'}
            writeConfig(self.config)
        super().__init__()
        # 加载 ui 文件
        self.ui = QUiLoader().load('data\\ui\\main.ui')
        self.setCentralWidget(self.ui)
        self.setWindowTitle("SnapTap")
        self.setWindowIcon(QIcon("data\\ui\\icon.ico"))

        # 设置窗口大小
        self.setMaximumHeight(68)
        self.setMaximumWidth(583)
        self.setMinimumHeight(68)
        self.setMinimumWidth(280)

        # 文本填充
        self.create_val()
        
        self.ui.wait.textChanged.connect(self.saveConfig)
        self.ui.left.keySequenceChanged.connect(self.saveConfig)
        self.ui.right.keySequenceChanged.connect(self.saveConfig)
        self.ui.up.keySequenceChanged.connect(self.saveConfig)
        self.ui.down.keySequenceChanged.connect(self.saveConfig)

        # 按钮事件
        self.ui.start.clicked.connect(self.toggle)
        self.thread = Worker()
        
        # 托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("data\\ui\\icon.ico"))
        self.menu = QMenu()
        self.start_action = QAction("启用", self)
        self.show_action = QAction("隐藏", self)
        self.exit_action = QAction("退出", self)
        self.start_action.triggered.connect(self.toggle)
        self.show_action.triggered.connect(self.show_toggle)
        self.exit_action.triggered.connect(sys.exit)
        self.menu.addAction(self.start_action)
        self.menu.addAction(self.show_action)
        self.menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def toggle(self):
        if self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()  # 等待线程结束
            self.ui.start.setText("启用")
            self.start_action.setText("启用")
        else:
            self.thread = Worker()
            self.thread.start()
            self.ui.start.setText("停用")
            self.start_action.setText("停用")

    def saveConfig(self):
        if (
            is_number(self.ui.wait.text())
            and is_oneKey(self.ui.left.keySequence().toString())
            and is_oneKey(self.ui.right.keySequence().toString())
            and is_oneKey(self.ui.up.keySequence().toString())
            and is_oneKey(self.ui.down.keySequence().toString())
        ):
            self.config = {
                'wait': self.ui.wait.text(),
                'left': self.ui.left.keySequence().toString(),
                'right': self.ui.right.keySequence().toString(),
                'up': self.ui.up.keySequence().toString(),
                'down': self.ui.down.keySequence().toString()
            }
            writeConfig(self.config)
        else:
            QMessageBox.warning(self, "错误", "配置有误，请检查输入！")
            self.config = readConfig()
            self.create_val()
        
    def create_val(self):
        self.ui.wait.setText(str(self.config['wait']))
        self.ui.left.setKeySequence(self.config['left'])
        self.ui.right.setKeySequence(self.config['right'])
        self.ui.up.setKeySequence(self.config['up'])
        self.ui.down.setKeySequence(self.config['down'])
        
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_toggle()
                
    def show_toggle(self):
        if self.isVisible():
            self.hide()
            self.show_action.setText("显示")
        else:
            self.show()
            self.show_action.setText("隐藏")
            
# 启动程序
app = QApplication(sys.argv)
main_window = Main()
main_window.show()
sys.exit(app.exec())
# D:\Users\xujiy\AppData\Local\Programs\Python\Python312\Scripts\pyinstaller main.py --onefile --windowed --name SnapTap --icon=data/ui/icon.ico --hidden-import PySide6.QtXml
# D:\Users\xujiy\AppData\Local\Programs\Python\Python312\Scripts\pyinstaller SnapTap.spec
