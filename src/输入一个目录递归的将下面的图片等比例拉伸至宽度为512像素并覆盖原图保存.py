import os
from PIL import Image

def resize_image_to_width(image_path, target_width=512):
    try:
        with Image.open(image_path) as img:
            width_percent = target_width / float(img.width)
            target_height = int(float(img.height) * width_percent)
            resized_image = img.resize((target_width, target_height), Image.LANCZOS)
            resized_image.save(image_path)  # 覆盖原图保存
            print(f"Resized and saved: {image_path}")
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")

def process_directory(directory, target_width=360):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                image_path = os.path.join(root, file)
                resize_image_to_width(image_path, target_width)

def main():
    directory = input("Enter the directory path: ")
    if os.path.isdir(directory):
        process_directory(directory)
    else:
        print("Invalid directory path")

if __name__ == "__main__":
    main()
