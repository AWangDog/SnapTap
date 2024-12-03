# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'warning.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(179, 99)
        main.setMinimumSize(QSize(179, 99))
        main.setMaximumSize(QSize(179, 99))
        self.gridLayout = QGridLayout(main)
        self.gridLayout.setObjectName(u"gridLayout")
        self.sure = QPushButton(main)
        self.sure.setObjectName(u"sure")

        self.gridLayout.addWidget(self.sure, 1, 0, 1, 1)

        self.reset = QPushButton(main)
        self.reset.setObjectName(u"reset")

        self.gridLayout.addWidget(self.reset, 1, 1, 1, 1)

        self.label = QLabel(main)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)


        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"\u8b66\u544a", None))
        self.sure.setText(QCoreApplication.translate("main", u"\u786e\u5b9a", None))
        self.reset.setText(QCoreApplication.translate("main", u"\u91cd\u7f6e\u6240\u6709\u8bbe\u7f6e", None))
        self.label.setText(QCoreApplication.translate("main", u"\u914d\u7f6e\u8f93\u5165\u6709\u8bef,\u8bf7\u68c0\u67e5: \n"
"\u54cd\u5e94\u65f6\u95f4\u8bf7\u8f93\u5165\u6570\u5b57;\n"
"\u5feb\u6377\u952e\u53ea\u652f\u6301\u5355\u952e;", None))
    # retranslateUi

