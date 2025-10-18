# PaddleOCR v5 GPU 版本批量识别工具

本项目使用 PaddleOCR v5 GPU 版本对图片进行批量文字识别，特别针对中文文学史相关图片进行了优化。

## 功能特点

- 使用 PaddleOCR v5 最新版本
- 支持 GPU 加速（RTX 3060）
- 批量处理 PNG 图片
- 生成 Markdown 格式输出文件
- 详细的日志记录

## 环境要求

- Python 3.11.8
- PaddlePaddle GPU 3.0.0 (CUDA 12.3)
- PaddleOCR 3.3.0
- NVIDIA RTX 3060 显卡

## 使用方法

1. 安装依赖：
   ```bash
   pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
   pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. 运行批量识别：
   ```bash
   python ocr_cli.py
   ```

## 项目文件说明

- `ocr_cli.py`: 主要的批量OCR处理脚本
- `PaddleOCR研究文档.md`: 安装和使用说明文档
- `install_commands.md`: 详细的安装命令列表
- `final_test.py`: 简单测试脚本

## 输出文件

- 识别结果：`data/中国文学史名词解释.md`
- 日志文件：`work/ocr_execution_*.log`