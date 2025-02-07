import os
from PIL import Image, ImageDraw


def apply_round_corners(image, radius):
    """对图片进行圆角处理，圆角区域为白色"""
    # 创建相同大小的圆角遮罩
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255)

    # 创建一个白色背景
    white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))

    # 将圆角图像粘贴到白色背景上
    rounded = Image.composite(image, white_bg, mask)
    return rounded.convert("RGB")  # 如果需要保存为JPEG，则转换为RGB模式


def process_images(directory, radius=50):
    """递归处理目录中的所有图片并覆盖原图"""
    supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(supported_formats):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        img = img.convert("RGBA")  # 确保支持透明度
                        rounded_img = apply_round_corners(img, radius)
                        rounded_img.save(file_path)  # 覆盖原图
                        print(f"处理完成: {file_path}")
                except Exception as e:
                    print(f"处理失败: {file_path}, 错误: {e}")


if __name__ == "__main__":
    input_dir = input("请输入要处理的目录: ").strip()
    if os.path.isdir(input_dir):
        process_images(input_dir, 30)
    else:
        print("输入的路径无效，请输入有效的目录路径。")
