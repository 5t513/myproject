# -*- coding: utf-8 -*-
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QMessageBox, QWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
import sys
import os
from PIL import ImageFont
from ultralytics import YOLO

sys.path.append('Interface_Program')
from Interface_Program.UiMain import Ui_MainWindow
import sys
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QCoreApplication
import detect_tools as tools
import cv2
import configuration
from Interface_Program.QssLoader import QSSLoader
from Interface_Program.precess_bar import ProgressBar
import numpy as np
import torch
import last
import Common


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.win1 = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initmain()
        self.clickconnect()

        # 加载css渲染效果
        style_file = 'Interface_Program/style.css'
        qss = QSSLoader.read_qss_file(style_file)
        self.setStyleSheet(qss)

        self.conf = 0.25
        self.iou = 0.7

    def clickconnect(self):
        self.ui.ImgBtn.clicked.connect(self.open_image)
        self.ui.Combox.activated.connect(self.Combox_change)
        self.ui.VideoBtn.clicked.connect(self.video_show)
        self.ui.CamBtn.clicked.connect(self.camera_show)
        self.ui.SaveBtn.clicked.connect(self.save)
        self.ui.WarnBtn.clicked.connect(self.next)
        self.ui.FileBtn.clicked.connect(self.detect_imgs)

    def initmain(self):
        self.display_width = 780
        self.display_height = 490

        self.my_path = None

        self.open_camera = False
        self.cap = None

        self.device = 0 if torch.cuda.is_available() else 'cpu'

        # 加载检测模型
        self.model = YOLO(configuration.model_path, task='detect')
        self.model(np.zeros((48, 48, 3)), device=self.device)  # 预先加载推理模型
        self.fontC = ImageFont.truetype("Font/pth.ttf", 25, 0)

        # 用于绘制不同颜色的矩形框
        self.colors = tools.Colors()

        # 更新视频图像
        self.timer_camera = QTimer()

        # 更新检测信息表格
        # self.timer_info = QTimer()
        # 保存视频
        self.timer_save_video = QTimer()

        # 表格
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(40)
        self.ui.tableWidget.setColumnWidth(0, 80)  # 设置列宽
        self.ui.tableWidget.setColumnWidth(1, 200)
        self.ui.tableWidget.setColumnWidth(2, 150)
        self.ui.tableWidget.setColumnWidth(3, 90)
        self.ui.tableWidget.setColumnWidth(4, 230)
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 表格铺满
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格不可编辑
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置表格整行选中
        self.ui.tableWidget.verticalHeader().setVisible(False)  # 隐藏列标题
        self.ui.tableWidget.setAlternatingRowColors(True)  # 表格背景交替

    def open_image(self):
        if self.cap:
            # 打开图片前关闭摄像头
            self.video_stop()
            self.open_camera = False
            self.ui.CamlineEdit.setText('摄像头未开启')
            self.cap = None

        # 弹出的窗口名称：'打开图片'
        # 默认打开的目录：'./'
        # 只能打开.jpg与.gif结尾的图片文件
        # file_path, _ = QFileDialog.getOpenFileName(self.ui.centralwidget, '打开图片', './', "Image files (*.jpg *.gif)")
        file_path, _ = QFileDialog.getOpenFileName(None, '打开图片', './', "Image files (*.jpg *.jepg *.png)")
        if not file_path:
            return

        self.ui.Combox.setDisabled(False)
        self.my_path = file_path
        self.my_img = tools.img_cvread(self.my_path)

        # 目标检测
        t1 = time.time()
        self.results = self.model(self.my_path, conf=self.conf, iou=self.iou)[0]
        t2 = time.time()
        take_time = '{:.3f} s'.format(t2 - t1)
        self.ui.time_lb.setText(take_time)

        loc = self.results.boxes.xyxy.tolist()
        self.loc = [list(map(int, e)) for e in loc]
        cls_list = self.results.boxes.cls.tolist()
        self.cls_list = [int(i) for i in cls_list]
        self.conf_list = self.results.boxes.conf.tolist()
        self.conf_list = ['%.2f %%' % (each * 100) for each in self.conf_list]

        # now_img = self.cv_img.copy()
        # for loacation, type_id, conf in zip(self.loc, self.cls_list, self.conf_list):
        #     type_id = int(type_id)
        #     color = self.colors(int(type_id), True)
        #     # cv2.rectangle(now_img, (int(x1), int(y1)), (int(x2), int(y2)), colors(int(type_id), True), 3)
        #     now_img = tools.drawRectBox(now_img, loacation, configuration.CH_names[type_id], self.fontC, color)

        # 统计类别数量
        for cls in self.cls_list:
            cl = configuration.CH_names[cls]
            if cl in Common.common.class_count:
                Common.common.class_count[cl] += 1
            else:
                Common.common.class_count[cl] = 1

        now_img = self.results.plot()
        self.draw_img = now_img
        # 获取缩放后的图片尺寸
        self.img_width, self.img_height = self.get_resize_size(now_img)
        resize_cvimg = cv2.resize(now_img, (self.img_width, self.img_height))
        pix_img = tools.cvimg_to_qpiximg(resize_cvimg)
        self.ui.label_show.setPixmap(pix_img)
        self.ui.label_show.setAlignment(Qt.AlignCenter)
        # 设置路径显示
        self.ui.PiclineEdit.setText(self.my_path)

        # 目标数目
        target_nums = len(self.cls_list)
        self.ui.label_nums.setText(str(target_nums))

        # 设置目标选择下拉框
        choose_list = ['全部']
        target_names = [configuration.names[id] + '_' + str(index) for index, id in enumerate(self.cls_list)]
        # object_list = sorted(set(self.cls_list))
        # for each in object_list:
        #     choose_list.append(configuration.CH_names[each])
        choose_list = choose_list + target_names

        self.ui.Combox.clear()
        self.ui.Combox.addItems(choose_list)

        if target_nums >= 1:
            self.ui.type_lb.setText(configuration.CH_names[self.cls_list[0]])
            self.ui.lb_conf.setText(str(self.conf_list[0]))
            #   默认显示第一个目标框坐标
            #   设置坐标位置值
            self.ui.lb_xmin.setText(str(self.loc[0][0]))
            self.ui.lb_ymin.setText(str(self.loc[0][1]))
            self.ui.lb_xmax.setText(str(self.loc[0][2]))
            self.ui.lb_ymax.setText(str(self.loc[0][3]))
        else:
            self.ui.type_lb.setText('')
            self.ui.lb_conf.setText('')
            self.ui.lb_xmin.setText('')
            self.ui.lb_ymin.setText('')
            self.ui.lb_xmax.setText('')
            self.ui.lb_ymax.setText('')

        # # 删除表格所有行
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()
        self.tabel_info_show(self.loc, self.cls_list, self.conf_list, path=self.my_path)

    def detect_imgs(self):
        if self.cap:
            # 打开图片前关闭摄像头
            self.video_stop()
            self.open_camera = False
            self.ui.CamlineEdit.setText('摄像头未开启')
            self.cap = None
        directory = QFileDialog.getExistingDirectory(self,
                                                     "选取文件夹",
                                                     "./")  # 起始路径
        if not directory:
            return
        self.my_path = directory
        img_suffix = ['jpg', 'png', 'jpeg', 'bmp']
        for file_name in os.listdir(directory):
            full_path = os.path.join(directory, file_name)
            if os.path.isfile(full_path) and file_name.split('.')[-1].lower() in img_suffix:
                # self.ui.Combox.setDisabled(False)
                img_path = full_path
                self.my_img = tools.img_cvread(img_path)
                # 目标检测
                t1 = time.time()
                self.results = self.model(img_path, conf=self.conf, iou=self.iou)[0]
                t2 = time.time()
                take_time = '{:.3f} s'.format(t2 - t1)
                self.ui.time_lb.setText(take_time)

                loc = self.results.boxes.xyxy.tolist()
                self.loc = [list(map(int, e)) for e in loc]
                cls_list = self.results.boxes.cls.tolist()
                self.cls_list = [int(i) for i in cls_list]
                self.conf_list = self.results.boxes.conf.tolist()
                self.conf_list = ['%.2f %%' % (each * 100) for each in self.conf_list]

                now_img = self.results.plot()

                self.draw_img = now_img

                # 获取类别数量
                for cls in self.cls_list:
                    cl = configuration.CH_names[cls]
                    if cl in Common.common.class_count:
                        Common.common.class_count[cl] += 1
                    else:
                        Common.common.class_count[cl] = 1
                # 获取缩放后的图片尺寸
                self.img_width, self.img_height = self.get_resize_size(now_img)
                resize_cvimg = cv2.resize(now_img, (self.img_width, self.img_height))
                pix_img = tools.cvimg_to_qpiximg(resize_cvimg)
                self.ui.label_show.setPixmap(pix_img)
                self.ui.label_show.setAlignment(Qt.AlignCenter)
                # 设置路径显示
                #self.ui.PiclineEdit.setText(img_path)

                # 目标数目
                target_nums = len(self.cls_list)
                self.ui.label_nums.setText(str(target_nums))

                # 设置目标选择下拉框
                choose_list = ['全部']
                target_names = [configuration.names[id] + '_' + str(index) for index, id in enumerate(self.cls_list)]
                choose_list = choose_list + target_names

                self.ui.Combox.clear()
                self.ui.Combox.addItems(choose_list)
                self.ui.FilelineEdit.setText(self.my_path)

                if target_nums >= 1:
                    self.ui.type_lb.setText(configuration.CH_names[self.cls_list[0]])
                    self.ui.lb_conf.setText(str(self.conf_list[0]))
                    #   默认显示第一个目标框坐标
                    #   设置坐标位置值
                    self.ui.lb_xmin.setText(str(self.loc[0][0]))
                    self.ui.lb_ymin.setText(str(self.loc[0][1]))
                    self.ui.lb_xmax.setText(str(self.loc[0][2]))
                    self.ui.lb_ymax.setText(str(self.loc[0][3]))
                else:
                    self.ui.type_lb.setText('')
                    self.ui.lb_conf.setText('')
                    self.ui.lb_xmin.setText('')
                    self.ui.lb_ymin.setText('')
                    self.ui.lb_xmax.setText('')
                    self.ui.lb_ymax.setText('')

                # # 删除表格所有行
                # self.ui.tableWidget.setRowCount(0)
                # self.ui.tableWidget.clearContents()
                self.tabel_info_show(self.loc, self.cls_list, self.conf_list, path=img_path)
                self.ui.tableWidget.scrollToBottom()
                QApplication.processEvents()  # 刷新页面

    def draw_rect_and_tabel(self, results, img):
        now_img = img.copy()
        loc = results.boxes.xyxy.tolist()
        self.loc = [list(map(int, e)) for e in loc]
        cls_list = results.boxes.cls.tolist()
        self.cls_list = [int(i) for i in cls_list]
        self.conf_list = results.boxes.conf.tolist()
        self.conf_list = ['%.2f %%' % (each * 100) for each in self.conf_list]

        for loacation, type_id, conf in zip(self.loc, self.cls_list, self.conf_list):
            type_id = int(type_id)
            color = self.colors(int(type_id), True)
            # cv2.rectangle(now_img, (int(x1), int(y1)), (int(x2), int(y2)), colors(int(type_id), True), 3)
            now_img = tools.drawRectBox(now_img, loacation, configuration.CH_names[type_id], self.fontC, color)

        # 获取缩放后的图片尺寸
        self.img_width, self.img_height = self.get_resize_size(now_img)
        resize_cvimg = cv2.resize(now_img, (self.img_width, self.img_height))
        pix_img = tools.cvimg_to_qpiximg(resize_cvimg)
        self.ui.label_show.setPixmap(pix_img)
        self.ui.label_show.setAlignment(Qt.AlignCenter)
        # 设置路径显示
        #self.ui.PiclineEdit.setText(self.my_path)

        # 目标数目
        target_nums = len(self.cls_list)
        self.ui.label_nums.setText(str(target_nums))
        if target_nums >= 1:
            self.ui.type_lb.setText(configuration.CH_names[self.cls_list[0]])
            self.ui.lb_conf.setText(str(self.conf_list[0]))
            self.ui.lb_xmin.setText(str(self.loc[0][0]))
            self.ui.lb_ymin.setText(str(self.loc[0][1]))
            self.ui.lb_xmax.setText(str(self.loc[0][2]))
            self.ui.lb_ymax.setText(str(self.loc[0][3]))
        else:
            self.ui.type_lb.setText('')
            self.ui.lb_conf.setText('')
            self.ui.lb_xmin.setText('')
            self.ui.lb_ymin.setText('')
            self.ui.lb_xmax.setText('')
            self.ui.lb_ymax.setText('')

        # 删除表格所有行
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()
        self.tabel_info_show(self.loc, self.cls_list, self.conf_list, path=self.my_path)
        return now_img

    def Combox_change(self):
        com_text = self.ui.Combox.currentText()
        if com_text == '全部':
            cur_box = self.loc
            cur_img = self.results.plot()
            self.ui.type_lb.setText(configuration.CH_names[self.cls_list[0]])
            self.ui.lb_conf.setText(str(self.conf_list[0]))
        else:
            index = int(com_text.split('_')[-1])
            cur_box = [self.loc[index]]
            cur_img = self.results[index].plot()
            self.ui.type_lb.setText(configuration.CH_names[self.cls_list[index]])
            self.ui.lb_conf.setText(str(self.conf_list[index]))

        # 设置坐标位置值
        self.ui.lb_xmin.setText(str(cur_box[0][0]))
        self.ui.lb_ymin.setText(str(cur_box[0][1]))
        self.ui.lb_xmax.setText(str(cur_box[0][2]))
        self.ui.lb_ymax.setText(str(cur_box[0][3]))

        resize_cvimg = cv2.resize(cur_img, (self.img_width, self.img_height))
        pix_img = tools.cvimg_to_qpiximg(resize_cvimg)
        self.ui.label_show.clear()
        self.ui.label_show.setPixmap(pix_img)
        self.ui.label_show.setAlignment(Qt.AlignCenter)

    def get_video_path(self):
        file_path, _ = QFileDialog.getOpenFileName(None, '打开视频', './', "Image files (*.avi *.mp4 *.wmv *.mkv)")
        if not file_path:
            return None
        self.my_path = file_path
        self.ui.VideolineEdit.setText(file_path)
        return file_path

    def video_start(self):
        # 删除表格所有行
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()

        # 清空下拉框
        self.ui.Combox.clear()

        # 定时器开启，每隔一段时间，读取一帧
        self.timer_camera.start(1)
        self.timer_camera.timeout.connect(self.open_frame)

    def tabel_info_show(self, locations, clses, confs, path=None):
        path = path
        for location, cls, conf in zip(locations, clses, confs):
            row_count = self.ui.tableWidget.rowCount()  # 返回当前行数(尾部)
            self.ui.tableWidget.insertRow(row_count)  # 尾部插入一行
            item_id = QTableWidgetItem(str(row_count + 1))  # 序号
            item_id.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中
            item_path = QTableWidgetItem(str(path))  # 路径
            # item_path.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            item_cls = QTableWidgetItem(str(configuration.CH_names[cls]))
            item_cls.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中

            item_conf = QTableWidgetItem(str(conf))
            item_conf.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中

            item_location = QTableWidgetItem(str(location))  # 目标框位置
            # item_location.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中

            self.ui.tableWidget.setItem(row_count, 0, item_id)
            self.ui.tableWidget.setItem(row_count, 1, item_path)
            self.ui.tableWidget.setItem(row_count, 2, item_cls)
            self.ui.tableWidget.setItem(row_count, 3, item_conf)
            self.ui.tableWidget.setItem(row_count, 4, item_location)
        self.ui.tableWidget.scrollToBottom()

    def video_stop(self):
        self.cap.release()
        self.timer_camera.stop()
        # self.timer_info.stop()

    def open_frame(self):
        ret, now_img = self.cap.read()
        if ret:
            # 目标检测
            t1 = time.time()
            results = self.model(now_img, conf=self.conf, iou=self.iou)[0]
            t2 = time.time()
            take_time = '{:.3f} s'.format(t2 - t1)
            self.ui.time_lb.setText(take_time)

            loc = results.boxes.xyxy.tolist()
            self.loc = [list(map(int, e)) for e in loc]
            cls_list = results.boxes.cls.tolist()
            self.cls_list = [int(i) for i in cls_list]
            self.conf_list = results.boxes.conf.tolist()
            self.conf_list = ['%.2f %%' % (each * 100) for each in self.conf_list]

            now_img = results.plot()

            # 获取类别数量
            for cls in self.cls_list:
                cl = configuration.CH_names[cls]
                if cl in Common.common.class_count:
                    Common.common.class_count[cl] += 1
                else:
                    Common.common.class_count[cl] = 1

            # 获取缩放后的图片尺寸
            self.img_width, self.img_height = self.get_resize_size(now_img)
            resize_cvimg = cv2.resize(now_img, (self.img_width, self.img_height))
            pix_img = tools.cvimg_to_qpiximg(resize_cvimg)
            self.ui.label_show.setPixmap(pix_img)
            self.ui.label_show.setAlignment(Qt.AlignCenter)

            # 目标数目
            target_nums = len(self.cls_list)
            self.ui.label_nums.setText(str(target_nums))

            # 设置目标选择下拉框
            choose_list = ['全部']
            target_names = [configuration.names[id] + '_' + str(index) for index, id in enumerate(self.cls_list)]
            # object_list = sorted(set(self.cls_list))
            # for each in object_list:
            #     choose_list.append(configuration.CH_names[each])
            choose_list = choose_list + target_names

            self.ui.Combox.clear()
            self.ui.Combox.addItems(choose_list)

            if target_nums >= 1:
                self.ui.type_lb.setText(configuration.CH_names[self.cls_list[0]])
                self.ui.lb_conf.setText(str(self.conf_list[0]))
                #   默认显示第一个目标框坐标
                #   设置坐标位置值
                self.ui.lb_xmin.setText(str(self.loc[0][0]))
                self.ui.lb_ymin.setText(str(self.loc[0][1]))
                self.ui.lb_xmax.setText(str(self.loc[0][2]))
                self.ui.lb_ymax.setText(str(self.loc[0][3]))
            else:
                self.ui.lb_ymax.setText('')
                self.ui.lb_ymin.setText('')
                self.ui.lb_xmax.setText('')
                self.ui.type_lb.setText('')
                self.ui.lb_conf.setText('')
                self.ui.lb_xmin.setText('')


            # 删除表格所有行
            # self.ui.tableWidget.setRowCount(0)
            # self.ui.tableWidget.clearContents()
            self.tabel_info_show(self.loc, self.cls_list, self.conf_list, path=self.my_path)

        else:
            self.cap.release()
            self.timer_camera.stop()

    def video_show(self):
        if self.open_camera:
            self.open_camera = False
            self.ui.CamlineEdit.setText('摄像头未开启')

        video_path = self.get_video_path()
        if not video_path:
            return None
        self.cap = cv2.VideoCapture(video_path)
        self.video_start()
        self.ui.Combox.setDisabled(True)

    def camera_show(self):
        self.open_camera = not self.open_camera
        if self.open_camera:
            self.ui.CamlineEdit.setText('摄像头开启')
            self.cap = cv2.VideoCapture(0)
            self.video_start()
            self.ui.Combox.setDisabled(True)
        else:
            self.ui.CamlineEdit.setText('摄像头未开启')
            self.ui.label_show.setText('')
            if self.cap:
                self.cap.release()
                cv2.destroyAllWindows()
            self.ui.label_show.clear()

    def get_resize_size(self, img):
        _img = img.copy()
        img_height, img_width, depth = _img.shape
        ratio = img_width / img_height
        if ratio >= self.display_width / self.display_height:
            self.img_width = self.display_width
            self.img_height = int(self.img_width / ratio)
        else:
            self.img_height = self.display_height
            self.img_width = int(self.img_height * ratio)
        return self.img_width, self.img_height

    def save(self):
        if self.cap is None and not self.my_path:
            QMessageBox.about(self, '提示', '当前没有可保存信息，请先打开图片或视频！')
            return

        if self.open_camera:
            QMessageBox.about(self, '提示', '摄像头视频无法保存!')
            return

        if self.cap:
            res = QMessageBox.information(self, '提示', '保存视频检测结果可能需要较长时间，请确认是否继续保存？', QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)
            if res == QMessageBox.Yes:
                self.video_stop()
                com_text = self.ui.Combox.currentText()
                self.btn2Thread_object = btn2Thread(self.my_path, self.model, com_text, self.conf, self.iou)
                self.btn2Thread_object.start()
                self.btn2Thread_object.update_ui_signal.connect(self.update_process_bar)
            else:
                return
        else:
            if os.path.isfile(self.my_path):
                fileName = os.path.basename(self.my_path)
                name, end_name = fileName.rsplit(".", 1)
                save_name = name + '-Detected_result.' + end_name
                save_img_path = os.path.join(configuration.save_path, save_name)
                # 保存图片
                cv2.imwrite(save_img_path, self.draw_img)
                QMessageBox.about(self, '提示', '图片保存成功!\n文件路径:{}'.format(save_img_path))
            else:
                img_suffix = ['jpg', 'png', 'jpeg', 'bmp']
                for file_name in os.listdir(self.my_path):
                    full_path = os.path.join(self.my_path, file_name)
                    if os.path.isfile(full_path) and file_name.split('.')[-1].lower() in img_suffix:
                        name, end_name = file_name.rsplit(".", 1)
                        save_name = name + '-Detected_result.' + end_name
                        save_img_path = os.path.join(configuration.save_path, save_name)
                        results = self.model(full_path, conf=self.conf, iou=self.iou)[0]
                        now_img = results.plot()
                        # 保存图片
                        cv2.imwrite(save_img_path, now_img)

                QMessageBox.about(self, '提示', '图片保存成功!\n文件路径:{}'.format(configuration.save_path))

    def update_process_bar(self, cun_num, total):
        if cun_num == 1:
            self.progress_bar = ProgressBar(self)
            self.progress_bar.show()
        if cun_num >= total:
            self.progress_bar.close()
            QMessageBox.about(self, '提示', '视频保存成功!\n文件在{}目录下'.format(configuration.save_path))
            return
        if self.progress_bar.isVisible() is False:
            # 点击取消保存时，终止进程
            self.btn2Thread_object.stop()
            return
        value = int(cun_num / total * 100)
        self.progress_bar.setValue(cun_num, total, value)
        QApplication.processEvents()

    def next(self):
        self.close()
        self.win1 = last.MainWindow1()
        self.win1.show()


