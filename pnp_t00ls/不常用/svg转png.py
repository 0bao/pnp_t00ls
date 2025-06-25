import os
import glob
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def convert_svg_to_png(input_svg, output_png):
    # 转换 SVG 到 ReportLab 图形对象
    drawing = svg2rlg(input_svg)
    # 保存为 PNG 文件
    renderPM.drawToFile(drawing, output_png, fmt='PNG')
    print(f"转换完成：{output_png}")

def main():
    # 输入目录
    input_directory = input("请输入包含 SVG 文件的目录: ")

    # 获取目录下的所有 SVG 文件
    svg_files = glob.glob(os.path.join(input_directory, '*.svg'))

    # 输出目录
    output_directory = input("请输入保存 PNG 文件的目录: ")
    os.makedirs(output_directory, exist_ok=True)  # 创建输出目录（如果不存在）

    # 转换每个 SVG 文件
    for svg_file in svg_files:
        # 定义输出文件名
        output_png = os.path.join(output_directory, os.path.basename(svg_file).replace('.svg', '.png'))
        convert_svg_to_png(svg_file, output_png)

if __name__ == "__main__":
    main()
