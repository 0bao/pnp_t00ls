import fitz
import os

def add_page_numbers(input_pdf, output_pdf):
    # 打开输入的 PDF 文件
    doc = fitz.open(input_pdf)

    # 获取总页数
    total_pages = doc.page_count

    # 遍历每一页，添加页码
    for i in range(total_pages):
        page = doc[i]
        page_number = f"Page {i + 1} of {total_pages}"

        # 获取页面尺寸
        page_width, page_height = page.rect.width, page.rect.height

        # 动态设置字体大小（根据页面高度设置字体大小）
        font_size = page_height * 0.01  # 字体大小为页面高度的 4%
        font = "helv"

        # 计算文本宽度
        font_obj = fitz.Font(font)  # 创建字体对象
        text_length = font_obj.text_length(page_number, font_size)

        # 计算居中对齐的位置
        x_position = (page_width - text_length) / 2
        y_position = page_height * 0.04  # 距离顶部 5% 的位置

        # 在页面上插入页码
        page.insert_text(
            fitz.Point(x_position, y_position),  # 页码位置
            page_number,
            fontsize=font_size,
            fontname=font,
            color=(0, 0, 0)  # 黑色字体
        )

    # 保存并覆盖原 PDF 文件
    doc.save(output_pdf)
    doc.close()


def main():
    # 简洁的输入提示，告知用户双引号会自动处理
    pdf_path = input('请输入 PDF 文件路径（程序将自动去除两端双引号）:\n')

    # 自动去除两端的双引号（如果有）
    input_pdf = pdf_path.strip('"')

    base_name, ext = os.path.splitext(input_pdf)
    output_pdf = f"{base_name}_with_page_numbers{ext}"

    if os.path.exists(input_pdf):
        add_page_numbers(input_pdf, output_pdf)
        print(f"页码已添加到 {output_pdf}")
    else:
        print(f"文件 {input_pdf} 不存在")


if __name__ == "__main__":
    main()
