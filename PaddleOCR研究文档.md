# PaddleOCR 研究文档

## 1. 安装要求

### 系统要求
- **操作系统**: Linux (您的系统符合要求)
- **Python版本**: 3.7+ (您的版本是3.11.8，符合要求)
- **GPU**: NVIDIA GPU (您的RTX 3060完全支持)
- **CUDA版本**: 11.0+ (您的版本是12.6，完全支持)

### 依赖库要求
- PaddlePaddle (GPU版本)
- PaddleOCR (包含PP-OCRv5模型)
- 标准Python库 (os, sys, time等)

## 2. 安装命令

### 步骤1: 升级pip
```bash
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤2: 安装PaddlePaddle GPU版本
```bash
python -m pip install paddlepaddle-gpu==3.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤3: 验证PaddlePaddle安装
```bash
python -c "import paddle; paddle.utils.run_check()"
```

### 步骤4: 安装PaddleOCR
```bash
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤5: 验证PaddleOCR安装
```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR安装成功')"
```

## 3. 使用参数说明

### PaddleOCR初始化参数
- `use_angle_cls=True`: 启用文字方向分类
- `lang='ch'`: 指定中文识别
- `use_gpu=True`: 使用GPU加速 (您的环境支持)
- `show_log=True`: 显示日志信息

### OCR识别参数
- `det_model_dir=None`: 使用默认检测模型
- `rec_model_dir=None`: 使用默认识别模型
- `cls_model_dir=None`: 使用默认分类模型

## 4. 基本使用示例

### 简单识别单张图片
```python
from paddleocr import PaddleOCR

# 初始化OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)

# 识别图片
result = ocr.ocr('图片路径', cls=True)

# 输出结果
for line in result:
    print(line[1][0])  # 打印识别的文字
```

### 批量处理图片
```python
import os
from paddleocr import PaddleOCR

# 初始化OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)

# 获取图片列表
image_folder = '图片文件夹路径'
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])

# 批量处理
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    result = ocr.ocr(image_path, cls=True)
    print(f"处理图片: {image_file}")
    # 处理识别结果...
```

## 5. 常见问题

### Q: 如何确认GPU是否被使用？
A: 运行PaddlePaddle验证命令时，会显示GPU信息。

### Q: 识别速度慢怎么办？
A: 确认`use_gpu=True`已设置，并检查GPU内存使用情况。

### Q: 如何提高识别准确率？
A: 确保图片清晰，文字方向正确，可以使用`use_angle_cls=True`自动校正方向。

## 6. PP-OCRv5模型特点

- **高精度**: 中文识别准确率高
- **多语言**: 支持80+种语言
- **轻量级**: 模型大小适中，运行速度快
- **GPU优化**: 充分利用GPU加速，提高处理效率