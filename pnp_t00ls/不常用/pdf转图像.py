import fitz  # PyMuPDF
import os

def pdf_image(pdf_path, img_path, zoom_x, zoom_y, rotation_angle, to_jpeg=True, quality=85):
    doc = fitz.open(pdf_path)
    for pg in range(doc.page_count):
        page = doc[pg]
        # 计算缩放矩阵并应用旋转
        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pix = page.get_pixmap(matrix=trans, alpha=False)

        if to_jpeg:
            out_file = os.path.join(img_path, f"{pg:03d}.jpg")
            # jpg_quality: 0-100
            pix.save(out_file, jpg_quality=quality)
        else:
            out_file = os.path.join(img_path, f"{pg:03d}.png")
            pix.save(out_file)

        print(f"已保存: {out_file}")

    doc.close()
    print(f"共转换 {doc.page_count} 页。")

if __name__ == '__main__':
    pdf_path = input("请输入 PDF 路径（自动去除引号）：\n").strip('"')

    if pdf_path.lower().endswith('.pdf'):
        output_dir = pdf_path[:-4]
        os.makedirs(output_dir, exist_ok=True)

        print(f"保存目录：{output_dir}")

        # 设定目标 DPI → zoom = DPI/72
        dpi = 300
        zoom = dpi / 72

        # 这里设置是否保存为 JPEG 及其质量
        pdf_image(pdf_path, output_dir, zoom, zoom, 0, to_jpeg=True, quality=85)

        print("图片已保存。")
    else:
        print("请输入正确的 PDF 文件路径")
