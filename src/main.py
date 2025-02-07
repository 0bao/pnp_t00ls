from 圆角 import *
from 边缘外扩 import *

import os


# 边缘外扩
def fun2():
    IMAGES_PATH = './res/pic/圆角/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    IMAGES_OUTPUT_PATH = './res/pic/边缘外扩/'
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    index = 0
    for name in image_names:
        index += 1
        input_image = Image.open(IMAGES_PATH + name)
        output_image = edge_extension(input_image, 86, 86)
        output_image.save(IMAGES_OUTPUT_PATH + str(index) + '.jpg', quality=100)



def paste_four_corner(img, corner_img):
    img.paste(corner_img, (0, 0), mask=corner_img)
    img.paste(corner_img, (0, img.size[1] - corner_img.size[1]), mask=corner_img)
    img.paste(corner_img, (img.size[0] - corner_img.size[0], img.size[1] - corner_img.size[1]), mask=corner_img)
    img.paste(corner_img, (img.size[0] - corner_img.size[0], 0), mask=corner_img)
    return img

# 四角粘贴
def fun3():
    IMAGES_PATH = './res/pic/边缘外扩/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    IMAGES_OUTPUT_PATH = './res/pic/四角粘贴/'
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    corner_img = Image.open('./res/pic/三级.png')
    index = 0
    for name in image_names:
        index += 1
        input_image = Image.open(IMAGES_PATH + name)
        output_image = paste_four_corner(input_image, corner_img)
        output_image.save(IMAGES_OUTPUT_PATH + str(index) + '.jpg', quality=100)

# 圆角
def fun1():
    IMAGES_PATH = './res/pic/原图裁剪/三级/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    IMAGES_OUTPUT_PATH = './res/pic/圆角/'
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    index = 0
    for name in image_names:
        input_image = Image.open(IMAGES_PATH + name)
        output_image = circle_corner(input_image, 110)
        output_image.save(IMAGES_OUTPUT_PATH + str(index) + '.jpg', quality=100)
        index += 1

def fun5():
    IMAGES_PATH = './res/pic/3x6原图/'
    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    IMAGES_OUTPUT_PATH = './res/pic/边缘外扩/'
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    index = 0
    for name in image_names:

        input_image = Image.open(IMAGES_PATH + name)
        output_image = edge_extension_a4(input_image)
        output_image.save(IMAGES_OUTPUT_PATH + str(index) + '.jpg', quality=100)
        index += 1


if __name__ == '__main__':
    img = Image.open("D:\\Projects\\visualstudio\\rgs\Assets\\hdr\\newport_loft.hdr")
    w, h = img.size
    w /= 2
    h /= 2
    img.resize(w, h).save("D:\\Projects\\visualstudio\\rgs\Assets\\hdr\\newport_loft1.hdr")





