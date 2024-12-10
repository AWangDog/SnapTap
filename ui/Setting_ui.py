# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Setting.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QSizePolicy,
    QWidget)

class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(355, 84)
        self.gridLayout = QGridLayout(main)
        self.gridLayout.setObjectName(u"gridLayout")
        self.run = QCheckBox(main)
        self.run.setObjectName(u"run")

        self.gridLayout.addWidget(self.run, 3, 0, 1, 1)

        self.background = QCheckBox(main)
        self.background.setObjectName(u"background")

        self.gridLayout.addWidget(self.background, 2, 0, 1, 1)

        self.run_on_windows_startup = QCheckBox(main)
        self.run_on_windows_startup.setObjectName(u"run_on_windows_startup")

        self.gridLayout.addWidget(self.run_on_windows_startup, 1, 0, 1, 2)


        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"\u8bbe\u7f6e", None))
        self.run.setText(QCoreApplication.translate("main", u"\u542f\u52a8\u81ea\u52a8\u542f\u7528", None))
        self.background.setText(QCoreApplication.translate("main", u"\u9759\u9ed8\u542f\u52a8", None))
        self.run_on_windows_startup.setText(QCoreApplication.translate("main", u"\u5f00\u673a\u81ea\u52a8\u8fd0\u884c", None))
    # retranslateUi

