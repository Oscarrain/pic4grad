import sys
import os
from PIL import Image

def resize_and_crop(input_path, output_path, scale=1.0, center_x=None, top_y=None):
    img = Image.open(input_path)
    
    # 处理透明背景：如果是RGBA模式，转换为RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        # 创建白色背景
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    w, h = img.size
    target_w, target_h = 150, 200
    target_ratio = target_w / target_h
    img_ratio = w / h

    # 计算裁剪区域的宽高
    if img_ratio > target_ratio:
        crop_h = h
        crop_w = int(h * target_ratio)
    else:
        crop_w = w
        crop_h = int(w / target_ratio)
    # 缩放裁剪区域
    crop_w = int(crop_w / scale)
    crop_h = int(crop_h / scale)
    # 默认中心点
    if center_x is None:
        center_x = w // 2
    if top_y is None:
        top_y = 0
    # 以center_x, top_y为上边中心点，计算裁剪区域
    left = int(center_x - crop_w // 2)
    top = int(top_y)
    # 边界检查
    if left < 0:
        left = 0
    if left + crop_w > w:
        left = w - crop_w
    if top < 0:
        top = 0
    if top + crop_h > h:
        top = h - crop_h
    img = img.crop((left, top, left + crop_w, top + crop_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)
    for quality in range(95, 10, -5):
        img.save(output_path, 'JPEG', quality=quality)
        if os.path.getsize(output_path) <= 50 * 1024:
            break
    if os.path.getsize(output_path) > 50 * 1024:
        print("警告：已压缩到最低quality，文件仍大于50KB。")

def main():
    if len(sys.argv) not in (3, 4, 6):
        print("用法: python resize_crop_jpg.py 输入图片路径 输出图片路径 [缩放比例] [center_x] [top_y]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    scale = float(sys.argv[3]) if len(sys.argv) >= 4 else 1.0
    center_x = int(sys.argv[4]) if len(sys.argv) >= 5 else None
    top_y = int(sys.argv[5]) if len(sys.argv) >= 6 else None
    resize_and_crop(input_path, output_path, scale=scale, center_x=center_x, top_y=top_y)
    print(f"处理完成，输出文件: {output_path}")

if __name__ == "__main__":
    main() 