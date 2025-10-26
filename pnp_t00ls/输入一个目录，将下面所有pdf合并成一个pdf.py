import fitz
from pathlib import Path

def merge_pdfs_in_dir(folder_path: str):
    """
    将 folder_path 下所有 PDF 按文件名排序后合并，输出到同一目录 output.pdf
    """
    folder = Path(folder_path)
    output_pdf = folder / "output.pdf"

    pdf_files = sorted(folder.glob("*.pdf"))  # 只合并顶层目录 *.pdf，按名字排序
    if not pdf_files:
        print("目录中没有找到 PDF 文件。")
        return

    merged = fitz.open()
    for pdf_file in pdf_files:
        with fitz.open(pdf_file) as src:
            merged.insert_pdf(src)           # 直接把整本插进来
            print(f"已添加：{pdf_file.name}")

    merged.save(output_pdf)
    merged.close()
    print(f"合并完成：{output_pdf}")


dir = input().strip().strip('"')
merge_pdfs_in_dir(dir)