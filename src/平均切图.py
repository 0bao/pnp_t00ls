import os
from PIL import Image

# 两点切图
def crop(input_img, pos):
    output_img = input_img.crop(pos)  # (left, upper, right, lower)
    return output_img


# 分割图片
def cut_image(image, col, row):
    width, height = image.size
    item_width = int(width / col)
    item_height = int(height / row)
    box_list = []
    # (left, upper, right, lower)
    for j in range(0, row):
        for i in range(0, col):
            box = (i * item_width, j * item_height, (i + 1) * item_width, (j + 1) * item_height)
            box_list.append(box)
    image_list = [image.crop(box) for box in box_list]
    return image_list


# 保存分割后的图片
def save_images(image_list):
    index = 1
    for image in image_list:
        image.save(str(index) + '.jpg')
        index += 1


if __name__ == '__main__':

    img_path = input()
    if (img_path[0] == '"' and img_path[-1] == '"'):
        img_path = img_path[1:-1]

    if (img_path[-4:] == '.jpg' or img_path[-4:] == '.JPG'):
        try:
            os.mkdir(img_path[0:-4])
        except:
            print("未创建目录")
            pass
    if (img_path[-4:] == '.png' or img_path[-4:] == '.PNG'):
        try:
            os.mkdir(img_path[0:-4])
        except:
            print("未创建目录")
            pass
    print("保存目录：" + img_path[0:-4])
    w = 0
    image = Image.open(img_path)
    #image = crop(image, (0, 0, 1450, 2060)) # 去除边框
    image_list = cut_image(image, 5, 2)  # 列 行
    for image in image_list:
        image.save(img_path[0:-4] + "/" + '%03d' % w + '.png', quality = 100)
        w += 1
