from PIL import Image
import os

def resize_image(image, target_width=2048):
    # Calculate the new height to maintain the aspect ratio
    width_percent = target_width / float(image.width)
    target_height = int((float(image.height) * float(width_percent)))
    new_size = (target_width, target_height)
    image = image.resize(new_size, Image.LANCZOS)
    return image

if __name__ == '__main__':

    width = 2048

    imgs_path = input("Image directory: ").strip().strip('"')

    output_dir = os.path.join(imgs_path, str(width))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Using makedirs to support multi-level directory creation
        print(f"Created output directory: {output_dir}")

    IMAGES_FORMAT = ['.jpg', '.jpeg', '.JPG', '.png', '.bmp']
    image_names = [name for name in os.listdir(imgs_path) if os.path.splitext(name)[1] in IMAGES_FORMAT]

    if not image_names:
        print("No valid images found.")
    else:
        image_names.sort()
        for index, name in enumerate(image_names):
            input_image = Image.open(os.path.join(imgs_path, name))
            out_img = resize_image(input_image, width)  # Resize the image to 2048 width while maintaining aspect ratio
            output_path = os.path.join(output_dir, f'{index:03d}.png')
            out_img.save(output_path, quality=100)
            print(f"Processed and saved: {output_path}")
