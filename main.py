from PySide6.QtWidgets import QApplication, QMessageBox, QLineEdit, QFileDialog, QKeySequenceEdit, QSystemTrayIcon, QMenu, QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QLabel, QSplitter, QTabWidget, QTableView, QHeaderView, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QResizeEvent, QStandardItemModel, QStandardItem, QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, QEvent
import sys, shutil, os, configparser, re, json, keyboard, time, ctypes

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
        return s != "" and ',' not in s and '+' not in s
        
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

def is_normal(c):
    return (is_number(c['wait'])
        and is_oneKey(c['left'])
        and is_oneKey(c['right'])
        and is_oneKey(c['up'])
        and is_oneKey(c['down']))
    
def is_temp(c):
    return (c['wait'] == '' 
            or c['left'] == ''
            or c['right'] == ''
            or c['up'] == ''
            or c['down'] == ''
            )
    
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 线程类
class Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        self.config = readConfig()
        key = [self.config['left'], self.config['right'], self.config['down'], self.config['up']]
        unkey = [self.config['right'], self.config['left'], self.config['up'], self.config['down']]
        last_key = [False, False, False, False]
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
            time.sleep(float(self.config['wait']))

    def stop(self):
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
        if is_admin():
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
        
        # 读取配置文件
        try:
            self.create_val(readConfig())
        except:
            self.reset_config()
            
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
        
        # 托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("ui\\icon.ico"))
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
        
        # warning 事件
        self.warning.sure.clicked.connect(self.warning_close)
        self.warning.reset.clicked.connect(self.reset_config)
            

    def toggle(self):
        if self.thread.isRunning():
            self.thread.stop()
            self.ui.start.setText("启用")
            self.start_action.setText("启用")
        else:
            self.create_val(readConfig())
            self.thread = Worker()
            self.thread.start()
            self.ui.start.setText("停用")
            self.start_action.setText("停用")
            
    def warning_close(self):
        self.warning.hide()
        self.ui.setDisabled(False)
    
    def reset_config(self):
        self.warning_close()
        self.config = {'wait' : 0.001, 'left' : 'a', 'right' : 'd', 'up' : 'w', 'down' :'s'}
        writeConfig(self.config)
        self.create_val(self.config)

    def saveConfig(self):
        self.config = {
            'wait': self.ui.wait.text(),
            'left': self.ui.left.keySequence().toString(),
            'right': self.ui.right.keySequence().toString(),
            'up': self.ui.up.keySequence().toString(),
            'down': self.ui.down.keySequence().toString()
        }
        if is_normal(self.config) and not is_temp(self.config):
            writeConfig(self.config)
            if self.thread.isRunning():
                self.thread.stop()
                self.thread.wait()
                self.thread = Worker()
                self.thread.start()
        elif not is_temp(self.config):
            self.ui.setDisabled(True)
            self.warning.show()
            self.create_val(readConfig())

        
    def create_val(self, config):
        self.ui.wait.setText(str(config['wait']))
        self.ui.left.setKeySequence(config['left'])
        self.ui.right.setKeySequence(config['right'])
        self.ui.up.setKeySequence(config['up'])
        self.ui.down.setKeySequence(config['down'])
        
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
    
    def closeEvent(self, event):
        self.warning.close()
        super().closeEvent(event)
        
    
            
# 启动程序
app = QApplication(sys.argv)
main_window = Main()
main_window.show()
sys.exit(app.exec())
