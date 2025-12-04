import io
import os
import re
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from reportlab.pdfgen import canvas

from libs.file_collector_with_ignore.file_collector_with_ignore import collect_files
from mypass import collect_pnpcfgs, get_effective_config
from pnpconfig_parser import PnpConfigParser
from utils import *


PAGE_WIDTH, PAGE_HEIGHT = mm_to_px(A4_WIDTH_MM), mm_to_px(A4_HEIGHT_MM)

# ａ４纸两边的白边
PAGE_MARGIN_WIDTH_MM = 25 / 2.0
PAGE_MARGIN_HEIGHT_MM = 30 / 2.0  # 实际大小是 35 为了做卡片妥协了

MAX_CARD_WIDTH_MM = float(defaults["MAX_CARD_WIDTH_MM"])
MAX_CARD_HEIGHT_MM = float(defaults["MAX_CARD_HEIGHT_MM"])
CARD_WIDTH_MM = float(defaults["CARD_WIDTH_MM"])
CARD_HEIGHT_MM = float(defaults["CARD_HEIGHT_MM"])
REPEAT = defaults["REPEAT"]
REPEAT_COUNT = defaults["REPEAT_COUNT"]
WRITE_TEXT = defaults["WRITE_TEXT"]
ROWS = defaults["ROWS"]
COLS = defaults["COLS"]
RIGHT_TO_LEFT = defaults["RIGHT_TO_LEFT"]
EFFECTIVE_REPEAT_COUNT = REPEAT_COUNT

BLEED_H_MM = 0
BLEED_V_MM = 0
CARD_WIDTH = 0
CARD_HEIGHT = 0
MAX_COLS = 0
MAX_ROWS = 0
MARGIN_X = 0
MARGIN_Y = 0


