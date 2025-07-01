from flask import Flask, request, render_template, send_file, url_for, redirect
import tempfile
import os
from resize_crop_jpg import resize_and_crop
import shutil
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()

app = Flask(__name__)

def get_scale(form):
    try:
        scale = float(form.get('scale', '1.0'))
        if scale < 1.0:
            scale = 1.0
        if scale > 2.0:
            scale = 2.0
        return round(scale, 2)
    except Exception:
        return 1.0

def get_temp_filename(original_extension='.jpg'):
    """根据原始文件扩展名生成临时文件名"""
    # 确保扩展名以.开头
    if not original_extension.startswith('.'):
        original_extension = '.' + original_extension
    return next(tempfile._get_candidate_names()) + original_extension

def get_file_extension(filename):
    """获取文件扩展名"""
    if filename:
        return os.path.splitext(filename)[1].lower()
    return '.jpg'

def get_image_size(orig_path):
    with Image.open(orig_path) as img:
        return img.size

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    download_url = None
    orig_filename = None
    result_filename = None
    original_filename = None
    scale = 1.0
    center_x = None
    top_y = None
    default_center_x = None
    if request.method == 'POST':
        action = request.form.get('action')
        scale = request.form.get('scaleInput') or request.form.get('scale')
        scale = get_scale({'scale': scale})
        orig_filename = request.form.get('orig_filename')
        center_x = request.form.get('center_x')
        top_y = request.form.get('top_y')
        original_filename = request.form.get('original_filename')
        file = request.files.get('file')
        if file:
            # 新上传图片，保存原图，重置参数
            scale = 1.0
            original_filename = file.filename
            # 根据原始文件扩展名保存
            file_extension = get_file_extension(original_filename)
            orig_filename = get_temp_filename(file_extension)
            orig_path = os.path.join(tempfile.gettempdir(), orig_filename)
            file.save(orig_path)
            w, h = get_image_size(orig_path)
            center_x = w // 2
            top_y = 0
            # 计算裁剪区域
            if w/h > 150/200:
                crop_w = int(h * 150/200 / scale)
                crop_h = int(h / scale)
            else:
                crop_w = int(w / scale)
                crop_h = int(w / (150/200) / scale)
            move_step_x = int(w * 0.05)
            move_step_y = int(h * 0.05)
            micro_step_x = max(1, move_step_x // 10)
            micro_step_y = max(1, move_step_y // 10)
            left_x = max(crop_w//2, center_x - move_step_x)
            right_x = min(w - crop_w//2, center_x + move_step_x)
            up_y = max(0, top_y - move_step_y)
            down_y = min(h - crop_h, top_y + move_step_y)
            default_center_x = w // 2
            center_x_minus1 = max(crop_w//2, center_x - micro_step_x)
            center_x_plus1 = min(w - crop_w//2, center_x + micro_step_x)
            top_y_minus1 = max(0, top_y - micro_step_y)
            top_y_plus1 = min(h - crop_h, top_y + micro_step_y)
        elif orig_filename:
            orig_path = os.path.join(tempfile.gettempdir(), orig_filename)
            w, h = get_image_size(orig_path)
            # 解析参数
            try:
                center_x = int(float(center_x)) if center_x is not None else w // 2
                top_y = int(float(top_y)) if top_y is not None else 0
            except Exception:
                center_x = w // 2
                top_y = 0
            move_step_x = int(w * 0.05)
            move_step_y = int(h * 0.05)
            micro_step_x = max(1, move_step_x // 10)
            micro_step_y = max(1, move_step_y // 10)
            if w/h > 150/200:
                crop_w = int(h * 150/200 / scale)
                crop_h = int(h / scale)
            else:
                crop_w = int(w / scale)
                crop_h = int(w / (150/200) / scale)
            if action == 'move_left':
                center_x = max(crop_w//2, center_x - move_step_x)
            elif action == 'move_right':
                center_x = min(w - crop_w//2, center_x + move_step_x)
            elif action == 'move_up':
                top_y = max(0, top_y - move_step_y)
            elif action == 'move_down':
                top_y = min(h - crop_h, top_y + move_step_y)
            elif action == 'reset':
                center_x = w // 2
                top_y = 0
            left_x = max(crop_w//2, center_x - move_step_x)
            right_x = min(w - crop_w//2, center_x + move_step_x)
            up_y = max(0, top_y - move_step_y)
            down_y = min(h - crop_h, top_y + move_step_y)
            default_center_x = w // 2
            center_x_minus1 = max(crop_w//2, center_x - micro_step_x)
            center_x_plus1 = min(w - crop_w//2, center_x + micro_step_x)
            top_y_minus1 = max(0, top_y - micro_step_y)
            top_y_plus1 = min(h - crop_h, top_y + micro_step_y)
            if action == 'move_left_px':
                center_x = max(crop_w//2, center_x - micro_step_x)
            elif action == 'move_right_px':
                center_x = min(w - crop_w//2, center_x + micro_step_x)
            elif action == 'move_up_px':
                top_y = max(0, top_y - micro_step_y)
            elif action == 'move_down_px':
                top_y = min(h - crop_h, top_y + micro_step_y)
        else:
            left_x = right_x = up_y = down_y = 0
            default_center_x = 0
            center_x_minus1 = center_x_plus1 = top_y_minus1 = top_y_plus1 = 0
        # 处理图片
        if orig_filename:
            orig_path = os.path.join(tempfile.gettempdir(), orig_filename)
            result_filename = get_temp_filename('.result.jpg')
            result_path = os.path.join(tempfile.gettempdir(), result_filename)
            resize_and_crop(orig_path, result_path, scale=scale, center_x=center_x, top_y=top_y)
            image_url = url_for('preview', filename=result_filename) + f'?s={scale}&x={center_x}&y={top_y}'
            download_url = url_for('download', filename=result_filename)
    else:
        scale = 1.0
        center_x = 0
        top_y = 0
        left_x = right_x = up_y = down_y = 0
        default_center_x = 0
        center_x_minus1 = center_x_plus1 = top_y_minus1 = top_y_plus1 = 0
    scale_up = round(float(scale) * 1.1, 2)
    scale_down = round(float(scale) * 0.9, 2)
    return render_template('index.html', image_url=image_url, download_url=download_url, orig_filename=orig_filename, result_filename=result_filename, scale=scale, scale_up=scale_up, scale_down=scale_down, center_x=center_x, top_y=top_y, left_x=left_x, right_x=right_x, up_y=up_y, down_y=down_y, default_center_x=default_center_x, center_x_minus1=center_x_minus1, center_x_plus1=center_x_plus1, top_y_minus1=top_y_minus1, top_y_plus1=top_y_plus1, original_filename=original_filename)

@app.route('/preview/<filename>')
def preview(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(file_path, mimetype='image/jpeg')

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(file_path, as_attachment=True, download_name='output.jpg', mimetype='image/jpeg')

@app.route('/delete', methods=['POST'])
def delete():
    orig_filename = request.form.get('orig_filename')
    result_filename = request.form.get('result_filename')
    for filename in [orig_filename, result_filename]:
        if filename:
            file_path = os.path.join(tempfile.gettempdir(), filename)
            try:
                os.remove(file_path)
            except Exception:
                pass
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)