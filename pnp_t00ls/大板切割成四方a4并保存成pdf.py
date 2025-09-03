import os
from PIL import Image
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from 平均切图 import *

# ------------------ 设置参数 ------------------
DPI = 300
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
MARGIN_MM = 7.5  # 每边留白 7.5mm

PRINTABLE_WIDTH_MM  = A4_WIDTH_MM - 2 * MARGIN_MM
PRINTABLE_HEIGHT_MM = A4_HEIGHT_MM - 2 * MARGIN_MM

# ------------------ 主程序 ------------------
def mm_to_px(mm_val):
    return int(mm_val / 25.4 * DPI)

def save_images_to_a4_pdf(image_list, new_width_px, new_height_px, output_dir, output_pdf_name="output.pdf"):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    a4_width, a4_height = 2480, 3508  # 300 DPI A4 尺寸，单位像素

    pages = []
    for img in image_list:
        if not isinstance(img, Image.Image):
            img = Image.open(img)

        resized_img = img.resize((new_width_px, new_height_px), Image.Resampling.LANCZOS)


        page = Image.new("RGB", (a4_width, a4_height), "white")

        x = (a4_width - new_width_px) // 2
        y = (a4_height - new_height_px) // 2

        page.paste(resized_img, (x, y))

        pages.append(page)

    output_pdf_path = os.path.join(output_dir, output_pdf_name)
    pages[0].save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=pages[1:])
    print(f"PDF保存到: {output_pdf_path}")

# 使用示例
# save_images_to_a4_pdf(image_list, 1000, 1400, "./pdf_outputs", "my_images.pdf")



def cut_and_export(image_path):
    # 打开图像
    image = Image.open(image_path)
    img_name = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = os.path.dirname(image_path)
    os.makedirs(output_dir, exist_ok=True)

    W_px, H_px = image.size

    # 计算缩放宽度（贴近A4纸长边减去留白）
    target_height_mm = PRINTABLE_HEIGHT_MM

    scale = target_height_mm / (H_px / DPI * 25.4)  # mm / mm
    target_width_mm = W_px / DPI * 25.4 * scale
    cut = int(target_width_mm / PRINTABLE_WIDTH_MM) + 1

    new_height_px = mm_to_px(target_height_mm)
    new_width_px = mm_to_px(target_width_mm / cut)

    image_list = cut_image(image, cut, 1)  # 列 行

    save_images_to_a4_pdf(image_list, new_width_px, new_height_px, output_dir, output_pdf_name="output.pdf")

    # 每页可打印高度（px）


    print(f"\n✅ 切割完成，参数如下：")
    print(f"原图尺寸：{W_px} x {H_px} px")
    print(f"缩放后尺寸：{new_width_px} x {new_height_px} px")
    print(f"总页数：{cut}")
    print(f"输出目录：{output_dir}\n")



# ------------------ 运行 ------------------
if __name__ == "__main__":
    image_path = input("请输入图片路径（支持jpg/png/webp等）: ").strip().strip('"')
    if not os.path.isfile(image_path):
        print("❌ 文件不存在，请检查路径。")
    else:
        cut_and_export(image_path)
