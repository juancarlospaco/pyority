#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:NO, LINT:OK, PY3:OK


# metadata
""" Pyority """
__version__ = ' 0.0.1 '
__license__ = ' GPLv3+ '
__author__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/pyority#pyority'
__date__ = '2015/01/01'
__docformat__ = 'html'


# imports
import sys
from getopt import getopt
from getpass import getuser
from subprocess import call
from webbrowser import open_new_tab

import psutil
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QVBoxLayout,
                             QGraphicsDropShadowEffect, QGroupBox, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QShortcut,
                             QSlider, QTableWidget, QTableWidgetItem, QWidget)


HELP = """<h3>Pyority:</h3><b>Change CPU and I/O Priorities with Python!</b><br>
{} version {}, licence GPLv3+, by {}""".format(__doc__, __version__, __author__)


###############################################################################


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__doc__.strip().capitalize())
        self.statusBar().showMessage(" Choose one App and move the sliders !")
        self.setMinimumSize(480, 240)
        self.setMaximumSize(640, 2048)
        self.setWindowIcon(QIcon.fromTheme("preferences-system"))
        self.center()
        QShortcut("Ctrl+q", self, activated=lambda: self.close())
        self.menuBar().addMenu("&File").addAction("Exit", exit)
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3",
                           lambda: open_new_tab('https://www.python.org'))
        helpMenu.addAction("About" + __doc__,
                           lambda: QMessageBox.about(self, __doc__, HELP))
        helpMenu.addSeparator()
        helpMenu.addAction("Keyboard Shortcut", lambda: QMessageBox.information(
            self, __doc__, "<b>Quit = CTRL+Q"))
        helpMenu.addAction("View Source Code",
                           lambda: call('xdg-open ' + __file__, shell=True))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        container, child_container = QWidget(), QWidget()
        container_layout = QVBoxLayout(container)
        child_layout = QHBoxLayout(child_container)
        self.setCentralWidget(container)
        # widgets
        group0 = QGroupBox("My Apps")
        group1, group2 = QGroupBox("CPU Priority"), QGroupBox("HDD Priority")
        child_layout.addWidget(group0)
        child_layout.addWidget(group1)
        child_layout.addWidget(group2)
        container_layout.addWidget(child_container)
        # table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setIconSize(QSize(64, 64))
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Graphic effect
        glow = QGraphicsDropShadowEffect(self)
        glow.setOffset(0)
        glow.setBlurRadius(9)
        glow.setColor(QColor(99, 255, 255))
        self.table.setGraphicsEffect(glow)
        glow.setEnabled(True)
        processes = self.generate_process_list()
        self.table.setRowCount(len(processes))
        for index, process in enumerate(processes):
            item = QTableWidgetItem(
                QIcon.fromTheme(process.name().split()[0].split('/')[0]),
                process.name().split()[0].split('/')[0].strip())
            item.setData(Qt.UserRole, process)
            item.setToolTip("{}, {}, {}, {}".format(
                process.name(), process.nice(),
                process.ionice()[1], process.pid))
            self.table.setItem(index, 0, item)
        self.table.clicked.connect(lambda: self.sliderhdd.setDisabled(False))
        self.table.clicked.connect(lambda: self.slidercpu.setDisabled(False))
        self.table.clicked.connect(lambda: self.slidercpu.setValue(
            int(tuple(self.table.currentItem().toolTip().split(","))[1])))
        self.table.clicked.connect(lambda: self.sliderhdd.setValue(
            int(tuple(self.table.currentItem().toolTip().split(","))[2])))
        self.table.resizeColumnsToContents()
        # self.table.resizeRowsToContents()
        # sliders
        self.slidercpu = QSlider()
        self.slidercpu.setRange(0, 19)
        self.slidercpu.setSingleStep(1)
        self.slidercpu.setTickPosition(3)
        self.slidercpu.setDisabled(True)
        self.slidercpu.setInvertedAppearance(True)
        self.slidercpu.setInvertedControls(True)
        self.slidercpu.valueChanged.connect(self.set_cpu_value)
        self.slidercpu.valueChanged.connect(
            lambda: self.slidercpu.setToolTip(str(self.slidercpu.value())))
        # Timer to start
        self.slidercpu_timer = QTimer(self)
        self.slidercpu_timer.setSingleShot(True)
        self.slidercpu_timer.timeout.connect(self.on_slidercpu_timer_timeout)
        QLabel(self.slidercpu).setPixmap(QIcon.fromTheme("list-add").pixmap(16))
        QVBoxLayout(group1).addWidget(self.slidercpu)
        self.sliderhdd = QSlider()
        self.sliderhdd.setRange(0, 7)
        self.sliderhdd.setSingleStep(1)
        self.sliderhdd.setTickPosition(3)
        self.sliderhdd.setDisabled(True)
        self.sliderhdd.setInvertedAppearance(True)
        self.sliderhdd.setInvertedControls(True)
        self.sliderhdd.valueChanged.connect(self.set_hdd_value)
        self.sliderhdd.valueChanged.connect(
            lambda: self.sliderhdd.setToolTip(str(self.sliderhdd.value())))
        # Timer to start
        self.sliderhdd_timer = QTimer(self)
        self.sliderhdd_timer.setSingleShot(True)
        self.sliderhdd_timer.timeout.connect(self.on_sliderhdd_timer_timeout)
        QLabel(self.sliderhdd).setPixmap(QIcon.fromTheme("list-add").pixmap(16))
        QVBoxLayout(group2).addWidget(self.sliderhdd)
        QVBoxLayout(group0).addWidget(self.table)

    def set_cpu_value(self):
        if self.slidercpu_timer.isActive():
            self.slidercpu_timer.stop()
        self.slidercpu_timer.start(1000)

    def set_hdd_value(self):
        if self.sliderhdd_timer.isActive():
            self.sliderhdd_timer.stop()
        self.sliderhdd_timer.start(1000)

    def on_slidercpu_timer_timeout(self):
        pid = int(tuple(self.table.currentItem().toolTip().split(","))[3])
        nice_before = psutil.Process(pid).nice()
        psutil.Process(pid).nice(self.slidercpu.value())
        self.statusBar().showMessage('nice before: {}, nice after: {}.'.format(
            nice_before, psutil.Process(pid).nice()), 5000)

    def on_sliderhdd_timer_timeout(self):
        pid = int(tuple(self.table.currentItem().toolTip().split(","))[3])
        ionice_before = psutil.Process(pid).ionice()
        psutil.Process(pid).ionice(
            2 if self.sliderhdd.value() < 7 else 0,
            self.sliderhdd.value() if self.sliderhdd.value() < 7 else None)
        self.statusBar().showMessage(
            'ionice before: {}, ionice after: {}'.format(
                ionice_before, psutil.Process(pid).ionice()), 5000)

    def center(self):
        """Center the Window on the Current Screen,with Multi-Monitor support"""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerPoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position"""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def closeEvent(self, event):
        ' Ask to Quit '
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit ?.', QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        event.accept() if the_conditional_is_true else event.ignore()

    def generate_process_list(self):
        return [p for p in psutil.process_iter() if p.username() == getuser()]


###############################################################################


def main():
    ' Main Loop '
    application = QApplication(sys.argv)
    application.setStyle('Oxygen')
    application.setApplicationName(__doc__.strip().lower())
    application.setOrganizationName(__doc__.strip().lower())
    application.setOrganizationDomain(__doc__.strip())
    application.setWindowIcon(QIcon.fromTheme("preferences-system"))
    try:
        opts, args = getopt(sys.argv[1:], 'hv', ('version', 'help'))
    except:
        pass
    for o, v in opts:
        if o in ('-h', '--help'):
            print(''' Usage:
                  -h, --help        Show help informations and exit.
                  -v, --version     Show version information and exit.''')
            return sys.exit(1)
        elif o in ('-v', '--version'):
            print(__version__)
            return sys.exit(1)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())


if __name__ in '__main__':
    main()
