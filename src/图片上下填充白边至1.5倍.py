from PIL import Image, ImageOps
import os

def adjust_image_aspect_ratio(image_path):
    img = Image.open(image_path)
    width, height = img.size
    target_height = int(width * 1.5)

    if height != target_height:
        # Calculate padding needed to center the image vertically
        padding_top = (target_height - height) // 2
        padding_bottom = target_height - height - padding_top
        padding = (0, padding_top, 0, padding_bottom)

        # Add white padding (fill color is white)
        img = ImageOps.expand(img, padding, fill='white')

        # Overwrite the original file
        img.save(image_path)

def process_images_in_folder(input_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            file_path = os.path.join(input_folder, filename)
            adjust_image_aspect_ratio(file_path)

def main():
    input_folder = input("Image directory: ").strip().strip('"')  # Replace with your input folder path
    process_images_in_folder(input_folder)

if __name__ == "__main__":
    main()
