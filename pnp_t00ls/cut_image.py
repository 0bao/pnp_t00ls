import os
from PIL import Image


def crop(input_img, pos):
    output_img = input_img.crop(pos)  # (left, upper, right, lower)
    return output_img


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


def save_images(image_list, output_dir, start_number=0, write_mode='覆盖'):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    elif write_mode == '如果存在文件夹则跳过':
        return 0

    saved_count = 0  # 计数已保存的图片

    for index, image in enumerate(image_list, start=start_number):
        # 检查是否是纯黑色图片
        if image.getbbox() is None:
            print(f"Skipping empty (solid color) image: {index:05d}.png")
            continue

        # 检查是否是全透明图片
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            extrema = image.getextrema()  # 获取通道极值
            if len(extrema) == 4 and extrema[3][1] == 0:  # 透明通道最大值为 0 说明完全透明
                print(f"Skipping fully transparent image: {index:05d}.png")
                continue

        image.save(f"{output_dir}/{index:05d}.png", quality=100)
        saved_count += 1  # 成功保存一张图片

    return saved_count


def process_image(img_path, col, row, start_number=0, write_mode='覆盖', custom_dir=''):
    if img_path[0] == '"' and img_path[-1] == '"':
        img_path = img_path[1:-1]

    if img_path[-4:].lower() in ['.jpg', '.png']:
        output_dir = img_path[0:-4]

        if custom_dir:  # If a custom directory is provided, use it instead
            output_dir = custom_dir

        image = Image.open(img_path)
        image_list = cut_image(image, col, row)
        saved_count = save_images(image_list, output_dir, start_number, write_mode)
        print(f"Images saved to: {output_dir}, total saved: {saved_count}")
        return saved_count  # Return the number of images successfully saved
    else:
        print("Invalid image format. Only .jpg and .png are supported.")
        return 0

