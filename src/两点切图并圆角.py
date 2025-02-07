import PIL.Image as Image
from PIL import ImageDraw, ImageFont

import os



# (left, upper, right, lower)
def crop(input_img, pos):
    output_img = input_img.crop(pos)  # (left, upper, right, lower)
    return output_img



from PIL import Image,ImageDraw
import os

def circle_corner(img, ratio):  #把原图片变成圆角，这个函数是从网上找的，原址 https://www.pyget.cn/p/185266
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """
    # 画圆（用于分离4个角）
    radii = int(img.size[0] * ratio)

    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形
    # 原图
    img = img.convert("RGBA")
    w, h = img.size
    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()
    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见

    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img,(0, 0), mask=img)

    return background


if __name__ ==  '__main__' :

    img_path = input()
    if (img_path[0] == '"' and img_path[-1] == '"'):
        img_path = img_path[1:-1]
    if (img_path[-1] == '\\' or img_path[-1] == '/'):
        img_path = img_path[0:-1]

    IMAGES_OUTPUT_PATH = img_path + '\\两点切分'
    try:
        os.mkdir(IMAGES_OUTPUT_PATH)
    except:
        pass
    print("保存目录：" + IMAGES_OUTPUT_PATH)


    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']  # 图片格式
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(img_path) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]

    image_names.sort()
    index = 0
    for name in image_names:
        input_path = img_path + '\\' + name
        input_image = Image.open(input_path)
        output_img = crop(input_image, (0, 0, 1860, 2825))   # (left, upper, right, lower)
        str_num = str('%03d' % index)
        output_path = IMAGES_OUTPUT_PATH + '\\' + str_num + '.png'
        output_img.save(output_path, quality=100)
        index += 1



    print("开始圆角")
    imgs_path = img_path

    try:
        os.mkdir(imgs_path + '\\圆角')
    except:
        pass

    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']
    image_names = [name for name in os.listdir(imgs_path + '\\两点切分') for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]

    image_names.sort()
    index = 0
    for name in image_names:
        # 不填写最后两个margin值表示居中对齐
        input_image = Image.open(imgs_path + '\\两点切分\\' + name)
        out_img = circle_corner(input_image, 0.08)
        out_img.save(imgs_path + '/圆角/' + '%03d' % index + '.png', quality=100)
        index += 1

