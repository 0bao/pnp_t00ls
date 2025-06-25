import os
import shutil


def is_image_file(filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def rename_and_copy_images(input_directory):
    # 输出目录名称
    output_directory = os.path.join(input_directory, "output_images")

    # 如果输出目录已存在，先删除它
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)

    os.makedirs(output_directory, exist_ok=True)

    counter = 0
    for root, _, files in os.walk(input_directory):
        for file in files:
            if is_image_file(file) and root != output_directory:
                old_path = os.path.join(root, file)
                new_filename = f"{counter:03d}{os.path.splitext(file)[1]}"
                new_path = os.path.join(output_directory, new_filename)
                shutil.copy2(old_path, new_path)
                print(f"Copied {old_path} to {new_path}")
                counter += 1

    print(f"所有图片已重命名并复制到 {output_directory}。")


if __name__ == "__main__":
    input_directory = input("请输入源目录路径：")
    rename_and_copy_images(input_directory)
