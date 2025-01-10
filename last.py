# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QFont

import Common


class MainWindow1(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('类别数量统计')
        self.setGeometry(100, 100, 400, 300)

        # Create labels to display class counts
        self.labels = {}
        for key, value in Common.common.class_count.items():
            label = QLabel(f'{key}: {value}')
            self.labels[key] = label

        # Create a button to check thresholds
        self.btn_check_threshold = QPushButton('检查阈值')
        self.btn_check_threshold.clicked.connect(self.check_thresholds)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Add labels to the layout
        for label in self.labels.values():
            label.setFont(QFont("Arial", 12))
            layout.addWidget(label)

        # Add button to the layout
        layout.addWidget(self.btn_check_threshold)

        self.setLayout(layout)

        # Apply stylesheet to the widget
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def check_thresholds(self):
        warning_messages = []
        # Check if class count exceeds thresholds
        for key, value in Common.common.thresholds.items():
            if key in Common.common.class_count and value < Common.common.class_count[key]:
                warning_messages.append(f'{key} 的数量超过阈值 {Common.common.thresholds[key]}')

        # Show warning message if thresholds exceeded
        if warning_messages:
            QMessageBox.warning(self, '警告', '\n'.join(warning_messages))
        else:
            QMessageBox.information(self, '提示', '各类别数量正常')

    def update_counts(self, class_name, count):
        if class_name in Common.common.class_count:
            Common.common.class_count[class_name] = count
            self.labels[class_name].setText(f'{class_name}: {count}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow1()
    window.show()
    sys.exit(app.exec_())
