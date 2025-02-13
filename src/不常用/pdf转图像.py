import fitz
import os

'''
# 将PDF转化为图片
pdfPath pdf文件的路径
imgPath 图像要保存的文件夹
zoom_x x方向的缩放系数
zoom_y y方向的缩放系数
rotation_angle 旋转角度
'''

def pdf_image(pdfPath, imgPath, zoom_x, zoom_y, rotation_angle):
    # 打开PDF文件
    pdf = fitz.open(pdfPath)
    # 逐页读取PDF
    for pg in range(0, pdf.page_count):
        page = pdf[pg]
        # 设置缩放和旋转系数

        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        # 开始写图像
        pm.save(imgPath + str(pg) + ".png")

    pdf.close()


if __name__ == '__main__':
    pdf_path = input()
    if (pdf_path[0] == '"' and pdf_path[-1] == '"'):
        pdf_path = pdf_path[1:-1]

    if (pdf_path[-4:] == '.pdf' or pdf_path[-4:] == '.PDF'):
        try:
            os.mkdir(pdf_path[0:-4])
        except:
            pass

        # 获取图片集地址下的所有图片名称
        print("保存目录：" + pdf_path[0:-4])
        pdf_image(pdf_path, pdf_path[0:-4] + '/', 5, 5, 0)

