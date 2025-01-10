# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

import MainProgram
import Common

class PollutionThresholdWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('污染物阈值设置')
        self.setGeometry(200, 200, 400, 300)

        # 说明标签
        self.instruction_label = QLabel('请输入每个污染物的阈值，超过该阈值就会发出相应预警')
        self.instruction_label.setStyleSheet("font-weight: bold;")

        # 创建标签和文本框
        self.labels = []
        self.lineedits = []
        pollutants = ['垃圾', '油膜', '绿藻', '污水', '水草', '浮萍', '沉积物', '泥沙', '水污染', '苔藓']

        for pollutant in pollutants:
            label = QLabel(pollutant + ':')
            label.setStyleSheet("font-size: 14px;")
            lineedit = QLineEdit()
            lineedit.setObjectName(pollutant)  # 设置对象名称
            self.labels.append(label)
            self.lineedits.append(lineedit)

        # 创建确定按钮
        self.confirm_button = QPushButton('确定')
        self.confirm_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.confirm_button.clicked.connect(self.checkThresholds)

        # 设置布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.instruction_label)
        for i in range(len(pollutants)):
            vbox.addWidget(self.labels[i])
            vbox.addWidget(self.lineedits[i])

        vbox.addWidget(self.confirm_button)
        self.setLayout(vbox)

        # 设置窗口背景颜色
        self.setStyleSheet("background-color: #f0f0f0;")

    def checkThresholds(self):
        for lineedit in self.lineedits:
            value = lineedit.text()
            if value == '':
                QMessageBox.warning(self, '警告', '请输入阈值！')
                return
            try:
                threshold = float(value)
                if threshold < 0:
                    QMessageBox.warning(self, '警告', '请输入正确阈值！')
                    return
                Common.common.thresholds[lineedit.objectName()] = threshold
            except ValueError:
                QMessageBox.warning(self, '警告', '请输入正确阈值！')
                return

        QMessageBox.information(self, '成功', '阈值设置成功！')
        self.close()
        self.win = MainProgram.MainWindow()
        self.win.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PollutionThresholdWindow()
    window.show()
    sys.exit(app.exec_())

