import fitz
import os

def convert_and_save_image(pix, output_path):
    # 如果图像有 Alpha 通道（透明通道），先将其转换为 RGB
    if pix.n >= 5:  # 这意味着图像可能是带 Alpha 通道的（例如 CMYK 或 RGBA）
        # 转换为 RGB 格式
        pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
        pix_rgb.save(output_path)
        pix_rgb = None
        print(f"保存图片: {output_path} (转换为 RGB 模式)")
    else:
        # 图像是 GRAY 或 RGB，可以直接保存
        pix.save(output_path)
        print(f"保存图片: {output_path} (GRAY/RGB 模式)")

if __name__ == '__main__':
    # 简洁的输入提示，告知用户双引号会自动处理
    pdf_path = input('请输入 PDF 文件路径（程序将自动去除两端双引号）:\n')

    # 自动去除两端的双引号（如果有）
    pdf_path = pdf_path.strip('"')

    # 检查文件扩展名是否为 .pdf 或 .PDF
    if pdf_path.lower().endswith('.pdf'):
        try:
            # 尝试创建保存图片的目录
            os.mkdir(pdf_path[:-4])
            print(f"创建目录: {pdf_path[:-4]}")
        except FileExistsError:
            print(f"目录 {pdf_path[:-4]} 已存在，跳过创建。")

        # 设置图片输出路径
        images_output_path = pdf_path[:-4]
        print(f"图片将保存到目录: {images_output_path}")

        # 打开 PDF 文档
        pdf_document = fitz.open(pdf_path)
        print(f"已打开 PDF 文件: {pdf_path}")

        index = 0  # 初始化图片计数器

        # 遍历 PDF 的每一页
        for current_page in range(len(pdf_document)):
            print(f"处理第 {current_page + 1} 页，共 {len(pdf_document)} 页。")

            # 获取当前页面上的所有图片
            for image in pdf_document.get_page_images(current_page):
                xref = image[0]  # 图片的 XREF
                pix = fitz.Pixmap(pdf_document, xref)

                # 格式化图片编号为三位数
                str_num = str('%03d' % index)
                output_path = os.path.join(images_output_path, f'{str_num}.png')

                try:
                    # 转换并保存为 RGB PNG
                    convert_and_save_image(pix, output_path)
                except Exception as e:
                    print(f"保存图片失败: {e}")
                finally:
                    pix = None  # 释放资源

                index += 1  # 图片计数器递增

        print("图片提取完成。")
