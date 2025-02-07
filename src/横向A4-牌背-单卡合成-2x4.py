import os
import PIL.Image as Image
from PIL import ImageDraw, ImageFont
import math

from 边缘外扩 import *
from 平均划线 import *


# 配置
IMAGES_PATH = './res/pic-int/'  # 图片集地址
IMAGE_SAVE_PATH = './res/pic-int/'  # 图片转换后文件夹目录
IMAGE_SAVE_NAME = '发明家2x5-A4打印'
# ----图片的长宽比
IMAGE_SIZE_WIDTH_FACTOR = 53               # 郎中闯江湖
IMAGE_SIZE_LENGTH_FACTOR = 86
X_LEGNTH = 673
Y_LEGHTN = 1050
IMAGE_SIZE_WIDTH_FACTOR = X_LEGNTH         # 王权骰铸
IMAGE_SIZE_LENGTH_FACTOR = Y_LEGHTN

IMAGE_SIZE_WIDTH_FACTOR = 1635    # 宝石商人
IMAGE_SIZE_LENGTH_FACTOR = 2211

IMAGE_SIZE_WIDTH_FACTOR = 850    # 长
IMAGE_SIZE_LENGTH_FACTOR = 1122  # 高


# 常数表
print('A4-300dpi 是 2480×3508')
A4_LEGHTH = 3508
A4_WIDTH = 2480

A4_LEGHTH = 2480
A4_WIDTH = 3508

padding=5
左右间距 = 80
IMAGE_ROW = 2  # 图片间隔，也就是合并成一张图后，一共有几行
IMAGE_COLUMN = 5  # 图片间隔，也就是合并成一张图后，一共有几列

# 拉伸比例适配 A4
IMAGE_SIZE_WIDTH = (A4_LEGHTH - 左右间距 * 2 - padding * IMAGE_COLUMN + padding) / IMAGE_COLUMN
IMAGE_SIZE_LENGTH = IMAGE_SIZE_WIDTH / IMAGE_SIZE_WIDTH_FACTOR * IMAGE_SIZE_LENGTH_FACTOR
IMAGE_SIZE_WIDTH = int(IMAGE_SIZE_WIDTH)
IMAGE_SIZE_LENGTH = int(IMAGE_SIZE_LENGTH)

head_padding = (A4_WIDTH - IMAGE_SIZE_LENGTH * IMAGE_ROW - padding * IMAGE_ROW + padding) / 2
head_padding = int(head_padding)


# 获取图片集地址下的所有图片名称

def process2x4_with_back(input_path, output_path, back_img):
    # 行数、列数
    row = 2
    col = 4
    # 图片格式
    IMAGES_FORMAT = ['.jpg', '.JPG','.png']

    image_names = [name for name in os.listdir(input_path) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    if len(image_names) == 0:
        return

    img = Image.open(input_path + image_names[0])
    w, h = img.size
    print(str(w) + ', ' + str(h))

    output_img_count = len(image_names) * 2 / (col * row)
    output_img_count = math.ceil(output_img_count)

    index = 0
    for i in range(0, output_img_count):
        output_image = Image.new('RGB', (w * col + padding * (col - 1), h * row + padding * row), 'white')  # 创建一个新图
        for y in range(0, row):
            for x in range(0, col):
                if index >= len(image_names):
                    break
                if y == 0: # 奇数行粘贴牌背
                    output_image.paste(back_img.resize((w,h), Image.LANCZOS), (x * (w + padding), y * (h + padding)))
                    continue
                from_image = Image.open(input_path + image_names[index])
                output_image.paste(from_image, (x * (w + padding), y * (h + padding)))

                index += 1
        output_image.save(output_path + str(i) + '.jpg', quality=100)  # 保存新图


if __name__ == '__main__':

    # 牌背
    back_img = Image.open('res/pic/牌背/炸弹猫.png')
    process2x4_with_back('res/pic/圆角/', 'res/pic/横向2x4/', back_img)


    IMAGES_PATH = 'res/pic/横向2x4/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    IMAGES_OUTPUT_PATH = './res/pic/边缘外扩/横向A4/'
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]

    # 缩放
    # -----------------------------
    scale_factor = 0.87
    index = 0
    print("------------- 开始缩放 --------------")
    print(f"缩放比例: {scale_factor}")
    for name in image_names:
        input_image = Image.open(IMAGES_PATH + name)
        output_image = edge_extension_a4_landscape(input_image, scale_factor)
        output_image.save(IMAGES_OUTPUT_PATH + str(index) + '.jpg', quality=100)
        index += 1


    IMAGES_PATH = './res/pic/边缘外扩/横向A4/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    for name in image_names:
        input_img_path = IMAGES_PATH + name
        # 不填写最后两个margin值表示居中对齐
        draw_line(input_img_path, 'res/pic/平均划线/炸弹猫/' + name, 2, 4, 491, 322)
