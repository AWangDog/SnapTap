# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QKeySequenceEdit,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(280, 68)
        main.setMinimumSize(QSize(280, 68))
        main.setMaximumSize(QSize(583, 68))
        self.gridLayout = QGridLayout(main)
        self.gridLayout.setObjectName(u"gridLayout")
        self.right = QKeySequenceEdit(main)
        self.right.setObjectName(u"right")

        self.gridLayout.addWidget(self.right, 1, 3, 1, 1)

        self.up = QKeySequenceEdit(main)
        self.up.setObjectName(u"up")

        self.gridLayout.addWidget(self.up, 0, 2, 1, 1)

        self.start = QPushButton(main)
        self.start.setObjectName(u"start")

        self.gridLayout.addWidget(self.start, 0, 3, 1, 1)

        self.down = QKeySequenceEdit(main)
        self.down.setObjectName(u"down")

        self.gridLayout.addWidget(self.down, 1, 2, 1, 1)

        self.left = QKeySequenceEdit(main)
        self.left.setObjectName(u"left")

        self.gridLayout.addWidget(self.left, 1, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(main)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.wait = QLineEdit(main)
        self.wait.setObjectName(u"wait")

        self.horizontalLayout.addWidget(self.wait)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)


        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"SnapTap", None))
        self.start.setText(QCoreApplication.translate("main", u"\u542f\u7528", None))
        self.label.setText(QCoreApplication.translate("main", u"\u54cd\u5e94\u65f6\u95f4", None))
    # retranslateUi

