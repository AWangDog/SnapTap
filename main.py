# python -m nuitka --standalone --windows-console-mode=disable --mingw64 --output-dir=out --enable-plugin=pyside6 --windows-product-version=1.1 --remove-output --product-name=BRTools --file-description=BRTools --output-filename=BRTools --windows-icon-from-ico=bin\icon.ico main.py
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPalette, QColor, QIcon
import sys


# 自定义 QMainWindow 子类
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.ui = uiLoader.load('bin\\main.ui')
        self.setCentralWidget(self.ui)
        self.setWindowTitle("BR Tools - v1.1")
        self.setWindowIcon(QIcon("bin\\icon.ico"))
        self.ui.ChoiceNowAmmo.valueChanged.connect(self.set_now_ammo)
        self.ammo = [[self.ui.LabelFirstAmmo, self.ui.FirstAmmo],
                     [self.ui.LabelSecondAmmo, self.ui.SecondAmmo],
                     [self.ui.LabelThirdAmmo, self.ui.ThirdAmmo],
                     [self.ui.LabelFourthAmmo, self.ui.FourthAmmo],
                     [self.ui.LabelFifthAmmo, self.ui.FifthAmmo],
                     [self.ui.LabelSixthAmmo, self.ui.SixthAmmo],
                     [self.ui.LabelSeventhAmmo, self.ui.SeventhAmmo],
                     [self.ui.LabelEighthAmmo, self.ui.EighthAmmo]]
        self.ui.ChoiceTrueAmmo.valueChanged.connect(self.com_all_ammo)
        self.ui.ChoiceFalseAmmo.valueChanged.connect(self.com_all_ammo)
        self.ui.Reset.clicked.connect(self.reset)
        for i,j in enumerate(self.ammo):
            j[1].currentTextChanged.connect(self.com_last_ammo)
        self.reset()
        
    def set_now_ammo(self):
        palette = QPalette()
        now_ammo = self.ui.ChoiceNowAmmo.value()
        self.ui.LabelNowAmmo.setText(f"当前第{str(now_ammo)}发：")
        for i,j in enumerate(self.ammo):
            j[0].setPalette(QPalette())
        for i,j in enumerate(self.ammo[:now_ammo]):
            palette.setColor(QPalette.ColorRole.WindowText, QColor('gray'))
            j[0].setPalette(palette)
            
    def com_all_ammo(self):
        all_ammo = int(self.ui.ChoiceTrueAmmo.value()) + int(self.ui.ChoiceFalseAmmo.value())
        for i,j in enumerate(self.ammo):
            j[1].setCurrentText("无")
        for i,j in enumerate(self.ammo[:all_ammo]):
            j[1].setCurrentText("未知")
        
    def com_ammo(self):
        for i,j in enumerate(self.ammo):
            if j[1].currentText() == "无":
                j[1].setStyleSheet("QComboBox { color: gray; }")
            elif j[1].currentText() == "未知":
                j[1].setStyleSheet("")
            elif j[1].currentText() == "实弹":
                j[1].setStyleSheet("QComboBox { color: red; }")
            elif j[1].currentText() == "空弹":
                j[1].setStyleSheet("QComboBox { color: green; }")
        self.ui.LabelComAmmo.setText(f"剩余未知实弹{self.true_ammo - self.now_true_ammo}发，空弹{self.false_ammo - self.now_false_ammo}发")
    
    def com_last_ammo(self):
        self.true_ammo = int(self.ui.ChoiceTrueAmmo.value())
        self.false_ammo = int(self.ui.ChoiceFalseAmmo.value())
        self.now_true_ammo = 0
        self.now_false_ammo = 0
        for i,j in enumerate(self.ammo):
            if j[1].currentText() == "实弹":
                self.now_true_ammo += 1
            elif j[1].currentText() == "空弹":
                self.now_false_ammo += 1
        if self.true_ammo - self.now_true_ammo == 0 and self.false_ammo - self.now_false_ammo >= 1:
            for i,j in enumerate(self.ammo):
                if j[1].currentText() == "未知":
                    j[1].setCurrentText("空弹")
        elif self.true_ammo - self.now_true_ammo >= 1 and self.false_ammo - self.now_false_ammo == 0:
            for i,j in enumerate(self.ammo):
                if j[1].currentText() == "未知":
                    j[1].setCurrentText("实弹")
        self.com_ammo()
    
    def reset(self):
        self.ui.ChoiceNowAmmo.setValue(0)
        self.ui.ChoiceTrueAmmo.setValue(0)
        self.ui.ChoiceFalseAmmo.setValue(0)
        self.set_now_ammo()
        self.com_all_ammo()
        self.com_last_ammo()

# 启动程序
app = QApplication(sys.argv)
uiLoader = QUiLoader()
main_window = MyMainWindow()
main_window.show()
sys.exit(app.exec())