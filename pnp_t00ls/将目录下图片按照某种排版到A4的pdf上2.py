import os
import re
import uuid

import fitz          # PyMuPDF
from PIL import Image
import io
from pathlib import Path

from config import *
from utils import mm_to_px

from reportlab.pdfgen import canvas

from libs.file_collector_with_ignore.file_collector_with_ignore import collect_files
from pnpconfig_parser import PnpConfigParser

from mypass import collect_pnpcfgs, get_effective_config

def set_global_config(input_dir):
    global DPI
    global A4_WIDTH_MM
    global A4_HEIGHT_MM
    global PAGE_WIDTH
    global PAGE_HEIGHT
    global MAX_CARD_WIDTH_MM
    global MAX_CARD_HEIGHT_MM
    global CARD_WIDTH_MM
    global CARD_HEIGHT_MM
    global REPEAT
    global REPEAT_COUNT
    global WRITE_TEXT
    global ROWS
    global COLS
    global RIGHT_TO_LEFT
    global PAGE_MARGIN_WIDTH_MM
    global PAGE_MARGIN_HEIGHT_MM
    global BLEED_H_MM
    global BLEED_V_MM
    global CARD_WIDTH
    global CARD_HEIGHT
    global MAX_COLS
    global MAX_ROWS
    global MARGIN_X
    global MARGIN_Y

    PAGE_WIDTH = mm_to_px(A4_WIDTH_MM)
    PAGE_HEIGHT = mm_to_px(A4_HEIGHT_MM)

    print(f"\n📁 扫描路径: {input_dir}\n")

    # 📂 获取配置路径
    config = PnpConfigParser(input_dir)
    config.parse()

    # 🎯 解析最终配置
    MAX_CARD_WIDTH_MM = float(config.get("MAX_CARD_WIDTH_MM", defaults["MAX_CARD_WIDTH_MM"]))
    MAX_CARD_HEIGHT_MM = float(config.get("MAX_CARD_HEIGHT_MM", defaults["MAX_CARD_HEIGHT_MM"]))
    CARD_WIDTH_MM = float(config.get("CARD_WIDTH_MM", defaults["CARD_WIDTH_MM"]))
    CARD_HEIGHT_MM = float(config.get("CARD_HEIGHT_MM", defaults["CARD_HEIGHT_MM"]))
    REPEAT = config.get("REPEAT", defaults["REPEAT"])
    REPEAT_COUNT = config.get("REPEAT_COUNT", defaults["REPEAT_COUNT"])
    WRITE_TEXT = config.get("WRITE_TEXT", defaults["WRITE_TEXT"])
    ROWS = config.get("ROWS", defaults["ROWS"])
    COLS = config.get("COLS", defaults["COLS"])
    RIGHT_TO_LEFT = config.get("RIGHT_TO_LEFT", defaults["RIGHT_TO_LEFT"])

    # ａ４纸两边的白边
    PAGE_MARGIN_WIDTH_MM = 25 / 2.0
    PAGE_MARGIN_HEIGHT_MM = 30 / 2.0  # 实际大小是 35 为了做卡片妥协了

    if CARD_WIDTH_MM == -1 or CARD_HEIGHT_MM == -1:
        CARD_WIDTH_MM = MAX_CARD_WIDTH_MM
        CARD_HEIGHT_MM = MAX_CARD_HEIGHT_MM

    # Adjust CARD_WIDTH_MM and CARD_HEIGHT_MM to fit within MAX_CARD dimensions if necessary
    if MAX_CARD_WIDTH_MM < CARD_WIDTH_MM:
        print(
            f"MAX_CARD_WIDTH_MM ({MAX_CARD_WIDTH_MM}) is smaller than CARD_WIDTH_MM ({CARD_WIDTH_MM}). "
            f"Adjusting CARD_WIDTH_MM to {MAX_CARD_WIDTH_MM}."
        )
        CARD_WIDTH_MM = MAX_CARD_WIDTH_MM

    if MAX_CARD_HEIGHT_MM < CARD_HEIGHT_MM:
        print(
            f"MAX_CARD_HEIGHT_MM ({MAX_CARD_HEIGHT_MM}) is smaller than CARD_HEIGHT_MM ({CARD_HEIGHT_MM}). "
            f"Adjusting CARD_HEIGHT_MM to {MAX_CARD_HEIGHT_MM}."
        )
        CARD_HEIGHT_MM = MAX_CARD_HEIGHT_MM

    BLEED_H_MM = (MAX_CARD_WIDTH_MM - CARD_WIDTH_MM) / 2.0
    BLEED_V_MM = (MAX_CARD_HEIGHT_MM - CARD_HEIGHT_MM) / 2.0

    CARD_WIDTH = mm_to_px(CARD_WIDTH_MM + 2 * BLEED_H_MM)  # Width with bleed
    CARD_HEIGHT = mm_to_px(CARD_HEIGHT_MM + 2 * BLEED_V_MM)  # Height with bleed

    MAX_COLS = COLS
    MAX_ROWS = ROWS
    if ROWS == -1 or COLS == -1:
        # Calculate rows and columns dynamically based on A4 page size
        MAX_COLS = (PAGE_WIDTH - mm_to_px(PAGE_MARGIN_WIDTH_MM * 2.0)) // CARD_WIDTH
        i = mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)
        MAX_ROWS = (PAGE_HEIGHT - mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)) // CARD_HEIGHT

    # Calculate margin for centering
    MARGIN_X = (PAGE_WIDTH - MAX_COLS * CARD_WIDTH) // 2
    MARGIN_Y = (PAGE_HEIGHT - MAX_ROWS * CARD_HEIGHT) // 2

