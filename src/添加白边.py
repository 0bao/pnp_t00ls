import os
import random
import shutil
import csv
from PIL import Image, ExifTags

def add_white_edge(infilename, outfilename, aspect):
    inImg = Image.open(infilename)
    # print(inImg.size)
    """
    对于手机、相机等设备拍摄的照片，由于手持方向的不同，拍出来的照片可能是旋转0°、90°、180°和270°。
    即使在电脑上利用软件将其转正，他们的exif信息中还是会保留方位信息。
    在用PIL读取这些图像时，读取的是原始数据，
    也就是说，即使电脑屏幕上显示是正常的照片，用PIL读进来后，
    也可能是旋转的图像，并且图片的size也可能与屏幕上的不一样。
    对于这种情况，可以利用PIL读取exif中的orientation信息，
    然后根据这个信息将图片转正后，再进行后续操作，具体如下。
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation': break
        exif = dict(inImg._getexif().items())
        if exif[orientation] == 3:
            inImg = inImg.rotate(180, expand=True)
        elif exif[orientation] == 6:
            inImg = inImg.rotate(270, expand=True)
        elif exif[orientation] == 8:
            inImg = inImg.rotate(90, expand=True)
    except:
        pass
    width, height = inImg.size  # 获取原图像的水平方向尺寸和垂直方向尺寸。
    # print(inImg.size)

    if (height / width) == aspect:
        inImg.save(outfilename)
    elif height / width > aspect:
        out_width = math.ceil(height / aspect)
        out_height = height
        bgImg = Image.new("RGB", (out_width, out_height), (255, 255, 255))
        bgImg.paste(inImg, (round((out_width - width) / 2), 0))
        bgImg.resize((out_width, out_height), Image.LANCZOS).save(outfilename)
    elif height / width < aspect:
        out_width = width
        out_height = math.ceil(width * aspect)
        bgImg: Image.Image = Image.new("RGB", (out_width, out_height), (255, 255, 255))
        bgImg.paste(inImg, (0, round((out_height - height) / 2)))
        bgImg.resize((out_width, out_height), Image.LANCZOS).save(outfilename)