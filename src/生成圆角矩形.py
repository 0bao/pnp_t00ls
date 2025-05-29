from PIL import Image, ImageDraw

def mm_to_px(mm, dpi=300):
    """将毫米转换为像素"""
    return int(mm * dpi / 25.4)

def create_centered_rounded_rectangle_image(bg_width_mm, bg_height_mm, rect_width_mm, rect_height_mm, radius_mm, dpi=300):
    """创建一张带有居中圆角矩形的图片，并在文件名中保留相关信息"""
    # 计算背景和矩形的像素尺寸
    bg_width_px = mm_to_px(bg_width_mm, dpi)
    bg_height_px = mm_to_px(bg_height_mm, dpi)
    rect_width_px = mm_to_px(rect_width_mm, dpi)
    rect_height_px = mm_to_px(rect_height_mm, dpi)
    radius_px = mm_to_px(radius_mm, dpi)

    # 如果圆角矩形大于背景，则自动缩小
    if rect_width_px > bg_width_px or rect_height_px > bg_height_px:
        scale_w = bg_width_px / rect_width_px
        scale_h = bg_height_px / rect_height_px
        scale = min(scale_w, scale_h) * 0.9  # 保留 10% 的边距

        rect_width_px = int(rect_width_px * scale)
        rect_height_px = int(rect_height_px * scale)
        radius_px = int(radius_px * scale)
        print("矩形尺寸超过背景，已自动缩小。")

    # 创建白色背景图像
    image = Image.new("RGB", (bg_width_px, bg_height_px), "white")
    draw = ImageDraw.Draw(image)

    # 计算圆角矩形的居中位置
    rect_x0 = (bg_width_px - rect_width_px) // 2
    rect_y0 = (bg_height_px - rect_height_px) // 2
    rect_x1 = rect_x0 + rect_width_px
    rect_y1 = rect_y0 + rect_height_px

    # 画黑色圆角矩形
    draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=radius_px, fill="black")

    # 生成文件名，不使用 'x' 作为分隔符
    output_path = f"centered_rect_{bg_width_mm}mm_{bg_height_mm}mm_{rect_width_mm}mm_{rect_height_mm}mm_radius{radius_mm}mm_{dpi}dpi.png"

    # 保存图片
    image.save(output_path, dpi=(dpi, dpi))
    print(f"图片已保存至 {output_path}")


MAX_CARD_WIDTH_MM = 54
MAX_CARD_HEIGHT_MM = 122

# -1 for auto
CARD_WIDTH_MM = 52 - 0.5
CARD_HEIGHT_MM = 119 - 0.5

# 调用函数，示例：在 80mm * 150mm 的白色背景上，放置 52mm * 120mm 的圆角矩形
create_centered_rounded_rectangle_image(
    bg_width_mm=MAX_CARD_WIDTH_MM,
    bg_height_mm=MAX_CARD_HEIGHT_MM,
    rect_width_mm=CARD_WIDTH_MM,
    rect_height_mm=CARD_HEIGHT_MM,
    radius_mm=2,
    dpi=300
)