def layout_images_to_pdf(image_paths, output_pdf_path, input_dir, cfg_map, right_to_left=False ):
    c = canvas.Canvas(output_pdf_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    x, y = MARGIN_X, PAGE_HEIGHT - MARGIN_Y - CARD_HEIGHT  # Start at top-left within margins

    col_count = 0
    row_count = 0

    if right_to_left:
        x = PAGE_WIDTH - MARGIN_X - CARD_WIDTH  # Start at top-right within margins

    for path in image_paths:
        print(f"Processing image: {path}")
        img = Image.open(path)

        # Convert image to RGBA (if not already), to preserve transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create a white background to paste the image on
        img_with_bleed = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255, 255))

        cfg = get_effective_config(path, cfg_map, input_dir)

        # Resize the image, maintaining the transparency (alpha channel)
        w,h = mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_WIDTH_MM"]).group(1))), \
                                  mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_HEIGHT_MM"]).group(1)))

        img_resized = img.resize((w,h), Image.LANCZOS)


        # Paste the resized image onto the white background
        img_with_bleed.paste(img_resized, ((CARD_WIDTH - w)//2,(CARD_HEIGHT - h)//2), img_resized)


        # Save resized image with bleed
        temp_filename = f"temp_image_{uuid.uuid4().hex}.png"
        img_with_bleed.save(temp_filename)

        c.drawImage(temp_filename, x, y, width=CARD_WIDTH, height=CARD_HEIGHT)
        os.remove(temp_filename)  # Remove the temporary image after adding to PDF

        if right_to_left:
            x -= CARD_WIDTH  # Move left
        else:
            x += CARD_WIDTH  # Move right

        col_count += 1
        if col_count == MAX_COLS:
            col_count = 0
            row_count += 1
            x = PAGE_WIDTH - MARGIN_X - CARD_WIDTH if right_to_left else MARGIN_X
            y -= CARD_HEIGHT

        if row_count == MAX_ROWS:
            c.showPage()
            row_count = 0
            x = PAGE_WIDTH - MARGIN_X - CARD_WIDTH if right_to_left else MARGIN_X
            y = PAGE_HEIGHT - MARGIN_Y - CARD_HEIGHT

    c.save()
    print(f"PDF saved as {output_pdf_path}")

def add_page_numbers(input_pdf):
    doc = fitz.open(input_pdf)
    total_pages = doc.page_count

    if WRITE_TEXT:
        for i in range(total_pages):
            page = doc[i]
            if RIGHT_TO_LEFT:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -r2l -rpt{REPEAT_COUNT} -p{i + 1}/{total_pages}"
            else:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -l2r -rpt{REPEAT_COUNT} -p{i + 1}/{total_pages}"
            page_width, page_height = page.rect.width, page.rect.height
            font_size = page_height * 0.01
            font = "helv"
            font_obj = fitz.Font(font)
            text_length = font_obj.text_length(page_number, font_size)
            x_position = (page_width - text_length) / 2
            y_position = page_height * 0.04

            page.insert_text(
                fitz.Point(x_position, y_position),
                page_number,
                fontsize=font_size,
                fontname=font,
                color=(0, 0, 0)
            )

    doc.saveIncr()
    doc.close()

def pdf_image(pdfPath):
    pdf = fitz.open(pdfPath)
    mark = Image.open("./res/mark-line.png").resize((PAGE_WIDTH, PAGE_HEIGHT), Image.LANCZOS)
    out_imgs = []

    for pg in range(pdf.page_count):
        page = pdf[pg]
        pix = page.get_pixmap(matrix=fitz.Matrix(DPI / 72., DPI / 72.), alpha=False)
        img_data = pix.tobytes()
        img = Image.open(io.BytesIO(img_data)).resize((PAGE_WIDTH, PAGE_HEIGHT), Image.LANCZOS)
        img.paste(mark, (0, 0), mark)
        out_imgs.append(img)

    pdf.close()

    out_imgs = [img.convert("RGB") for img in out_imgs]

    if out_imgs:
        first_image = out_imgs[0]
        first_image.save(pdfPath[0: -4] + "-marked-line.pdf", save_all=True, append_images=out_imgs[1:], quality=100)

    add_page_numbers(pdfPath[0: -4] + "-marked-line.pdf")
    print(f"Marked PDF saved as {pdfPath[0: -4]}-marked-line.pdf")

def overlay_image_on_pdf(pdf_path: str, overlay_image_path: str):
    """
    将 overlay_image_path 按每页大小拉伸后，铺满 pdf_path 每一页。
    输出文件名: 原pdf名 + '-' + 图片主名 + '.pdf'
    """
    pdf = fitz.open(pdf_path)
    overlay_img = Image.open(overlay_image_path).convert("RGBA")

    out_imgs = []
    for page in pdf:
        pix = page.get_pixmap(alpha=False)               # 原始尺寸渲染
        img_data = pix.tobytes()
        base_img = Image.open(io.BytesIO(img_data)).convert("RGBA")

        # 拉伸叠加图到与当前页一样大小
        stretched = overlay_img.resize(base_img.size, Image.LANCZOS)

        # 覆盖整页
        base_img.paste(stretched, (0, 0), stretched)

        out_imgs.append(base_img.convert("RGB"))

    pdf.close()

    if out_imgs:
        stem = Path(overlay_image_path).stem
        output_path = Path(pdf_path).with_stem(Path(pdf_path).stem + f"-{stem}")
        out_imgs[0].save(
            output_path,
            save_all=True,
            append_images=out_imgs[1:],
            quality=100
        )

        add_page_numbers(output_path)
        print(f"PDF 已保存：{output_path}")

def main():
    input_dir = ""

    if input_dir == "":
        input_dir = input("Enter the path to the images folder: ").strip().strip('"')

    set_global_config(input_dir)

    cfg_map = collect_pnpcfgs(input_dir)
    print(f"共解析 {len(cfg_map)} 个配置目录\n")

    filtered_files = collect_files(input_dir)

    for img in filtered_files:
        print(img)
    # 在此进行处理，可以按需要修改
    image_files = []


    for file_path in filtered_files:
        match = re.search(r'x(\d+)', file_path)
        repeat_count = int(match.group(1)) if match else 1
        image_files.extend([file_path] * repeat_count)

    if REPEAT:
        global REPEAT_COUNT
        REPEAT_COUNT = (MAX_COLS * MAX_ROWS) //len(image_files)
        image_files = image_files * REPEAT_COUNT


    output_pdf = os.path.join(input_dir, "output.pdf")
    layout_images_to_pdf(filtered_files, output_pdf, input_dir, cfg_map, RIGHT_TO_LEFT)
    pdf_image(output_pdf)



if __name__ == "__main__":
    main()