#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:NO, LINT:OK, PY3:OK


# metadata
"""Pyority."""
__package__ = "pyority"
__version__ = ' 0.0.1 '
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/pyority#pyority'
__date__ = '2015/01/01'
__docformat__ = 'html'
__source__ = ('https://raw.githubusercontent.com/juancarlospaco/'
              'pyority/master/pyority.py')


# imports
import os
import sys
from ctypes import byref, cdll, create_string_buffer
from copy import copy
from getopt import getopt
from getpass import getuser
import logging as log
from subprocess import call
from urllib import request
from webbrowser import open_new_tab
import signal
import time
from datetime import datetime

import psutil

from PyQt5.QtCore import QSize, Qt, QTimer, QUrl
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkProxyFactory,
                             QNetworkRequest)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QFontDialog,
                             QGraphicsDropShadowEffect, QGroupBox, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QShortcut,
                             QSlider, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget, QProgressDialog)


HELP = """<h3>Pyority:</h3><b>Change CPU and I/O Priority with Python!</b><br>
{} version {}, licence GPLv3+,by {}""".format(__doc__, __version__, __author__)


###############################################################################


class Downloader(QProgressDialog):

    """Downloader Dialog with complete informations and progress bar."""

    def __init__(self, parent=None):
        """Init class."""
        super(Downloader, self).__init__(parent)
        self.setWindowTitle(__doc__)
        if not os.path.isfile(__file__) or not __source__:
            return
        if not os.access(__file__, os.W_OK):
            error_msg = ("Destination file permission denied (not Writable)! "
                         "Try again to Update but as root or administrator.")
            log.critical(error_msg)
            QMessageBox.warning(self, __doc__.title(), error_msg)
            return
        self._time, self._date = time.time(), datetime.now().isoformat()[:-7]
        self._url, self._dst = __source__, __file__
        log.debug("Downloading from {} to {}.".format(self._url, self._dst))
        if not self._url.lower().startswith("https:"):
            log.warning("Unsecure Download over plain text without SSL.")
        self.template = """<h3>Downloading</h3><hr><table>
        <tr><td><b>From:</b></td>      <td>{}</td>
        <tr><td><b>To:  </b></td>      <td>{}</td> <tr>
        <tr><td><b>Started:</b></td>   <td>{}</td>
        <tr><td><b>Actual:</b></td>    <td>{}</td> <tr>
        <tr><td><b>Elapsed:</b></td>   <td>{}</td>
        <tr><td><b>Remaining:</b></td> <td>{}</td> <tr>
        <tr><td><b>Received:</b></td>  <td>{} MegaBytes</td>
        <tr><td><b>Total:</b></td>     <td>{} MegaBytes</td> <tr>
        <tr><td><b>Speed:</b></td>     <td>{}</td>
        <tr><td><b>Percent:</b></td>     <td>{}%</td></table><hr>"""
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.save_downloaded_data)
        self.manager.sslErrors.connect(self.download_failed)
        self.progreso = self.manager.get(QNetworkRequest(QUrl(self._url)))
        self.progreso.downloadProgress.connect(self.update_download_progress)
        self.show()
        self.exec_()

    def save_downloaded_data(self, data):
        """Save all downloaded data to the disk and quit."""
        log.debug("Download done. Update Done.")
        with open(os.path.join(self._dst), "wb") as output_file:
            output_file.write(data.readAll())
        data.close()
        QMessageBox.information(self, __doc__.title(),
                                "<b>You got the latest version of this App!")
        del self.manager, data
        return self.close()

    def download_failed(self, download_error):
        """Handle a download error, probable SSL errors."""
        log.error(download_error)
        QMessageBox.warning(self, __doc__.title(), str(download_error))

    def seconds_time_to_human_string(self, time_on_seconds=0):
        """Calculate time, with precision from seconds to days."""
        minutes, seconds = divmod(int(time_on_seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        human_time_string = ""
        if days:
            human_time_string += "%02d Days " % days
        if hours:
            human_time_string += "%02d Hours " % hours
        if minutes:
            human_time_string += "%02d Minutes " % minutes
        human_time_string += "%02d Seconds" % seconds
        return human_time_string

    def update_download_progress(self, bytesReceived, bytesTotal):
        """Calculate statistics and update the UI with them."""
        downloaded_MB = round(((bytesReceived / 1024) / 1024), 2)
        total_data_MB = round(((bytesTotal / 1024) / 1024), 2)
        downloaded_KB, total_data_KB = bytesReceived / 1024, bytesTotal / 1024
        # Calculate download speed values, with precision from Kb/s to Gb/s
        elapsed = time.clock()
        if elapsed > 0:
            speed = round((downloaded_KB / elapsed), 2)
            if speed > 1024000:  # Gigabyte speeds
                download_speed = "{} GigaByte/Second".format(speed // 1024000)
            if speed > 1024:  # MegaByte speeds
                download_speed = "{} MegaBytes/Second".format(speed // 1024)
            else:  # KiloByte speeds
                download_speed = "{} KiloBytes/Second".format(int(speed))
        if speed > 0:
            missing = abs((total_data_KB - downloaded_KB) // speed)
        percentage = int(100.0 * bytesReceived // bytesTotal)
        self.setLabelText(self.template.format(
            self._url.lower()[:99], self._dst.lower()[:99],
            self._date, datetime.now().isoformat()[:-7],
            self.seconds_time_to_human_string(time.time() - self._time),
            self.seconds_time_to_human_string(missing),
            downloaded_MB, total_data_MB, download_speed, percentage))
        self.setValue(percentage)


###############################################################################


class MainWindow(QMainWindow):

    """Main window class."""

    def __init__(self, parent=None):
        """Init class."""
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
        windowMenu.addAction("FullScreen", lambda: self.showFullScreen())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("Top-Left", lambda: self.move(0, 0))
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        windowMenu.addSeparator()
        windowMenu.addAction(
            "Increase size", lambda:
            self.resize(self.size().width() * 1.4, self.size().height() * 1.4))
        windowMenu.addAction("Decrease size", lambda: self.resize(
            self.size().width() // 1.4, self.size().height() // 1.4))
        windowMenu.addAction("Minimum size", lambda:
                             self.resize(self.minimumSize()))
        windowMenu.addAction("Maximum size", lambda:
                             self.resize(self.maximumSize()))
        windowMenu.addAction("Horizontal Wide", lambda: self.resize(
            self.maximumSize().width(), self.minimumSize().height()))
        windowMenu.addAction("Vertical Tall", lambda: self.resize(
            self.minimumSize().width(), self.maximumSize().height()))
        windowMenu.addSeparator()
        windowMenu.addAction("Disable Resize", lambda:
                             self.setFixedSize(self.size()))
        windowMenu.addAction("Set Interface Font...", lambda:
                             self.setFont(QFontDialog.getFont()[0]))
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3",
                           lambda: open_new_tab('https://www.python.org'))
        helpMenu.addAction("About" + __doc__,
                           lambda: QMessageBox.about(self, __doc__, HELP))
        helpMenu.addSeparator()
        helpMenu.addAction(
            "Keyboard Shortcut",
            lambda: QMessageBox.information(self, __doc__, "<b>Quit = CTRL+Q"))
        helpMenu.addAction("View Source Code",
                           lambda: call('xdg-open ' + __file__, shell=True))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        helpMenu.addAction("Report Bugs", lambda: open_new_tab(
            'https://github.com/juancarlospaco/pyority/issues?state=open'))
        helpMenu.addAction("Check Updates", lambda: self.check_for_updates())
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
        QLabel(self.slidercpu).setPixmap(
            QIcon.fromTheme("list-add").pixmap(16))
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
        QLabel(self.sliderhdd).setPixmap(
            QIcon.fromTheme("list-add").pixmap(16))
        QVBoxLayout(group2).addWidget(self.sliderhdd)
        QVBoxLayout(group0).addWidget(self.table)

    def set_cpu_value(self):
        """Set the CPU value."""
        if self.slidercpu_timer.isActive():
            self.slidercpu_timer.stop()
        self.slidercpu_timer.start(1000)

    def set_hdd_value(self):
        """Set the Disk value."""
        if self.sliderhdd_timer.isActive():
            self.sliderhdd_timer.stop()
        self.sliderhdd_timer.start(1000)

    def on_slidercpu_timer_timeout(self):
        """What to do on slider timer time out."""
        pid = int(tuple(self.table.currentItem().toolTip().split(","))[3])
        psutil.Process(pid).nice(self.slidercpu.value())
        nice_result = 'Nice before: {},nice after: {}.'.format(
            psutil.Process(pid).nice(), psutil.Process(pid).nice())
        self.statusBar().showMessage(nice_result, 5000)
        log.info(nice_result)

    def on_sliderhdd_timer_timeout(self):
        """What to do on slider timer time out."""
        pid = int(tuple(self.table.currentItem().toolTip().split(","))[3])
        ionice_before = psutil.Process(pid).ionice()
        psutil.Process(pid).ionice(
            2 if self.sliderhdd.value() < 7 else 0,
            self.sliderhdd.value() if self.sliderhdd.value() < 7 else None)
        nice_result = 'ionice before: {}, ionice after: {}'.format(
            ionice_before, psutil.Process(pid).ionice())
        self.statusBar().showMessage(nice_result, 5000)
        log.info(nice_result)

    def check_for_updates(self):
        """Method to check for updates from Git repo versus this version."""
        this_version = str(open(__file__).read())
        last_version = str(request.urlopen(__source__).read().decode("utf8"))
        if this_version != last_version:
            m = "Theres new Version available!<br>Download update from the web"
        else:
            m = "No new updates!<br>You have the lastest version of this app"
        return QMessageBox.information(self, __doc__.title(), "<b>" + m)

    def center(self):
        """Center Window on the Current Screen,with Multi-Monitor support."""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerPoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position."""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def closeEvent(self, event):
        """Ask to Quit."""
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit ?.', QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        event.accept() if the_conditional_is_true else event.ignore()

    def generate_process_list(self):
        """Return a list of processes."""
        return [p for p in psutil.process_iter() if p.username() == getuser()]


###############################################################################


def main():
    """Main Loop."""
    APPNAME = str(__package__ or __doc__)[:99].lower().strip().replace(" ", "")
    if not sys.platform.startswith("win") and sys.stderr.isatty():
        def add_color_emit_ansi(fn):
            """Add methods we need to the class."""
            def new(*args):
                """Method overload."""
                if len(args) == 2:
                    new_args = (args[0], copy(args[1]))
                else:
                    new_args = (args[0], copy(args[1]), args[2:])
                if hasattr(args[0], 'baseFilename'):
                    return fn(*args)
                levelno = new_args[1].levelno
                if levelno >= 50:
                    color = '\x1b[31m'  # red
                elif levelno >= 40:
                    color = '\x1b[31m'  # red
                elif levelno >= 30:
                    color = '\x1b[33m'  # yellow
                elif levelno >= 20:
                    color = '\x1b[32m'  # green
                elif levelno >= 10:
                    color = '\x1b[35m'  # pink
                else:
                    color = '\x1b[0m'  # normal
                try:
                    new_args[1].msg = color + str(new_args[1].msg) + '\x1b[0m'
                except Exception as reason:
                    print(reason)  # Do not use log here.
                return fn(*new_args)
            return new
        # all non-Windows platforms support ANSI Colors so we use them
        log.StreamHandler.emit = add_color_emit_ansi(log.StreamHandler.emit)
    log.basicConfig(level=-1, format="%(levelname)s:%(asctime)s %(message)s")
    log.getLogger().addHandler(log.StreamHandler(sys.stderr))
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary('libc.so.6')  # set process name
        buff = create_string_buffer(len(APPNAME) + 1)
        buff.value = bytes(APPNAME.encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception as reason:
        log.warning(reason)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # CTRL+C work to quit app
    application = QApplication(sys.argv)
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
            return sys.exit(0)
        elif o in ('-v', '--version'):
            print(__version__)
            return sys.exit(0)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())


if __name__ in '__main__':
    main()
