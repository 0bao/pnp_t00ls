from PIL import Image
import os


def process_images_in_directory(directory):
    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')

    for filename in os.listdir(directory):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(directory, filename)

            try:
                # 打开图片
                with Image.open(file_path) as img:
                    # 原始大小
                    original_size = img.size
                    original_width, original_height = original_size

                    # 计算放大后的新大小
                    new_width = int(original_width * 1.14)
                    new_height = int(original_height * 1.09)

                    # 放大图片
                    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

                    # 计算裁剪的区域
                    left = (new_width - original_width) // 2
                    upper = (new_height - original_height) // 2
                    right = left + original_width
                    lower = upper + original_height

                    # 裁剪回原始大小
                    img_cropped = img_resized.crop((left, upper, right, lower))

                    # 保存并覆盖原文件
                    img_cropped.save(file_path)
                    print(f"处理完成: {file_path}")

            except Exception as e:
                print(f"处理图片时出错: {file_path}, 错误: {e}")


# 调用函数
directory_path = input("请输入图片所在的目录路径: ")
process_images_in_directory(directory_path)
