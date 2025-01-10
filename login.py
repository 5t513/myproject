# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
import MainProgram
from second import PollutionThresholdWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.window = None
        self.win = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('登录')
        self.setGeometry(200, 200, 400, 200)

        # 标签和输入框
        self.username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # 登录按钮
        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.login)

        # 布局
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        hbox1.addWidget(self.username_label)
        hbox1.addWidget(self.username_input)
        hbox2.addWidget(self.password_label)
        hbox2.addWidget(self.password_input)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.login_button)

        self.setLayout(vbox)

        # 添加样式
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            QLineEdit, QPushButton {
                font-size: 16px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # 在这里进行用户验证逻辑，这里简单地进行了判断
        if username == 'admin' and password == 'admin':
            QMessageBox.information(self, '登录成功', '登录成功！')
            self.close()
            self.window = PollutionThresholdWindow()
            self.window.show()

        else:
            QMessageBox.warning(self, '登录失败', '用户名或密码错误！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
