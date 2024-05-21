from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from moviepy.editor import VideoFileClip
import torch
import functools

import sys
sys.path.append(r"E:\\Desktop\\Code")  # 导入函数
from no_speaker_button import *
from has_speaker_button import *

import shutil

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, processing_function, video_path, output_pdf_path):
        super().__init__()
        self.processing_function = processing_function
        self.video_path = video_path
        self.output_pdf_path = output_pdf_path

    def run(self):
        self.processing_function(self.video_path, self.output_pdf_path)
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 视频文件地址
        self.video_path = None

        # 窗口名称
        self.setWindowTitle("Video To PDF")

        # 创建主窗口中央的部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建垂直布局
        main_layout = QVBoxLayout(central_widget)

        # 创建菜单栏
        self.create_menu()

        # 创建框
        self.thumbnail_label = QLabel()
        self.thumbnail_frame = self.create_thumbnail_frame(self.thumbnail_label)
        self.center_label_text(self.thumbnail_frame, "请先上传视频文件")

        # 将框添加到布局并居中显示
        main_layout.addStretch(1)
        main_layout.addWidget(self.thumbnail_frame, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)

        # 创建按钮
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        self.has_speaker_button = QPushButton("有演讲者")
        self.no_speaker_button = QPushButton("无演讲者")
        
        # 设置按钮样式
        button_style = """
        QPushButton {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            
            font-size: 16px;
            margin: 4px 2px;
            
            border-radius: 10px;
        }

        QPushButton:hover {
            background-color: #45a049; /* Darker Green */
        }
        """

        self.has_speaker_button.setStyleSheet(button_style)
        self.no_speaker_button.setStyleSheet(button_style)

        # 缩短按钮大小
        self.has_speaker_button.setMaximumWidth(120)
        self.no_speaker_button.setMaximumWidth(120)

        button_layout.addWidget(self.has_speaker_button)
        button_layout.addWidget(self.no_speaker_button)


        # # 将按钮的点击事件连接到槽函数
        # self.has_speaker_button.clicked.connect(has_Button(self.video_path, "output_pdf.pdf"))
        # self.no_speaker_button.clicked.connect(no_Button(self.video_path, "output_pdf.pdf"))

        # 将菜单栏、按钮添加到主布局中
        main_layout.addWidget(button_widget)

        # 设置视频缩略图标签的大小
        self.thumbnail_label.setFixedWidth(600)
        self.thumbnail_label.setFixedHeight(400)

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_image_folder)
        


    def create_menu(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单项
        file_menu = menu_bar.addMenu("文件")
        file_menu.setIcon(QIcon("open.png"))
        file_menu.setTitle(" 文件")

        # 添加上传视频菜单项，并设置图标
        open_action = QAction("上传视频", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

    def open_file_dialog(self):
        # 打开文件对话框
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("视频文件 (*.mp4 *.avi *.mkv)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            # 在这里处理选择的文件
            print("选择的文件:", selected_files)
            # 在此加载并显示视频文件的缩略图
            if selected_files:
                self.video_path  = selected_files[0]
                thumbnail = self.generate_thumbnail(self.video_path)
                if thumbnail:
                    self.thumbnail_label.setPixmap(thumbnail)
                    self.thumbnail_label.setText("")  # 清除标题
                else:
                    self.thumbnail_label.setText("无法生成缩略图")
                 # 初始化时连接按钮
                self.connect_buttons()

    def create_thumbnail_frame(self, label):
        # 创建框架
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(label)  # 将标签添加到框架中
        return frame

    def generate_thumbnail(self, video_path):
        try:
            # 使用 MoviePy 打开视频文件
            clip = VideoFileClip(video_path)

            # 提取视频的第一帧作为缩略图
            frame = clip.get_frame(0)

            # 将帧转换为 QPixmap
            thumbnail = QPixmap.fromImage(QImage(frame.tobytes(), frame.shape[1], frame.shape[0], QImage.Format_RGB888))

            # 缩放缩略图以适应标签大小
            thumbnail = thumbnail.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio)

            # 返回缩略图
            return thumbnail
        except Exception as e:
            # 如果提取失败，返回 None，并打印错误信息
            print("提取视频缩略图失败:", e)
            return None

    def center_label_text(self, frame, text):
        # 使标签中的文本居中显示
        # 使标签中的文本居中显示
        label = frame.findChild(QLabel)
        if label:
            label.setAlignment(Qt.AlignCenter)
            label.setText(text)
            # 设置字体
            font = QFont("Arial", 12)  # 选择字体和大小
            font.setWeight(QFont.Bold)  # 设置字体加粗
            label.setFont(font)

    def top_label_text(self, frame, text):
        label = frame.findChild(QLabel)
        if label:
            label.setAlignment(Qt.AlignTop|Qt.AlignCenter)
            label.setText(text)
            # 设置字体
            font = QFont("Arial", 12)  # 选择字体和大小
            font.setWeight(QFont.Bold)  # 设置字体加粗
            label.setFont(font)

    # 点击事件
    # 在主窗口类中添加一个方法用于选择输出 PDF 路径
    def select_output_pdf_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        output_pdf_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        return output_pdf_path

    # 将按钮的点击事件连接到槽函数
    def connect_buttons(self):
        if self.video_path:
            output_pdf_path = self.select_output_pdf_path()
            if output_pdf_path:
                self.has_speaker_button.clicked.connect(lambda: self.handle_button_click(has_Button, output_pdf_path))
                self.no_speaker_button.clicked.connect(lambda: self.handle_button_click(no_Button, output_pdf_path))
                # self.has_speaker_button.clicked.connect(lambda: has_Button(self.video_path, output_pdf_path))
                # self.no_speaker_button.clicked.connect(lambda: no_Button(self.video_path, output_pdf_path))
        else:
            print("请先上传视频文件")

    def handle_button_click(self, processing_function, output_pdf_path):

        #self.top_label_text(self.thumbnail_frame, "处理中...")
        print("处理中...")

        self.timer.start(500)  # 设置定时器触发时间间隔为500毫秒

        # 选取图片文件夹路径
        path = os.path.dirname(output_pdf_path)
        img_path = os.path.join(path, "img")
        self.image_folder_path = img_path
        

        # 创建并启动工作线程
        self.worker_thread = WorkerThread(processing_function, self.video_path, output_pdf_path)

        if processing_function.__name__ == "has_Button":
            # 创建进度条
            self.center_progress_bar(self.thumbnail_frame)
            # 进度条
            self.worker_thread.video_processor = video_processor  # 在WorkerThread实例中创建VideoProcessor实例
            self.worker_thread.video_processor.progress_updated.connect(self.update_progress_bar)

            self.center_label_text(self.thumbnail_frame, "抠除人像中...")

        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()
        

    def on_worker_finished(self):
        # 在工作线程完成后进行清理和更新
        path = os.path.dirname(self.worker_thread.output_pdf_path)
        img_path = os.path.join(path, "img")
        print(img_path)
        create_pdf_from_folder(img_path, self.worker_thread.output_pdf_path)
        shutil.rmtree(img_path)
        QMessageBox.information(self, "已完成", "处理已完成！", QMessageBox.Ok)
        #self.processing_label.hide() # 隐藏处理中
        self.center_label_text(self.thumbnail_frame, "请先上传视频文件")
        # 断开按钮的点击连接，不然会重复创建进程进而报错
        self.has_speaker_button.clicked.disconnect()
        self.no_speaker_button.clicked.disconnect()

        # 停止定时器
        self.timer.stop()

        # 清除进度条
        if hasattr(self, 'progress_bar'):
            self.progress_bar.deleteLater()
            del self.progress_bar

    def center_progress_bar(self, frame):
        # 创建进度条并添加到垂直布局中
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        frame.layout().addWidget(self.progress_bar)

    # 槽函数，用于接收处理进度信号并更新进度条
    def update_progress_bar(self, progress):
        #print("Received progress update:", progress)
        if progress==99:
            progress = 100
        self.progress_bar.setValue(progress)

    def check_image_folder(self):
        # 若img文件夹不存咋，则跳过
        if not os.path.exists(self.image_folder_path):
            if hasattr(self, 'processing_label'):
                self.processing_label.deleteLater()  # 删除 QLabel 对象
                del self.processing_label  # 删除属性引用
            # self.processing_label.hide()
            return

        # 创建显示 "处理中" 文本的标签
        if not hasattr(self, 'processing_label'):
            # 清除进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.deleteLater()
                del self.progress_bar
                
            self.processing_label = QLabel("处理中...")
            self.processing_label.setAlignment(Qt.AlignCenter)
            layout = self.thumbnail_frame.layout()
            layout.addWidget(self.processing_label)

            # 创建 QFont 对象，并设置字体和大小
            font = QFont("Arial", 12)
            # 设置字体加粗
            font.setWeight(QFont.Bold)
            # 将字体应用到标签上
            self.processing_label.setFont(font)


        # 检查临时文件夹中是否有新的图片文件
        image_files = [f for f in os.listdir(self.image_folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if image_files:
            # 取最新的图片文件
            latest_image = sorted(image_files, key=lambda x: os.path.getmtime(os.path.join(self.image_folder_path, x)))[-1]
            image_path = os.path.join(self.image_folder_path, latest_image)

            # 加载图片并缩放适应标签的大小
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio)

            # 更新显示最新的图片
            self.thumbnail_label.setPixmap(pixmap)
            self.thumbnail_label.setText("")  # 清除标题

            # # 更新显示最新的图片
            # image = QImage(image_path)
            # pixmap = QPixmap.fromImage(image)
            # if not pixmap.isNull():
            #     self.thumbnail_label.setPixmap(pixmap)
            #     self.thumbnail_label.setText("")  # 清除标题

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
