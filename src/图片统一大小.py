from PIL import Image
import os

def resize_and_pad_image(image, target_width=512):
    original_size = image.size
    ratio = target_width / original_size[0]
    new_size = (target_width, int(original_size[1] * ratio))

    # Resize the image while keeping the aspect ratio
    image = image.resize(new_size, Image.LANCZOS)

    # Create a new white background image
    target_size = (target_width, new_size[1])
    new_image = Image.new("RGB", target_size, (255, 255, 255))

    # Center the image vertically if needed
    paste_position = (0, 0)

    # Paste the resized image onto the white background
    new_image.paste(image, paste_position)
    return new_image

if __name__ == '__main__':
    imgs_path = input("Image directory: ")
    if imgs_path[0] == '"' and imgs_path[-1] == '"':
        imgs_path = imgs_path[1:-1]

    output_dir = imgs_path + '/256'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print(f"Created output directory: {output_dir}")

    IMAGES_FORMAT = ['.jpg', '.JPG', '.png']
    image_names = [name for name in os.listdir(imgs_path) if os.path.splitext(name)[1] in IMAGES_FORMAT]

    if not image_names:
        print("No valid images found.")
    else:
        image_names.sort()
        for index, name in enumerate(image_names):
            input_image = Image.open(os.path.join(imgs_path, name))
            out_img = resize_and_pad_image(input_image,256)
            output_path = os.path.join(output_dir, f'{index:03d}.png')
            out_img.save(output_path, quality=100)
            print(f"Processed and saved: {output_path}")