class btn2Thread(QThread):
    """
    进行检测后的视频保存
    """
    # 声明一个信号
    update_ui_signal = pyqtSignal(int, int)

    def __init__(self, path, model, com_text, conf, iou):
        super(btn2Thread, self).__init__()
        self.my_path = path
        self.model = model
        self.com_text = com_text
        self.conf = conf
        self.iou = iou
        # 用于绘制不同颜色矩形框
        self.colors = tools.Colors()
        self.is_running = True  # 标志位，表示线程是否正在运行

    def run(self):
        # VideoCapture方法是cv2库提供的读取视频方法
        cap = cv2.VideoCapture(self.my_path)
        # 设置需要保存视频的格式“xvid”
        # 该参数是MPEG-4编码类型，文件名后缀为.avi
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # 设置视频帧频
        fps = cap.get(cv2.CAP_PROP_FPS)
        # 设置视频大小
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        # VideoWriter方法是cv2库提供的保存视频方法
        # 按照设置的格式来out输出
        fileName = os.path.basename(self.my_path)
        name, end_name = fileName.split('.')
        save_name = name + '_detect_result.avi'
        save_video_path = os.path.join(configuration.save_path, save_name)
        out = cv2.VideoWriter(save_video_path, fourcc, fps, size)

        prop = cv2.CAP_PROP_FRAME_COUNT
        total = int(cap.get(prop))
        print("[INFO] 视频总帧数：{}".format(total))
        cun_num = 0

        # 确定视频打开并循环读取
        while (cap.isOpened() and self.is_running):
            cun_num += 1
            print('当前第{}帧，总帧数{}'.format(cun_num, total))
            # 逐帧读取，ret返回布尔值
            # 参数ret为True 或者False,代表有没有读取到图片
            # frame表示截取到一帧的图片
            ret, frame = cap.read()
            if ret == True:
                # 检测
                results = self.model(frame, conf=self.conf, iou=self.iou)[0]
                frame = results.plot()
                out.write(frame)
                self.update_ui_signal.emit(cun_num, total)
            else:
                break
        # 释放资源
        cap.release()
        out.release()

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
