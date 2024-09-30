# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'homepage.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDockWidget,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QStackedWidget,
    QStatusBar, QTextBrowser, QTextEdit, QToolButton,
    QWidget)

class Ui_mw_home(object):
    def setupUi(self, mw_home):
        if not mw_home.objectName():
            mw_home.setObjectName(u"mw_home")
        mw_home.setEnabled(True)
        mw_home.resize(800, 600)
        self.actionclose = QAction(mw_home)
        self.actionclose.setObjectName(u"actionclose")
        self.centralwidget = QWidget(mw_home)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 10, 721, 541))
        self.homepage = QWidget()
        self.homepage.setObjectName(u"homepage")
        self.spend_label = QLabel(self.homepage)
        self.spend_label.setObjectName(u"spend_label")
        self.spend_label.setGeometry(QRect(340, 50, 81, 20))
        self.current_spend_goal = QProgressBar(self.homepage)
        self.current_spend_goal.setObjectName(u"current_spend_goal")
        self.current_spend_goal.setGeometry(QRect(320, 90, 118, 23))
        self.current_spend_goal.setValue(24)
        self.current_month_revenue = QLabel(self.homepage)
        self.current_month_revenue.setObjectName(u"current_month_revenue")
        self.current_month_revenue.setGeometry(QRect(100, 80, 141, 41))
        self.rev_title = QLabel(self.homepage)
        self.rev_title.setObjectName(u"rev_title")
        self.rev_title.setGeometry(QRect(90, 50, 151, 16))
        self.stackedWidget.addWidget(self.homepage)
        self.chatpage = QWidget()
        self.chatpage.setObjectName(u"chatpage")
        self.te_chathistory = QTextBrowser(self.chatpage)
        self.te_chathistory.setObjectName(u"te_chathistory")
        self.te_chathistory.setGeometry(QRect(0, 0, 731, 441))
        self.te_chatinput = QTextEdit(self.chatpage)
        self.te_chatinput.setObjectName(u"te_chatinput")
        self.te_chatinput.setGeometry(QRect(150, 450, 381, 81))
        self.bt_submitchat = QPushButton(self.chatpage)
        self.bt_submitchat.setObjectName(u"bt_submitchat")
        self.bt_submitchat.setGeometry(QRect(550, 450, 31, 71))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoUp))
        self.bt_submitchat.setIcon(icon)
        self.stackedWidget.addWidget(self.chatpage)
        self.brandperformance = QWidget()
        self.brandperformance.setObjectName(u"brandperformance")
        self.de_startdate = QDateEdit(self.brandperformance)
        self.de_startdate.setObjectName(u"de_startdate")
        self.de_startdate.setGeometry(QRect(40, 40, 110, 22))
        self.de_startdate.setCalendarPopup(True)
        self.de_enddate = QDateEdit(self.brandperformance)
        self.de_enddate.setObjectName(u"de_enddate")
        self.de_enddate.setGeometry(QRect(160, 40, 110, 22))
        self.de_enddate.setCalendarPopup(True)
        self.cb_brandfilter = QComboBox(self.brandperformance)
        self.cb_brandfilter.setObjectName(u"cb_brandfilter")
        self.cb_brandfilter.setGeometry(QRect(330, 40, 103, 32))
        self.lbl_datefilter = QLabel(self.brandperformance)
        self.lbl_datefilter.setObjectName(u"lbl_datefilter")
        self.lbl_datefilter.setGeometry(QRect(50, 10, 61, 16))
        self.lbl_brandfilter = QLabel(self.brandperformance)
        self.lbl_brandfilter.setObjectName(u"lbl_brandfilter")
        self.lbl_brandfilter.setGeometry(QRect(350, 20, 61, 16))
        self.stackedWidget.addWidget(self.brandperformance)
        mw_home.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mw_home)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(False)
        self.file = QMenu(self.menubar)
        self.file.setObjectName(u"file")
        self.file.setEnabled(True)
        mw_home.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mw_home)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setEnabled(False)
        self.statusbar.setSizeGripEnabled(False)
        mw_home.setStatusBar(self.statusbar)
        self.w_dock = QDockWidget(mw_home)
        self.w_dock.setObjectName(u"w_dock")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_dock.sizePolicy().hasHeightForWidth())
        self.w_dock.setSizePolicy(sizePolicy)
        self.w_dock.setMinimumSize(QSize(40, 38))
        font = QFont()
        font.setPointSize(9)
        self.w_dock.setFont(font)
        self.w_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.bt_home = QToolButton(self.dockWidgetContents)
        self.bt_home.setObjectName(u"bt_home")
        self.bt_home.setGeometry(QRect(10, 10, 31, 31))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoHome))
        self.bt_home.setIcon(icon1)
        self.bt_chat = QToolButton(self.dockWidgetContents)
        self.bt_chat.setObjectName(u"bt_chat")
        self.bt_chat.setGeometry(QRect(10, 60, 31, 31))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.WeatherStorm))
        self.bt_chat.setIcon(icon2)
        self.bt_brandperformance = QToolButton(self.dockWidgetContents)
        self.bt_brandperformance.setObjectName(u"bt_brandperformance")
        self.bt_brandperformance.setGeometry(QRect(10, 110, 31, 31))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailMarkImportant))
        self.bt_brandperformance.setIcon(icon3)
        self.bt_settings = QToolButton(self.dockWidgetContents)
        self.bt_settings.setObjectName(u"bt_settings")
        self.bt_settings.setGeometry(QRect(10, 490, 31, 31))
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.bt_settings.setIcon(icon4)
        self.w_dock.setWidget(self.dockWidgetContents)
        mw_home.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.w_dock)

        self.menubar.addAction(self.file.menuAction())
        self.file.addAction(self.actionclose)

        self.retranslateUi(mw_home)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mw_home)
    # setupUi

    def retranslateUi(self, mw_home):
        mw_home.setWindowTitle(QCoreApplication.translate("mw_home", u"MainWindow", None))
        self.actionclose.setText(QCoreApplication.translate("mw_home", u"close", None))
        self.spend_label.setText(QCoreApplication.translate("mw_home", u"spend goal", None))
        self.current_month_revenue.setText(QCoreApplication.translate("mw_home", u"TextLabel", None))
        self.rev_title.setText(QCoreApplication.translate("mw_home", u"Curent Monthly Revenue", None))
        self.bt_submitchat.setText("")
        self.lbl_datefilter.setText(QCoreApplication.translate("mw_home", u"date filter", None))
        self.lbl_brandfilter.setText(QCoreApplication.translate("mw_home", u"brand", None))
        self.file.setTitle(QCoreApplication.translate("mw_home", u"file", None))
        self.w_dock.setWindowTitle(QCoreApplication.translate("mw_home", u"podscale", None))
        self.bt_home.setText(QCoreApplication.translate("mw_home", u"...", None))
        self.bt_chat.setText(QCoreApplication.translate("mw_home", u"...", None))
        self.bt_brandperformance.setText(QCoreApplication.translate("mw_home", u"...", None))
        self.bt_settings.setText(QCoreApplication.translate("mw_home", u"...", None))
    # retranslateUi

