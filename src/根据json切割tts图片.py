import os

from disoolve_tts_json import get_unique_nodes
from cut_image import process_image
import shutil


import os
from PIL import Image


def find_image_with_extension(base_path):
    # 常见图片扩展名列表
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']

    # 遍历所有扩展名并尝试找到有效的图片文件
    for ext in extensions:
        file_path = base_path + ext
        if os.path.exists(file_path):
            # 验证文件是否是一个有效图像
            try:
                with Image.open(file_path) as img:
                    img.verify()  # 验证文件是否为有效图像
                return file_path  # 返回完整的路径
            except (IOError, SyntaxError):
                continue  # 如果图像验证失败，继续尝试其他扩展名

    # 如果没有找到有效的图片文件，返回空字符串
    return ""


# 让用户输入 JSON 文件路径并调用方法
file_path = input("请输入 JSON 文件路径（放在 Workshop 目录下）: ").replace('"', '')

# Get the directory of the file
directory = os.path.dirname(file_path)

# Use os.path.join to safely build the path for the 'Images' directory
img_dir = os.path.abspath(os.path.join(directory, "..", "Images"))

unique_nodes = get_unique_nodes(file_path)

# 遍历并打印结果
if unique_nodes:
    print("\n解析出的唯一节点信息：")
    start_number = 0;
    for i, node in enumerate(unique_nodes, start=1):
        print(f"\n节点 {i}:")
        print(node)
        img_path = os.path.abspath(os.path.join(img_dir, node['FaceName']))
        print(img_path)
        img_path = find_image_with_extension(img_path)
        if img_path != "":
            print(img_path)
            col = node['NumWidth']
            row = node['NumHeight']
            count = process_image(img_path, col, row, start_number, '如果存在文件夹则跳过')
            start_number += count
        if not node['BackIsHidden']:
            dir_name = os.path.splitext(img_path)[0]
            # 创建 back 目录的完整路径
            back_dir = os.path.join(dir_name, "back")
            # 创建目录（如果不存在）
            os.makedirs(back_dir, exist_ok=True)
            back_img_path = find_image_with_extension(os.path.abspath(os.path.join(img_dir, node['BackName'])))
            if not node['UniqueBack']:
                shutil.copy(back_img_path, back_dir)
            else:
                process_image(back_img_path, col, row, start_number, '覆盖', back_dir)

                front_dir = os.path.join(dir_name, "front")
                os.makedirs(front_dir, exist_ok=True)
                # 遍历源目录下的所有文件（不递归子目录）
                for filename in os.listdir(dir_name):
                    source_path = os.path.join(dir_name, filename)

                    # 确保是文件而不是目录，并且是图片文件
                    if os.path.isfile(source_path) and filename.lower().endswith(
                            ('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        dest_path = os.path.join(front_dir, filename)

                        # 如果目标路径文件已经存在，跳过
                        if os.path.exists(dest_path):
                            continue

                        # 剪切文件到目标目录
                        shutil.move(source_path, dest_path)








