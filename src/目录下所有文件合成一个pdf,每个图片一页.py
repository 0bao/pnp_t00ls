from PIL import Image
import os


def convert_images_to_pdf(input_dir):
    image_paths = []

    # 遍历目录获取所有图片
    for root, _, files in os.walk(input_dir):
        for file in sorted(files):  # 按名称排序
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff')):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        print("未找到任何图片！")
        return

    # A4 纸张尺寸（以像素计，假设 300 DPI）
    a4_width, a4_height = 2480, 3508  # 210x297 mm at 300 dpi

    pdf_images = []
    for img_path in image_paths:
        with Image.open(img_path) as img:
            img = img.convert("RGB")  # 转换为 RGB 格式（避免错误）
            img.thumbnail((a4_width, a4_height))  # 缩放以适应 A4 纸张
            pdf_images.append(img)

    # 生成 PDF 文件路径（保存在输入目录下）
    output_pdf = os.path.join(input_dir, "output.pdf")

    # 保存 PDF
    pdf_images[0].save(output_pdf, save_all=True, append_images=pdf_images[1:])
    print(f"PDF 已成功保存到: {output_pdf}")


# 获取用户输入的图片目录
input_directory = input("请输入包含图片的目录路径: ").strip()

if os.path.isdir(input_directory):
    convert_images_to_pdf(input_directory)
else:
    print("错误: 目录不存在！")
