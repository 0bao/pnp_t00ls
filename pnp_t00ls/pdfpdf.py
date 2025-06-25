import io
import os
import re
import uuid

import fitz
from PIL import Image
from reportlab.pdfgen import canvas

from file_collector_with_ignore.file_collector_with_ignore import collect_files

imgs_path = "C:/Users/11400/Desktop/share/桌游/burgundy-the_castle_of_burgundy_勃艮第城堡-豪华版-mini/token/正方形板块/"

imgs_path = ""


WRITE_TEXT = True

# Constants for sizing in mm, converted to pixels (A4 at 300ppi)
A4_WIDTH, A4_HEIGHT = (2480, 3508)  # A4 size at 300ppi

MAX_CARD_WIDTH_MM = 44
MAX_CARD_HEIGHT_MM = 64


# -1 for auto
CARD_WIDTH_MM = -1
CARD_HEIGHT_MM = -1

# -1 for auto
ROWS = -1
COLS = -1

RIGHT_TO_LEFT = True

# ａ４纸两边的白边
PAGE_MARGIN_WIDTH_MM = 25 / 2.0
PAGE_MARGIN_HEIGHT_MM = 30 / 2.0 # 实际大小是 35 为了做卡片妥协了

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
DPI = 300

# Convert dimensions from mm to pixels
def mm_to_px(mm, dpi=DPI):
    return int((mm / 25.4) * dpi)

CARD_WIDTH = mm_to_px(CARD_WIDTH_MM + 2 * BLEED_H_MM)  # Width with bleed
CARD_HEIGHT = mm_to_px(CARD_HEIGHT_MM + 2 * BLEED_V_MM)  # Height with bleed

MAX_COLS = COLS
MAX_ROWS = ROWS
if ROWS == -1 or COLS == -1:
    # Calculate rows and columns dynamically based on A4 page size
    MAX_COLS = (A4_WIDTH - mm_to_px(PAGE_MARGIN_WIDTH_MM * 2.0)) // CARD_WIDTH
    i = mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)
    MAX_ROWS = (A4_HEIGHT - mm_to_px(PAGE_MARGIN_HEIGHT_MM * 2.0)) // CARD_HEIGHT

# Calculate margin for centering
MARGIN_X = (A4_WIDTH - MAX_COLS * CARD_WIDTH) // 2
MARGIN_Y = (A4_HEIGHT - MAX_ROWS * CARD_HEIGHT) // 2

# Prepare images and PDF output
def create_pdf(input_dir, output_pdf, right_to_left=False):
    c = canvas.Canvas(output_pdf, pagesize=(A4_WIDTH, A4_HEIGHT))
    x, y = MARGIN_X, A4_HEIGHT - MARGIN_Y - CARD_HEIGHT  # Start at top-left within margins

    # Collect image files
    image_files = []

    filtered_files = collect_files(input_dir)

    for img in filtered_files:
        print(img)
    # 在此进行处理，可以按需要修改
    image_files = []
    for file_path in filtered_files:
        match = re.search(r'x(\d+)', file_path)
        repeat_count = int(match.group(1)) if match else 1
        image_files.extend([file_path] * repeat_count)


    col_count = 0
    row_count = 0

    if right_to_left:
        x = A4_WIDTH - MARGIN_X - CARD_WIDTH  # Start at top-right within margins

    for image_path in image_files:
        print(f"Processing image: {image_path}")
        img = Image.open(image_path)

        # Convert image to RGBA (if not already), to preserve transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create a white background to paste the image on
        img_with_bleed = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255, 255))

        # Resize the image, maintaining the transparency (alpha channel)
        img_resized = img.resize((CARD_WIDTH - 2 * mm_to_px(BLEED_H_MM),
                                  CARD_HEIGHT - 2 * mm_to_px(BLEED_V_MM)), Image.LANCZOS)

        # Paste the resized image onto the white background
        img_with_bleed.paste(img_resized, (mm_to_px(BLEED_H_MM), mm_to_px(BLEED_V_MM)), img_resized)

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
            x = A4_WIDTH - MARGIN_X - CARD_WIDTH if right_to_left else MARGIN_X
            y -= CARD_HEIGHT

        if row_count == MAX_ROWS:
            c.showPage()
            row_count = 0
            x = A4_WIDTH - MARGIN_X - CARD_WIDTH if right_to_left else MARGIN_X
            y = A4_HEIGHT - MARGIN_Y - CARD_HEIGHT

    c.save()
    print(f"PDF saved as {output_pdf}")

def add_page_numbers(input_pdf):
    doc = fitz.open(input_pdf)
    total_pages = doc.page_count

    if WRITE_TEXT:
        for i in range(total_pages):
            page = doc[i]
            if RIGHT_TO_LEFT:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -r2l -p{i + 1}/{total_pages}"
            else:
                page_number = f"-iw{CARD_WIDTH_MM} -ih{CARD_HEIGHT_MM} -ow{MAX_CARD_WIDTH_MM} -oh{MAX_CARD_HEIGHT_MM} -r{MAX_ROWS} -c{MAX_COLS} -l2r -p{i + 1}/{total_pages}"
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

def pdf_image(pdfPath, zoom_x, zoom_y, rotation_angle):
    a4_target_size = (2480, 3508)  # Resize to A4 size
    pdf = fitz.open(pdfPath)
    mark = Image.open("../res/mark-line.png").resize(a4_target_size, Image.LANCZOS)
    out_imgs = []

    for pg in range(pdf.page_count):
        page = pdf[pg]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle), alpha=False)
        img_data = pix.tobytes()
        img = Image.open(io.BytesIO(img_data)).resize(a4_target_size, Image.LANCZOS)
        img.paste(mark, (0, 0), mark)
        out_imgs.append(img)

    pdf.close()

    out_imgs = [img.convert("RGB") for img in out_imgs]

    if out_imgs:
        first_image = out_imgs[0]
        first_image.save(pdfPath[0: -4] + "-marked-line.pdf", save_all=True, append_images=out_imgs[1:], quality=100)

    add_page_numbers(pdfPath[0: -4] + "-marked-line.pdf")
    print(f"Marked PDF saved as {pdfPath[0: -4]}-marked-line.pdf")



if imgs_path == "":
    imgs_path = input("Enter the path to the images folder: ").strip().strip('"')

input_directory = imgs_path
output_pdf = os.path.join(input_directory, "output.pdf")
create_pdf(input_directory, output_pdf, RIGHT_TO_LEFT)
pdf_image(output_pdf, 2, 2, 0)