def refresh_layout_metrics():
    global CARD_WIDTH_MM, CARD_HEIGHT_MM, MAX_CARD_WIDTH_MM, MAX_CARD_HEIGHT_MM
    global BLEED_H_MM, BLEED_V_MM, CARD_WIDTH, CARD_HEIGHT
    global MAX_COLS, MAX_ROWS, MARGIN_X, MARGIN_Y

    if CARD_WIDTH_MM == -1 or CARD_HEIGHT_MM == -1:
        CARD_WIDTH_MM = MAX_CARD_WIDTH_MM
        CARD_HEIGHT_MM = MAX_CARD_HEIGHT_MM

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

    CARD_WIDTH = mm_to_px(CARD_WIDTH_MM + 2 * BLEED_H_MM)
    CARD_HEIGHT = mm_to_px(CARD_HEIGHT_MM + 2 * BLEED_V_MM)

    MAX_COLS = COLS
    MAX_ROWS = ROWS
    if ROWS == -1 or COLS == -1:
        MAX_COLS = max(1, (PAGE_WIDTH - mm_to_px(PAGE_MARGIN_WIDTH_MM * 2.0)) // CARD_WIDTH)
        MAX_ROWS = max(1, (PAGE_HEIGHT - mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)) // CARD_HEIGHT)

    MARGIN_X = (PAGE_WIDTH - MAX_COLS * CARD_WIDTH) // 2
    MARGIN_Y = (PAGE_HEIGHT - MAX_ROWS * CARD_HEIGHT) // 2


refresh_layout_metrics()

# Prepare images and PDF output
def prepare_image_files(file_paths):
    image_files = []
    for file_path in file_paths:
        match = re.search(r'x(\d+)', file_path)
        repeat_count = int(match.group(1)) if match else 1
        image_files.extend([file_path] * repeat_count)

    if not image_files:
        return image_files, 0

    if REPEAT:
        tiles_per_page = max(1, MAX_COLS * MAX_ROWS)
        repeat_count = max(1, tiles_per_page // len(image_files))
        image_files = image_files * repeat_count
    else:
        repeat_count = REPEAT_COUNT

    return image_files, repeat_count


def create_pdf(image_files, output_pdf, cfg_map, base_dir, right_to_left=False):
    if not image_files:
        print("没有找到可用的图片，终止生成 PDF。")
        return

    c = canvas.Canvas(output_pdf, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    x, y = MARGIN_X, PAGE_HEIGHT - MARGIN_Y - CARD_HEIGHT  # Start at top-left within margins
    col_count = 0
    row_count = 0

    if right_to_left:
        x = PAGE_WIDTH - MARGIN_X - CARD_WIDTH  # Start at top-right within margins

    for image_path in image_files:
        print(f"Processing image: {image_path}")
        with Image.open(image_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            img_with_bleed = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255, 255))
            cfg = get_effective_config(image_path, cfg_map, base_dir)

            w = mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_WIDTH_MM"]).group(1)))
            h = mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_HEIGHT_MM"]).group(1)))
            img_resized = img.resize((w, h), Image.LANCZOS)

            img_with_bleed.paste(img_resized, ((CARD_WIDTH - w)//2, (CARD_HEIGHT - h)//2), img_resized)

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
    print(f"PDF saved as {output_pdf}")

def add_page_numbers(input_pdf):
    doc = fitz.open(input_pdf)
    total_pages = doc.page_count

    if WRITE_TEXT:
        for i in range(total_pages):
            page = doc[i]
            if RIGHT_TO_LEFT:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -r2l -rpt{EFFECTIVE_REPEAT_COUNT} -p{i + 1}/{total_pages}"
            else:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -l2r -rpt{EFFECTIVE_REPEAT_COUNT} -p{i + 1}/{total_pages}"
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

def render_pdf_pages(pdf_path, zoom_x=1, zoom_y=1, rotation_angle=0, target_size=None):
    pdf = fitz.open(pdf_path)
    matrix = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
    try:
        for page in pdf:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_data = pix.tobytes()
            img = Image.open(io.BytesIO(img_data))
            if target_size:
                img = img.resize(target_size, Image.LANCZOS)
            yield img
    finally:
        pdf.close()


def save_images_as_pdf(images, output_path, success_message=None):
    rgb_images = [img.convert("RGB") for img in images]
    if not rgb_images:
        print("没有可以保存的页面图像。")
        return

    first_image, *rest = rgb_images
    first_image.save(output_path, save_all=True, append_images=rest, quality=100)
    add_page_numbers(output_path)
    if success_message:
        print(success_message)


def pdf_image(pdfPath, zoom_x, zoom_y, rotation_angle):
    a4_target_size = (2480, 3508)  # Resize to A4 size
    mark = Image.open("./res/mark-line.png").resize(a4_target_size, Image.LANCZOS)
    marked_images = []

    for img in render_pdf_pages(pdfPath, zoom_x, zoom_y, rotation_angle, a4_target_size):
        img = img.convert("RGBA")
        img.paste(mark, (0, 0), mark)
        marked_images.append(img)

    output_path = pdfPath[0: -4] + "-marked-line.pdf"
    save_images_as_pdf(marked_images, output_path, f"Marked PDF saved as {output_path}")


def overlay_image_on_pdf(pdf_path: str, overlay_image_path: str):
    """
    将 overlay_image_path 按每页大小拉伸后，铺满 pdf_path 每一页。
    输出文件名: 原pdf名 + '-' + 图片主名 + '.pdf'
    """
    overlay_img = Image.open(overlay_image_path).convert("RGBA")

    out_imgs = []
    for base_img in render_pdf_pages(pdf_path):
        base_img = base_img.convert("RGBA")
        stretched = overlay_img.resize(base_img.size, Image.LANCZOS)
        base_img.paste(stretched, (0, 0), stretched)
        out_imgs.append(base_img)

    if out_imgs:
        stem = Path(overlay_image_path).stem
        output_path = Path(pdf_path).with_stem(Path(pdf_path).stem + f"-{stem}")
        save_images_as_pdf(out_imgs, output_path, f"PDF 已保存：{output_path}")


def main(provided_path=""):
    global MAX_CARD_WIDTH_MM, MAX_CARD_HEIGHT_MM, CARD_WIDTH_MM, CARD_HEIGHT_MM
    global REPEAT, REPEAT_COUNT, WRITE_TEXT, ROWS, COLS, RIGHT_TO_LEFT, EFFECTIVE_REPEAT_COUNT

    imgs_path = provided_path.strip().strip('"') if provided_path else ""
    if not imgs_path:
        imgs_path = input("Enter the path to the images folder: ").strip().strip('"')

    base_dir = imgs_path
    print(f"\n📁 扫描路径: {base_dir}\n")

    files = collect_files(base_dir)
    print(f"共找到 {len(files)} 个文件")

    cfg_map = collect_pnpcfgs(base_dir)
    print(f"共解析 {len(cfg_map)} 个配置目录\n")

    config_parser = PnpConfigParser(imgs_path)
    config_parser.parse()

    MAX_CARD_WIDTH_MM = float(config_parser.get("MAX_CARD_WIDTH_MM", defaults["MAX_CARD_WIDTH_MM"]))
    MAX_CARD_HEIGHT_MM = float(config_parser.get("MAX_CARD_HEIGHT_MM", defaults["MAX_CARD_HEIGHT_MM"]))
    CARD_WIDTH_MM = float(config_parser.get("CARD_WIDTH_MM", defaults["CARD_WIDTH_MM"]))
    CARD_HEIGHT_MM = float(config_parser.get("CARD_HEIGHT_MM", defaults["CARD_HEIGHT_MM"]))
    REPEAT = config_parser.get("REPEAT", defaults["REPEAT"])
    REPEAT_COUNT = config_parser.get("REPEAT_COUNT", defaults["REPEAT_COUNT"])
    WRITE_TEXT = config_parser.get("WRITE_TEXT", defaults["WRITE_TEXT"])
    ROWS = config_parser.get("ROWS", defaults["ROWS"])
    COLS = config_parser.get("COLS", defaults["COLS"])
    RIGHT_TO_LEFT = config_parser.get("RIGHT_TO_LEFT", defaults["RIGHT_TO_LEFT"])

    refresh_layout_metrics()

    image_files, EFFECTIVE_REPEAT_COUNT = prepare_image_files(files)
    output_pdf = os.path.join(base_dir, "output.pdf")
    create_pdf(image_files, output_pdf, cfg_map, base_dir, RIGHT_TO_LEFT)
    pdf_image(output_pdf, 2, 2, 0)
    # overlay_image_on_pdf(output_pdf, "./res/marker-415_635.png")


if __name__ == "__main__":
    main()