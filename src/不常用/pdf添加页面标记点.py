import fitz
import os
import PIL.Image as Image
import io

'''
# 将PDF转化为图片
pdfPath pdf文件的路径
imgPath 图像要保存的文件夹
zoom_x x方向的缩放系数
zoom_y y方向的缩放系数
rotation_angle 旋转角度
'''

def pdf_image(pdfPath, imgPath, zoom_x, zoom_y, rotation_angle):
    # 指定目标大小 (宽度, 高度)
    a4_target_size = (2479, 3508)  # 例如，缩放至 200x300 像素
    # 打开PDF文件
    pdf = fitz.open(pdfPath)

    mark = Image.open("../../res/mark-line.png")

    mark = mark.resize(a4_target_size, Image.LANCZOS)

    out_imgs = []
    # 逐页读取PDF
    for pg in range(0, pdf.page_count):
        page = pdf[pg]
        # 设置缩放和旋转系数

        pix = page.get_pixmap()

        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pix = page.get_pixmap(matrix=trans, alpha=False)

        # 获取图像数据
        img_data = pix.tobytes()  # 获取图像的字节数据

        img = Image.open(io.BytesIO(img_data))

        # 使用 ANTIALIAS 算法进行高质量缩放
        img = img.resize(a4_target_size, Image.LANCZOS)

        img.paste(mark, (0, 0), mark)
        out_imgs.append(img)

    pdf.close()

    # for img in out_imgs:
    #     img.show()

    # 假设 out_imgs 是你已经创建并填充的图像列表
    # 确保所有图像都转换为 RGB 模式，因为 PDF 不支持带有透明度的图像
    out_imgs = [img.convert("RGB") for img in out_imgs]

    # 将图像列表中的第一张图片作为 PDF 的起始页
    if out_imgs:
        first_image = out_imgs[0]

        # 将其余图像作为追加页保存到 PDF 中
        first_image.save(pdfPath[0: -4] + "-marked-line.pdf", save_all=True, append_images=out_imgs[1:], quality=100)



if __name__ == '__main__':
    pdf_path = input("pdf path: ")
    if (pdf_path[0] == '"' and pdf_path[-1] == '"'):
        pdf_path = pdf_path[1:-1]

        # 获取图片集地址下的所有图片名称
        pdf_image(pdf_path, pdf_path[0:-4] + '/', 5, 5, 0)


