# opencv读取图片是按 BGR 的顺序
import cv2 as cv
import os
import time
import imutils
from PIL import Image
import torch

OUTPUT_SLIDES_DIR = f"./output"

FRAME_RATE = 3                   # no.of frames per second that needs to be processed, fewer the count faster the speed
WARMUP = FRAME_RATE              # initial number of frames to be skipped
FGBG_HISTORY = FRAME_RATE * 15   # no.of frames in background object
VAR_THRESHOLD = 14               # Threshold on the squared Mahalanobis distance between the pixel and the model to decide whether a pixel is well described by the background model.
DETECT_SHADOWS = False            # If true, the algorithm will detect shadows and mark them.
MIN_PERCENT = 0.1                # min % of diff between foreground and background to detect if motion has stopped
MAX_PERCENT = 3                  # max % of diff between foreground and background to detect if frame is still in motion

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# 读取视频帧
def get_frames(video_path):
    '''A fucntion to return the frames from a video located at video_path
    this function skips frames as defined in FRAME_RATE'''
    
    
    # open a pointer to the video file initialize the width and height of the frame
    vs = cv.VideoCapture(video_path)
    if not vs.isOpened():
        raise Exception(f'unable to open file {video_path}')


    total_frames = vs.get(cv.CAP_PROP_FRAME_COUNT)
    frame_time = 0
    frame_count = 0

    # loop over the frames of the video
    while True:
        vs.set(cv.CAP_PROP_POS_MSEC, frame_time * 1000)    # move frame to a timestamp
        frame_time += 1/FRAME_RATE

        (_, frame) = vs.read()
        # if the frame is None, then we have reached the end of the video file
        if frame is None:
            break

        frame_count += 1
        yield frame_count, frame_time, frame

    vs.release()

# 使用前景和背景相关知识判断前景运动从而判断幻灯片是否进行了切换
def no_Button(video_path, output_folder_screenshot_path):
    ''''''
    # Initialize fgbg a Background object with Parameters
    # history = The number of frames history that effects the background subtractor
    # varThreshold = Threshold on the squared Mahalanobis distance between the pixel and the model to decide whether a pixel is well described by the background model. This parameter does not affect the background update.
    # detectShadows = If true, the algorithm will detect shadows and mark them. It decreases the speed a bit, so if you do not need this feature, set the parameter to false.

    fgbg = cv.createBackgroundSubtractorMOG2(history=FGBG_HISTORY, varThreshold=VAR_THRESHOLD,detectShadows=DETECT_SHADOWS)

    
    captured = False
    start_time = time.time()
    (W, H) = (None, None)
    screenshoots_count = 0
    for frame_count, frame_time, frame in get_frames(video_path):
        orig = frame.copy() # clone the original frame (so we can save it later), 
        frame = imutils.resize(frame, width=600) # resize the frame
        mask = fgbg.apply(frame) # apply the background subtractor

        #mask_path = os.path.join(output_folder_screenshot_path, f"mask_{frame_count:03}.png")
        #cv.imwrite(mask_path, mask)


        if W is None or H is None:
            (H, W) = mask.shape[:2]

        p_diff = (cv.countNonZero(mask) / float(W * H)) * 100 # 统计前景像素在当前帧中所占的百分比

        path = os.path.dirname(output_folder_screenshot_path)
        path = os.path.join(path, "img")
        if not os.path.exists(path):
            os.makedirs(path)

        if p_diff < MIN_PERCENT and not captured and frame_count > WARMUP:
            captured = True
            filename = f"{screenshoots_count:03}_{round(frame_time/60, 2)}.png"

            path = os.path.join(path, filename)
            
            cv.imwrite(path, orig)
            screenshoots_count += 1
        elif captured and p_diff >= MAX_PERCENT:
            captured = False
    print(f'{screenshoots_count} screenshots Captured!')
    print(f'Time taken {time.time()-start_time}s')
    return 

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf_from_folder(folder_path, output_pdf):
    # 获取文件夹中的所有图片文件路径
    image_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.jpg', '.jpeg', '.png'))]

    # 创建 PDF
    c = canvas.Canvas(output_pdf, pagesize=letter)
    for image_path in image_paths: 
        with Image.open(image_path) as img:
            width, height = img.size
            c.setPageSize((width, height))  # 设置 PDF 页面尺寸为图片尺寸
            c.drawImage(image_path, 0, 0, width=width, height=height)
            c.showPage()  # 创建新页面
    c.save()

if __name__=="__main__":
    no_Button("", "")
    create_pdf_from_folder("", "")

