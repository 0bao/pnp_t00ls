import PIL.Image as Image
from PIL import ImageDraw, ImageFont

def edge_extension(img, w_extension, h_extension, color = (255, 255, 255)):
    w, h = img.size
    w = w + w_extension * 2
    h = h + h_extension * 2
    output_image = Image.new('RGB', (w, h), color)
    output_image.paste(img, (w_extension, h_extension))
    return output_image

def edge_extension_a4(img):
    A4_HEIGHT = 2480
    A4_WIDTH = 3508
    w, h = img.size
    color = (255, 255, 255)
    aspect = w / h
    print(str(aspect))

    t_h = A4_HEIGHT * 0.89
    t_w = A4_WIDTH * 0.89
    # 优先保护 w
    if t_h < h * A4_WIDTH / w:
        h = t_h
        w = h * aspect
    else:
        w = t_w
        h = w / aspect

    print(str(aspect))

    h = int(h)
    w = int(w)

    w_extension = int((A4_WIDTH - w) / 2)
    h_extension = int((A4_HEIGHT - h) / 2)

    print('w_extension: ' + str(w_extension))
    print('h_extension: ' + str(h_extension))

    output_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), color)
    output_image.paste(img.resize((w, h), Image.LANCZOS), (int(w_extension), int(h_extension)))
    return output_image



def edge_extension_a4_portrait(img):
    A4_HEIGHT = 3508
    A4_WIDTH = 2480
    w, h = img.size
    color = (255, 255, 255)
    aspect = w / h
    print(str(aspect))

    # 七大奇迹
    t_h = A4_HEIGHT * 0.917
    t_w = A4_WIDTH * 0.917
    # 优先保护 w
    if t_h < h * A4_WIDTH / w:
        h = t_h
        w = h * aspect
    else:
        w = t_w
        h = w / aspect

    print(str(aspect))

    h = int(h)
    w = int(w)

    w_extension = int((A4_WIDTH - w) / 2)
    h_extension = int((A4_HEIGHT - h) / 2)

    print('w_extension: ' + str(w_extension))
    print('h_extension: ' + str(h_extension))

    output_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), color)
    output_image.paste(img.resize((w, h), Image.LANCZOS), (int(w_extension), int(h_extension)))
    return output_image


def edge_extension_a4_landscape(img, scale = 0.917):
    A4_HEIGHT = 2480 * 2
    A4_WIDTH = 3508 * 2
    w, h = img.size
    color = (255, 255, 255)
    aspect = w / h
    print(str(aspect))

    t_h = A4_HEIGHT * scale
    t_w = A4_WIDTH * scale

    # 优先保护 w
    if t_h < h * A4_WIDTH / w:
        h = t_h
        w = h * aspect
    else:
        w = t_w
        h = w / aspect

    print(str(aspect))

    h = int(h)
    w = int(w)

    w_extension = int((A4_WIDTH - w) / 2)
    h_extension = int((A4_HEIGHT - h) / 2)

    print('w_extension: ' + str(w_extension))
    print('h_extension: ' + str(h_extension))

    output_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), color)
    output_image.paste(img.resize((w, h), Image.LANCZOS), (int(w_extension), int(h_extension)))
    return output_image