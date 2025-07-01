# pic4grad

为研招报名照发愁？pic4grad 帮你轻松搞定：自由缩放、移动、保存，一键生成报名证件照。

Worried about your graduate admission photo? pic4grad makes it easy: freely scale, move, save, and generate compliant admission photos in one click.

## 快速开始

1. 安装依赖
   ```
   pip install -r requirements.txt
   ```
2. 启动服务（开发模式）
   ```
   python app.py
   ```
   默认访问：http://localhost:5000
3. 生产部署（推荐端口8000，可自定义）
   ```
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
   默认访问：http://localhost:8000

## 功能
- 智能裁剪、缩放、移动
- 支持像素级微调
- 本地运行，数据不出本地
- 支持JPG压缩≤50KB

## 贡献
欢迎PR和建议！ 