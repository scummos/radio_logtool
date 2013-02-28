# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Sun Jul 22 16:59:10 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(880, 804)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.window_splitter = QtGui.QSplitter(self.centralwidget)
        self.window_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.window_splitter.setObjectName(_fromUtf8("window_splitter"))
        self.plot_splitter = QtGui.QSplitter(self.window_splitter)
        self.plot_splitter.setOrientation(QtCore.Qt.Vertical)
        self.plot_splitter.setObjectName(_fromUtf8("plot_splitter"))
        self.plot_sum = KPlotWidget(self.plot_splitter)
        self.plot_sum.setProperty("backgroundColor", QtGui.QColor(45, 45, 45))
        self.plot_sum.setProperty("foregroundColor", QtGui.QColor(199, 199, 199))
        self.plot_sum.setProperty("gridColor", QtGui.QColor(121, 121, 124))
        self.plot_sum.setProperty("grid", True)
        self.plot_sum.setObjectName(_fromUtf8("plot_sum"))
        self.verticalLayoutWidget = QtGui.QWidget(self.window_splitter)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.mode_group = QtGui.QGroupBox(self.verticalLayoutWidget)
        self.mode_group.setMinimumSize(QtCore.QSize(0, 0))
        self.mode_group.setStyleSheet(_fromUtf8(" QGroupBox {\n"
"     border-top: 1px solid black;\n"
"     border-bottom: 1px solid black;\n"
"     margin-top: 1ex;\n"
" }\n"
"\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }"))
        self.mode_group.setFlat(False)
        self.mode_group.setCheckable(True)
        self.mode_group.setObjectName(_fromUtf8("mode_group"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.mode_group)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mode_interval = QtGui.QRadioButton(self.mode_group)
        self.mode_interval.setEnabled(False)
        self.mode_interval.setChecked(False)
        self.mode_interval.setObjectName(_fromUtf8("mode_interval"))
        self.verticalLayout_2.addWidget(self.mode_interval)
        self.mode_gradient = QtGui.QRadioButton(self.mode_group)
        self.mode_gradient.setChecked(True)
        self.mode_gradient.setObjectName(_fromUtf8("mode_gradient"))
        self.verticalLayout_2.addWidget(self.mode_gradient)
        self.invertSignalCheckbox = QtGui.QCheckBox(self.mode_group)
        self.invertSignalCheckbox.setChecked(True)
        self.invertSignalCheckbox.setObjectName(_fromUtf8("invertSignalCheckbox"))
        self.verticalLayout_2.addWidget(self.invertSignalCheckbox)
        self.verticalLayout_3.addWidget(self.mode_group)
        self.gradientSettings_group = QtGui.QGroupBox(self.verticalLayoutWidget)
        self.gradientSettings_group.setEnabled(True)
        self.gradientSettings_group.setStyleSheet(_fromUtf8(" QGroupBox {\n"
"     border-top: 1px solid black;\n"
"     border-bottom: 1px solid black;\n"
"     margin-top: 1ex;\n"
" }\n"
"\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }"))
        self.gradientSettings_group.setCheckable(True)
        self.gradientSettings_group.setObjectName(_fromUtf8("gradientSettings_group"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.gradientSettings_group)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self._integration_g = QtGui.QLabel(self.gradientSettings_group)
        self._integration_g.setObjectName(_fromUtf8("_integration_g"))
        self.horizontalLayout_5.addWidget(self._integration_g)
        self.gradientSettings_integrate = QtGui.QLineEdit(self.gradientSettings_group)
        self.gradientSettings_integrate.setObjectName(_fromUtf8("gradientSettings_integrate"))
        self.horizontalLayout_5.addWidget(self.gradientSettings_integrate)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.verticalLayout_3.addWidget(self.gradientSettings_group)
        self.limits_box = QtGui.QGroupBox(self.verticalLayoutWidget)
        self.limits_box.setStyleSheet(_fromUtf8(" QGroupBox {\n"
"     border-top: 1px solid black;\n"
"     border-bottom: 1px solid black;\n"
"     margin-top: 1ex;\n"
" }\n"
"\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }"))
        self.limits_box.setCheckable(False)
        self.limits_box.setObjectName(_fromUtf8("limits_box"))
        self.gridLayout = QtGui.QGridLayout(self.limits_box)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.limits_label_x = QtGui.QLabel(self.limits_box)
        self.limits_label_x.setObjectName(_fromUtf8("limits_label_x"))
        self.gridLayout.addWidget(self.limits_label_x, 3, 0, 1, 1)
        self.limits_autoFromIntegrated = QtGui.QRadioButton(self.limits_box)
        self.limits_autoFromIntegrated.setObjectName(_fromUtf8("limits_autoFromIntegrated"))
        self.gridLayout.addWidget(self.limits_autoFromIntegrated, 1, 1, 1, 1)
        self.limits_slider_x = QtGui.QSlider(self.limits_box)
        self.limits_slider_x.setSingleStep(10)
        self.limits_slider_x.setPageStep(5000)
        self.limits_slider_x.setOrientation(QtCore.Qt.Horizontal)
        self.limits_slider_x.setInvertedAppearance(False)
        self.limits_slider_x.setInvertedControls(False)
        self.limits_slider_x.setObjectName(_fromUtf8("limits_slider_x"))
        self.gridLayout.addWidget(self.limits_slider_x, 3, 1, 1, 1)
        self.limits_slider_y = QtGui.QSlider(self.limits_box)
        self.limits_slider_y.setSingleStep(10)
        self.limits_slider_y.setPageStep(5000)
        self.limits_slider_y.setOrientation(QtCore.Qt.Horizontal)
        self.limits_slider_y.setInvertedAppearance(False)
        self.limits_slider_y.setInvertedControls(False)
        self.limits_slider_y.setObjectName(_fromUtf8("limits_slider_y"))
        self.gridLayout.addWidget(self.limits_slider_y, 4, 1, 1, 1)
        self.limits_autoFromData = QtGui.QRadioButton(self.limits_box)
        self.limits_autoFromData.setChecked(True)
        self.limits_autoFromData.setObjectName(_fromUtf8("limits_autoFromData"))
        self.gridLayout.addWidget(self.limits_autoFromData, 0, 1, 1, 1)
        self.limits_label_y = QtGui.QLabel(self.limits_box)
        self.limits_label_y.setObjectName(_fromUtf8("limits_label_y"))
        self.gridLayout.addWidget(self.limits_label_y, 4, 0, 1, 1)
        self.limits_text_y = QtGui.QLineEdit(self.limits_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.limits_text_y.sizePolicy().hasHeightForWidth())
        self.limits_text_y.setSizePolicy(sizePolicy)
        self.limits_text_y.setMaximumSize(QtCore.QSize(60, 60))
        self.limits_text_y.setObjectName(_fromUtf8("limits_text_y"))
        self.gridLayout.addWidget(self.limits_text_y, 4, 2, 1, 1)
        self.limits_text_x = QtGui.QLineEdit(self.limits_box)
        self.limits_text_x.setMaximumSize(QtCore.QSize(60, 60))
        self.limits_text_x.setObjectName(_fromUtf8("limits_text_x"))
        self.gridLayout.addWidget(self.limits_text_x, 3, 2, 1, 1)
        self.limits_manual = QtGui.QRadioButton(self.limits_box)
        self.limits_manual.setObjectName(_fromUtf8("limits_manual"))
        self.gridLayout.addWidget(self.limits_manual, 2, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.limits_box)
        self.preview_group = QtGui.QGroupBox(self.verticalLayoutWidget)
        self.preview_group.setStyleSheet(_fromUtf8(" QGroupBox {\n"
"     border-top: 1px solid black;\n"
"     border-bottom: 1px solid black;\n"
"     margin-top: 1ex;\n"
" }\n"
"\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }"))
        self.preview_group.setCheckable(True)
        self.preview_group.setObjectName(_fromUtf8("preview_group"))
        self.verticalLayout = QtGui.QVBoxLayout(self.preview_group)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self._every = QtGui.QLabel(self.preview_group)
        self._every.setObjectName(_fromUtf8("_every"))
        self.horizontalLayout_2.addWidget(self._every)
        self.preview_repeatInterval = QtGui.QLineEdit(self.preview_group)
        self.preview_repeatInterval.setObjectName(_fromUtf8("preview_repeatInterval"))
        self.horizontalLayout_2.addWidget(self.preview_repeatInterval)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.preview_group)
        self.preview_now = QtGui.QPushButton(self.verticalLayoutWidget)
        self.preview_now.setObjectName(_fromUtf8("preview_now"))
        self.verticalLayout_3.addWidget(self.preview_now)
        self.record_group = QtGui.QGroupBox(self.verticalLayoutWidget)
        self.record_group.setStyleSheet(_fromUtf8(" QGroupBox {\n"
"     border-top: 1px solid black;\n"
"     border-bottom: 1px solid black;\n"
"     margin-top: 1ex;\n"
" }\n"
"\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }"))
        self.record_group.setObjectName(_fromUtf8("record_group"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.record_group)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.record_url = KUrlComboRequester(self.record_group)
        self.record_url.setObjectName(_fromUtf8("record_url"))
        self.verticalLayout_4.addWidget(self.record_url)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.record_group)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.record_prefix = QtGui.QLineEdit(self.record_group)
        self.record_prefix.setObjectName(_fromUtf8("record_prefix"))
        self.horizontalLayout_3.addWidget(self.record_prefix)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.record_startstop = QtGui.QPushButton(self.record_group)
        self.record_startstop.setCheckable(True)
        self.record_startstop.setObjectName(_fromUtf8("record_startstop"))
        self.verticalLayout_4.addWidget(self.record_startstop)
        self.verticalLayout_3.addWidget(self.record_group)
        self.control_clear = QtGui.QPushButton(self.verticalLayoutWidget)
        self.control_clear.setObjectName(_fromUtf8("control_clear"))
        self.verticalLayout_3.addWidget(self.control_clear)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.connectionStatus = QtGui.QLabel(self.verticalLayoutWidget)
        self.connectionStatus.setObjectName(_fromUtf8("connectionStatus"))
        self.horizontalLayout_4.addWidget(self.connectionStatus)
        self.reconnectButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.reconnectButton.setEnabled(False)
        self.reconnectButton.setObjectName(_fromUtf8("reconnectButton"))
        self.horizontalLayout_4.addWidget(self.reconnectButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.analogdisplay_layout = QtGui.QGridLayout()
        self.analogdisplay_layout.setObjectName(_fromUtf8("analogdisplay_layout"))
        self.temperature_value = QtGui.QLabel(self.verticalLayoutWidget)
        self.temperature_value.setStyleSheet(_fromUtf8("font-family:monospace;\n"
"font-size:20pt;\n"
"color:#FF4000;\n"
"background-color:black;"))
        self.temperature_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.temperature_value.setObjectName(_fromUtf8("temperature_value"))
        self.analogdisplay_layout.addWidget(self.temperature_value, 2, 1, 1, 1)
        self.voltage_mean_label = QtGui.QLabel(self.verticalLayoutWidget)
        self.voltage_mean_label.setText(_fromUtf8(""))
        self.voltage_mean_label.setObjectName(_fromUtf8("voltage_mean_label"))
        self.analogdisplay_layout.addWidget(self.voltage_mean_label, 3, 0, 1, 1)
        self.voltage_label = QtGui.QLabel(self.verticalLayoutWidget)
        self.voltage_label.setObjectName(_fromUtf8("voltage_label"))
        self.analogdisplay_layout.addWidget(self.voltage_label, 1, 0, 1, 1)
        self.temperature_label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.temperature_label_2.setObjectName(_fromUtf8("temperature_label_2"))
        self.analogdisplay_layout.addWidget(self.temperature_label_2, 1, 1, 1, 1)
        self.voltage_value = QtGui.QLabel(self.verticalLayoutWidget)
        self.voltage_value.setStyleSheet(_fromUtf8("font-family:monospace;\n"
"font-size:20pt;\n"
"color:#0084FF;\n"
"background-color:black;"))
        self.voltage_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.voltage_value.setMargin(20)
        self.voltage_value.setObjectName(_fromUtf8("voltage_value"))
        self.analogdisplay_layout.addWidget(self.voltage_value, 2, 0, 1, 1)
        self.line = QtGui.QFrame(self.verticalLayoutWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.analogdisplay_layout.addWidget(self.line, 0, 0, 1, 1)
        self.verticalLayout_3.addLayout(self.analogdisplay_layout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout_5.addWidget(self.window_splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 880, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuData = QtGui.QMenu(self.menubar)
        self.menuData.setObjectName(_fromUtf8("menuData"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionSave_displayed = QtGui.QAction(MainWindow)
        self.actionSave_displayed.setObjectName(_fromUtf8("actionSave_displayed"))
        self.actionOpen_and_continue = QtGui.QAction(MainWindow)
        self.actionOpen_and_continue.setEnabled(False)
        self.actionOpen_and_continue.setObjectName(_fromUtf8("actionOpen_and_continue"))
        self.menuFile.addAction(self.actionQuit)
        self.menuData.addAction(self.actionSave_displayed)
        self.menuData.addAction(self.actionOpen_and_continue)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuData.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("activated()")), MainWindow.close)
        QtCore.QObject.connect(self.mode_interval, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.gradientSettings_group.setHidden)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_group.setTitle(QtGui.QApplication.translate("MainWindow", "Data Acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_interval.setToolTip(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Acquire chunks of an exact length, and add them all together for the result. To reduce the amount of data to process, <span style=\" font-style:italic;\">Integration [samples]</span> nearby samples are squared and added together.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_interval.setText(QtGui.QApplication.translate("MainWindow", "Interval", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_gradient.setToolTip(QtGui.QApplication.translate("MainWindow", "Acquire chunks of some length, and add all of each chunks\' samples together. For the result, the values obtained by this are just plotted sequentially. This gives a rough plot of signal intensity over time.", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_gradient.setText(QtGui.QApplication.translate("MainWindow", "Gradient", None, QtGui.QApplication.UnicodeUTF8))
        self.invertSignalCheckbox.setText(QtGui.QApplication.translate("MainWindow", "Invert signal", None, QtGui.QApplication.UnicodeUTF8))
        self.gradientSettings_group.setTitle(QtGui.QApplication.translate("MainWindow", "Integrate the data automatically", None, QtGui.QApplication.UnicodeUTF8))
        self._integration_g.setText(QtGui.QApplication.translate("MainWindow", "Integration [samples]:", None, QtGui.QApplication.UnicodeUTF8))
        self.gradientSettings_integrate.setText(QtGui.QApplication.translate("MainWindow", "30", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_box.setTitle(QtGui.QApplication.translate("MainWindow", "Diagram limits", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_label_x.setText(QtGui.QApplication.translate("MainWindow", "min", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_autoFromIntegrated.setText(QtGui.QApplication.translate("MainWindow", "Auto: from integrated data", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_autoFromData.setText(QtGui.QApplication.translate("MainWindow", "Auto: from data", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_label_y.setText(QtGui.QApplication.translate("MainWindow", "max", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_text_y.setText(QtGui.QApplication.translate("MainWindow", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_text_x.setText(QtGui.QApplication.translate("MainWindow", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.limits_manual.setText(QtGui.QApplication.translate("MainWindow", "Manual", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_group.setTitle(QtGui.QApplication.translate("MainWindow", "Auto preview", None, QtGui.QApplication.UnicodeUTF8))
        self._every.setText(QtGui.QApplication.translate("MainWindow", "every [samples]", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_repeatInterval.setText(QtGui.QApplication.translate("MainWindow", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_now.setText(QtGui.QApplication.translate("MainWindow", "Preview now", None, QtGui.QApplication.UnicodeUTF8))
        self.record_group.setTitle(QtGui.QApplication.translate("MainWindow", "Recording", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Prefix:", None, QtGui.QApplication.UnicodeUTF8))
        self.record_prefix.setText(QtGui.QApplication.translate("MainWindow", "data_", None, QtGui.QApplication.UnicodeUTF8))
        self.record_startstop.setText(QtGui.QApplication.translate("MainWindow", "Record", None, QtGui.QApplication.UnicodeUTF8))
        self.control_clear.setText(QtGui.QApplication.translate("MainWindow", "Clear data", None, QtGui.QApplication.UnicodeUTF8))
        self.connectionStatus.setText(QtGui.QApplication.translate("MainWindow", "Not connected", None, QtGui.QApplication.UnicodeUTF8))
        self.reconnectButton.setText(QtGui.QApplication.translate("MainWindow", "Reconnect", None, QtGui.QApplication.UnicodeUTF8))
        self.temperature_value.setText(QtGui.QApplication.translate("MainWindow", "--.--", None, QtGui.QApplication.UnicodeUTF8))
        self.voltage_label.setText(QtGui.QApplication.translate("MainWindow", "Voltage (mV)", None, QtGui.QApplication.UnicodeUTF8))
        self.temperature_label_2.setText(QtGui.QApplication.translate("MainWindow", "Temperature (°C)", None, QtGui.QApplication.UnicodeUTF8))
        self.voltage_value.setText(QtGui.QApplication.translate("MainWindow", "--.--", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuData.setTitle(QtGui.QApplication.translate("MainWindow", "Data", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_displayed.setText(QtGui.QApplication.translate("MainWindow", "Save displayed...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_and_continue.setText(QtGui.QApplication.translate("MainWindow", "Open and continue...", None, QtGui.QApplication.UnicodeUTF8))

from PyKDE4.kio import KUrlComboRequester
from PyKDE4.kdeui import KPlotWidget
