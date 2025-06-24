from PIL import Image
import os

# 你可以在这里修改边框图片路径
BORDER_IMAGE_PATH = "C:\\Users\\11400\\Desktop\\职业边框.png"

def add_border_and_overwrite(folder_path, border_path):
    # 加载边框图片
    try:
        border_img = Image.open(border_path).convert("RGBA")
    except FileNotFoundError:
        print(f"❌ 找不到边框图片：{border_path}")
        return

    supported_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(supported_exts):
            img_path = os.path.join(folder_path, file_name)

            try:
                # 加载原图并转换为 RGBA
                base_img = Image.open(img_path).convert("RGBA")
            except Exception as e:
                print(f"❌ 无法打开图片：{img_path}，跳过。原因：{e}")
                continue

            # 拉伸边框并合成
            base_size = base_img.size
            resized_border = border_img.resize(base_size, Image.Resampling.LANCZOS)
            combined = Image.alpha_composite(base_img, resized_border)

            # 若原图为非 PNG 格式，则转换为 RGB 保存（以避免 alpha 渐变错误）
            ext = os.path.splitext(file_name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.bmp']:
                combined = combined.convert("RGB")

            # 保存覆盖原图
            combined.save(img_path)
            print(f"✔ 已覆盖：{file_name}")

    print("🎉 全部图片已处理并覆盖。")

if __name__ == "__main__":
    folder = input("📁 请输入包含图片的文件夹路径：").strip()
    if os.path.isdir(folder):
        add_border_and_overwrite(folder, BORDER_IMAGE_PATH)
    else:
        print("❌ 无效的目录路径，请重新运行脚本。")