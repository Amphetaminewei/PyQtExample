#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
        QMessageBox, QProgressBar)

import mainwindow_rc
from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    # Maintain the list of browser windows so that they do not get garbage
    # collected.
    _window_list = []

    def __init__(self):
        # 调用父类mainwindow的构造函数
        super(MainWindow, self).__init__()

        # 如果我没理解错的话，append就是把 *this 内的对象依次放到window_list里面

        MainWindow._window_list.append(self)

        self.setupUi(self)

        # Qt Designer (at least to v4.2.1) can't handle arbitrary widgets in a
        # QToolBar - even though uic can, and they are in the original .ui
        # file.  Therefore we manually add the problematic widgets.

        # Qt Desinger不能处理QToolBar中的小部件，因此这里要手动处理有问题的小部件

        # 这里添加的小部件有编辑框和Label，并将其加入到工具栏中，和go动作绑定在一起
        # 通过QLabel和QLineEdit的构造函数都和C++形式差不多，第一个字符串参数是显示
        # 初始控件中的文字，后面的是parent，绑定他的父控件，应该和C++那套一样，通过
        # 父控件的析构来析构子控件，防止出现野控件

        # 同时注意一下，Python里面定义新变量不需要指定类型，如果我没理解错的话，
        # self.lblAddress就是个新建的对象，用来存储QLabel构造函数的返回值

        self.lblAddress = QLabel("Address", self.tbAddress)
        self.tbAddress.insertWidget(self.actionGo, self.lblAddress)
        self.addressEdit = QLineEdit(self.tbAddress)
        self.tbAddress.insertWidget(self.actionGo, self.addressEdit)

        # 信号槽绑定，这个好像和C++的不老么一样，但是更简单了，信号变成成员了
        # 而connect的参数就只有一个槽
        # *.signal.connect(slot)
        # 而C++的看起来是connect(signal_emiter,signal,slot_emiter,slot)

        self.addressEdit.returnPressed.connect(self.actionGo.trigger)
        self.actionBack.triggered.connect(self.WebBrowser.GoBack)
        self.actionForward.triggered.connect(self.WebBrowser.GoForward)
        self.actionStop.triggered.connect(self.WebBrowser.Stop)
        self.actionRefresh.triggered.connect(self.WebBrowser.Refresh)
        self.actionHome.triggered.connect(self.WebBrowser.GoHome)
        self.actionSearch.triggered.connect(self.WebBrowser.GoSearch)
        
        self.pb = QProgressBar(self.statusBar())
        self.pb.setTextVisible(False)
        self.pb.hide()
        self.statusBar().addPermanentWidget(self.pb)

        self.WebBrowser.dynamicCall('GoHome()')

    # 处理关闭事件的函数，析构list后调用accept来告诉程序这个事件已经被接收了
    # 对于closeEvent的处理，比较特殊，如果在重写的函数中显示调用accept
    # 触发closeEvent后窗口就将会被关闭，而如果显示调用ignore的话，则触发
    # closeEvent后窗口不会被关闭

    def closeEvent(self, e):
        MainWindow._window_list.remove(self)
        e.accept()

    # 这玩意，看起来好像是单纯的修改个title就完事了
    def on_WebBrowser_TitleChange(self, title):
        self.setWindowTitle("Qt WebBrowser - " + title)

    def on_WebBrowser_ProgressChange(self, a, b):
        if a <= 0 or b <= 0:
            self.pb.hide()
            return

        self.pb.show()
        self.pb.setRange(0, b)
        self.pb.setValue(a)

    def on_WebBrowser_CommandStateChange(self, cmd, on):
        if cmd == 1:
            self.actionForward.setEnabled(on)
        elif cmd == 2:
            self.actionBack.setEnabled(on)
            
    def on_WebBrowser_BeforeNavigate(self):
        self.actionStop.setEnabled(True)

    def on_WebBrowser_NavigateComplete(self, _):
        self.actionStop.setEnabled(False)

    @pyqtSlot()
    def on_actionGo_triggered(self):
        self.WebBrowser.dynamicCall('Navigate(const QString&)',
                self.addressEdit.text())

    @pyqtSlot()
    def on_actionNewWindow_triggered(self):
        window = MainWindow()
        window.show()
        if self.addressEdit.text().isEmpty():
            return;

        window.addressEdit.setText(self.addressEdit.text())
        window.actionStop.setEnabled(True)
        window.on_actionGo_triggered()

    @pyqtSlot()
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About WebBrowser",
                "This Example has been created using the ActiveQt integration into Qt Designer.\n"
                "It demonstrates the use of QAxWidget to embed the Internet Explorer ActiveX\n"
                "control into a Qt application.")

    @pyqtSlot()
    def on_actionAboutQt_triggered(self):
        QMessageBox.aboutQt(self, "About Qt")


if __name__ == "__main__":
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(a.exec_())
