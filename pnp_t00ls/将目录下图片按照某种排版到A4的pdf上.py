import io
import os
import re
import tempfile
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from reportlab.pdfgen import canvas

from config import A4_HEIGHT_MM, A4_WIDTH_MM, defaults
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

# Prepare images and PDF output
def prepare_image_files(file_paths, repeat, repeat_count, max_cols, max_rows):
    image_files = []
    for file_path in file_paths:
        match = re.search(r'x(\d+)', file_path)
        repeat_count = int(match.group(1)) if match else 1
        image_files.extend([file_path] * repeat_count)

    if not image_files:
        return image_files, 0

    if repeat:
        tiles_per_page = max(1, max_cols * max_rows)
        effective_repeat = max(1, tiles_per_page // len(image_files))
        image_files = image_files * effective_repeat
    else:
        effective_repeat = repeat_count

    return image_files, effective_repeat


def create_pdf(image_files, output_pdf, cfg_map, base_dir, config_dict):
    if not image_files:
        print("没有找到可用的图片，终止生成 PDF。")
        return

    card_width = config_dict["CARD_WIDTH_PX"]
    card_height = config_dict["CARD_HEIGHT_PX"]
    max_cols = config_dict["MAX_COLS"]
    max_rows = config_dict["MAX_ROWS"]
    margin_x = config_dict["MARGIN_X"]
    margin_y = config_dict["MARGIN_Y"]
    right_to_left = config_dict["RIGHT_TO_LEFT"]

    c = canvas.Canvas(output_pdf, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    x, y = margin_x, PAGE_HEIGHT - margin_y - card_height  # Start at top-left within margins
    col_count = 0
    row_count = 0

    if right_to_left:
        x = PAGE_WIDTH - margin_x - card_width  # Start at top-right within margins

    for image_path in image_files:
        print(f"Processing image: {image_path}")
        with Image.open(image_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            img_with_bleed = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 255))
            cfg = get_effective_config(image_path, cfg_map, base_dir)

            w = mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_WIDTH_MM"]).group(1)))
            h = mm_to_px(float(re.match(r'CONST\((.+)\)', cfg["CARD_HEIGHT_MM"]).group(1)))
            img_resized = img.resize((w, h), Image.LANCZOS)

            img_with_bleed.paste(img_resized, ((card_width - w)//2, (card_height - h)//2), img_resized)

            temp_filename = f"temp_image_{uuid.uuid4().hex}.png"
            img_with_bleed.save(temp_filename)

        c.drawImage(temp_filename, x, y, width=card_width, height=card_height)
        os.remove(temp_filename)  # Remove the temporary image after adding to PDF

        if right_to_left:
            x -= card_width  # Move left
        else:
            x += card_width  # Move right

        col_count += 1
        if col_count == max_cols:
            col_count = 0
            row_count += 1
            x = PAGE_WIDTH - margin_x - card_width if right_to_left else margin_x
            y -= card_height

        if row_count == max_rows:
            c.showPage()
            row_count = 0
            x = PAGE_WIDTH - margin_x - card_width if right_to_left else margin_x
            y = PAGE_HEIGHT - margin_y - card_height

    c.save()
    print(f"PDF saved as {output_pdf}")

def add_page_numbers(input_pdf, config_dict, effective_repeat_count):
    doc = fitz.open(input_pdf)
    total_pages = doc.page_count

    write_text = config_dict["WRITE_TEXT"]
    right_to_left = config_dict["RIGHT_TO_LEFT"]
    max_card_width_mm = config_dict["MAX_CARD_WIDTH_MM"]
    max_card_height_mm = config_dict["MAX_CARD_HEIGHT_MM"]
    card_width_mm = config_dict["CARD_WIDTH_MM"]
    card_height_mm = config_dict["CARD_HEIGHT_MM"]
    max_rows = config_dict["MAX_ROWS"]
    max_cols = config_dict["MAX_COLS"]

    if write_text:
        for i in range(total_pages):
            page = doc[i]
            if right_to_left:
                page_number = (
                    f"-iw{card_width_mm} -ih{card_height_mm} "
                    f"-ow{max_card_width_mm} -oh{max_card_height_mm} "
                    f"-r{max_rows} -c{max_cols} -r2l "
                    f"-rpt{effective_repeat_count} -p{i + 1}/{total_pages}"
                )
            else:
                page_number = (
                    f"-iw{card_width_mm} -ih{card_height_mm} "
                    f"-ow{max_card_width_mm} -oh{max_card_height_mm} "
                    f"-r{max_rows} -c{max_cols} -l2r "
                    f"-rpt{effective_repeat_count} -p{i + 1}/{total_pages}"
                )
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


def save_images_as_pdf(images, output_path, config_dict, effective_repeat_count, success_message=None):
    rgb_images = [img.convert("RGB") for img in images]
    if not rgb_images:
        print("没有可以保存的页面图像。")
        return

    first_image, *rest = rgb_images
    first_image.save(output_path, save_all=True, append_images=rest, quality=100)
    add_page_numbers(output_path, config_dict, effective_repeat_count)
    if success_message:
        print(success_message)


def apply_watermark_to_pdf_pages(pdf_path, config_dict, effective_repeat_count,
                                 watermark_image_path="./res/mark-line.png",
                                 zoom_x=2, zoom_y=2, rotation_angle=0):
    """
    EN: Apply the watermark image to every page of the PDF.
    ZH: 将水印图片粘贴到 PDF 的每一页上，输出新的 PDF 文件。
    """
    a4_target_size = (2480, 3508)  # Resize to A4 size
    mark = Image.open(watermark_image_path).resize(a4_target_size, Image.LANCZOS)
    marked_images = []

    for img in render_pdf_pages(pdf_path, zoom_x, zoom_y, rotation_angle, a4_target_size):
        img = img.convert("RGBA")
        img.paste(mark, (0, 0), mark)
        marked_images.append(img)

    output_path = pdf_path[0: -4] + "-marked-line.pdf"
    save_images_as_pdf(marked_images, output_path, config_dict, effective_repeat_count,
                       f"Marked PDF saved as {output_path}")
    return output_path


def overlay_image_on_pdf(pdf_path: str, overlay_image_path: str, config_dict, effective_repeat_count):
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
        save_images_as_pdf(out_imgs, output_path, config_dict, effective_repeat_count,
                           f"PDF 已保存：{output_path}")


def load_config_and_files(provided_path=""):
    """
    EN: Load configuration, collect files, and build per-directory config map.
    ZH: 读取配置、收集文件并生成目录配置映射，返回后续所需的全部信息。
    """
    global MAX_CARD_WIDTH_MM, MAX_CARD_HEIGHT_MM, CARD_WIDTH_MM, CARD_HEIGHT_MM
    global REPEAT, REPEAT_COUNT, WRITE_TEXT, ROWS, COLS, RIGHT_TO_LEFT

    imgs_path = provided_path.strip().strip('"') if provided_path else ""
    if not imgs_path:
        imgs_path = input("Enter the path to the images folder: ").strip().strip('"')

    base_dir = imgs_path
    print(f"\n📁 扫描路径: {base_dir}\n")

    # 第一步：收集所有目标文件
    files = collect_files(base_dir)
    print(f"共找到 {len(files)} 个文件")

    # 第二步：收集并解析所有 .pnpcfg
    cfg_map = collect_pnpcfgs(base_dir)
    print(f"共解析 {len(cfg_map)} 个配置目录\n")

    # 第三步：获取并解析配置
    config_parser = PnpConfigParser(imgs_path)
    config_parser.parse()

    # 解析基础配置
    max_card_width_mm = float(config_parser.get("MAX_CARD_WIDTH_MM", defaults["MAX_CARD_WIDTH_MM"]))
    max_card_height_mm = float(config_parser.get("MAX_CARD_HEIGHT_MM", defaults["MAX_CARD_HEIGHT_MM"]))
    card_width_mm = float(config_parser.get("CARD_WIDTH_MM", defaults["CARD_WIDTH_MM"]))
    card_height_mm = float(config_parser.get("CARD_HEIGHT_MM", defaults["CARD_HEIGHT_MM"]))
    repeat = config_parser.get("REPEAT", defaults["REPEAT"])
    repeat_count = config_parser.get("REPEAT_COUNT", defaults["REPEAT_COUNT"])
    write_text = config_parser.get("WRITE_TEXT", defaults["WRITE_TEXT"])
    rows = config_parser.get("ROWS", defaults["ROWS"])
    cols = config_parser.get("COLS", defaults["COLS"])
    right_to_left = config_parser.get("RIGHT_TO_LEFT", defaults["RIGHT_TO_LEFT"])

    # 计算排版相关尺寸（不依赖全局可变变量）
    if card_width_mm == -1 or card_height_mm == -1:
        card_width_mm = max_card_width_mm
        card_height_mm = max_card_height_mm

    if max_card_width_mm < card_width_mm:
        print(
            f"MAX_CARD_WIDTH_MM ({max_card_width_mm}) is smaller than CARD_WIDTH_MM ({card_width_mm}). "
            f"Adjusting CARD_WIDTH_MM to {max_card_width_mm}."
        )
        card_width_mm = max_card_width_mm

    if max_card_height_mm < card_height_mm:
        print(
            f"MAX_CARD_HEIGHT_MM ({max_card_height_mm}) is smaller than CARD_HEIGHT_MM ({card_height_mm}). "
            f"Adjusting CARD_HEIGHT_MM to {max_card_height_mm}."
        )
        card_height_mm = max_card_height_mm

    bleed_h_mm = (max_card_width_mm - card_width_mm) / 2.0
    bleed_v_mm = (max_card_height_mm - card_height_mm) / 2.0

    card_width_px = mm_to_px(card_width_mm + 2 * bleed_h_mm)
    card_height_px = mm_to_px(card_height_mm + 2 * bleed_v_mm)

    max_cols = cols
    max_rows = rows
    if rows == -1 or cols == -1:
        max_cols = max(1, (PAGE_WIDTH - mm_to_px(PAGE_MARGIN_WIDTH_MM * 2.0)) // card_width_px)
        max_rows = max(1, (PAGE_HEIGHT - mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)) // card_height_px)

    margin_x = (PAGE_WIDTH - max_cols * card_width_px) // 2
    margin_y = (PAGE_HEIGHT - max_rows * card_height_px) // 2

    # 构建配置字典（包含原始 mm 配置和派生的像素/布局参数）
    config_dict = {
        "MAX_CARD_WIDTH_MM": max_card_width_mm,
        "MAX_CARD_HEIGHT_MM": max_card_height_mm,
        "CARD_WIDTH_MM": card_width_mm,
        "CARD_HEIGHT_MM": card_height_mm,
        "REPEAT": repeat,
        "REPEAT_COUNT": repeat_count,
        "WRITE_TEXT": write_text,
        "ROWS": rows,
        "COLS": cols,
        "RIGHT_TO_LEFT": right_to_left,
        "BLEED_H_MM": bleed_h_mm,
        "BLEED_V_MM": bleed_v_mm,
        "CARD_WIDTH_PX": card_width_px,
        "CARD_HEIGHT_PX": card_height_px,
        "MAX_COLS": max_cols,
        "MAX_ROWS": max_rows,
        "MARGIN_X": margin_x,
        "MARGIN_Y": margin_y,
        "cfg_map": cfg_map,
        "base_dir": base_dir,
    }

    return config_dict, files, cfg_map, base_dir


def generate_pdf_document(config_dict, files, cfg_map, base_dir, save_pdf=True, output_filename="output.pdf"):
    """
    EN: Generate a PDF document based on the provided layout configuration.
    ZH: 根据传入的排版配置生成 PDF 文件，可选择保存到目录或暂存。
    """
    # 准备图片文件列表（根据配置决定重复次数）
    image_files, effective_repeat_count = prepare_image_files(
        files,
        repeat=config_dict["REPEAT"],
        repeat_count=config_dict["REPEAT_COUNT"],
        max_cols=config_dict["MAX_COLS"],
        max_rows=config_dict["MAX_ROWS"],
    )
    
    if save_pdf:
        output_pdf = os.path.join(base_dir, output_filename)
    else:
        # 如果不保存，使用临时文件
        output_pdf = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4().hex}.pdf")
    
    # 生成PDF
    create_pdf(image_files, output_pdf, cfg_map, base_dir, config_dict)

    return output_pdf, effective_repeat_count


def main(provided_path=""):
    # 步骤1：读取配置（获取文件路径列表以及处理的配置）
    config_dict, files, cfg_map, base_dir = load_config_and_files(provided_path)
    
    # 步骤2：根据配置生成PDF文件（不执行水印操作）
    pdf_path, effective_repeat_count = generate_pdf_document(
        config_dict, files, cfg_map, base_dir, save_pdf=True
    )
    
    # 步骤3：将水印粘贴到PDF每一页
    apply_watermark_to_pdf_pages(
        pdf_path,
        config_dict,
        effective_repeat_count,
        zoom_x=2,
        zoom_y=2,
        rotation_angle=0,
    )
    
if __name__ == "__main__":
    main()