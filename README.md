# 幻灯片转PDF系统

## 项目介绍

### 使用场景说明

本系统能够处理特定场景下的教学视频，将视频中出现的幻灯片转存为PDF。这里的特殊场景有两类：

1. 第一类视频，幻灯片铺满整个屏幕，不出现演讲者

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211414946.png)

2. 第二类视频，幻灯片铺满整个画面，但是会有演讲者

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211416245.png)

### 文件说明

- `has_speaker` 文件夹中存放的是有演讲者的教学视频
- `no_speaker` 文件夹中存放的是无演讲者的教学视频
- `has_speaker.py` 文件存放的是处理有演讲者视频的代码
- `no_speaker.py` 文件存放的是处理无演讲者视频的代码
- `main.py` 文件用于实现UI界面
- `yolov8n-seg.pt` 是YOLOv8分割模型文件

## 运行环境

Python环境，主要使用到的库有：

- PyQt5
- torch（GPU加速）
- cv2
- os
- time
- imutils
- PIL
- ultralytics（YOLOv8）
- reportlab

## 原理说明

![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211428904.png)

下面是两类视频的处理过程

1. 无演讲者视频
   - 使用背景减除与前景检测技术进行关键帧提取
   - 将关键帧（图片）转存为PDF
2. 有演讲者视频
   - 先通过YOLOv8分割演讲者（获取人物轮廓坐标）
   - 使用图像处理技术（膨胀 + inpaint修复）抠除人物
   - 使用背景减除与前景检测技术进行关键帧提取
   - 将关键帧（图片）转存为PDF

## 系统演示

1. 运行`main.py`文件

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211432965.png)

2. 点击菜单栏的文件图标，上传视频文件，并确定PDF的保存位置

3. 若上传的是无演讲者视频，则点击“无演讲者”按钮，主窗口中会显示保存下来的关键帧

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211435781.png)

4. 若上传的是有演讲者视频，点击“有演讲者”按钮，主窗口首先会显示一个进度条表示抠除人像的进度，抠除人像完成后同上

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211439070.png)

5. 处理完成后会有弹窗显示

   ![](https://cdn.jsdelivr.net/gh/hxt616/PicGo@main/img/202405211440004.png)