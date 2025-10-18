# PaddleOCR 安装命令列表

## 安装前说明
- 请按顺序执行以下命令
- 每个命令执行后，请等待确认成功再执行下一个
- 如果出现错误，请立即停止并告知我

---

## 命令1: 环境检查
```bash
# 检查Python版本
python --version

# 检查GPU状态
nvidia-smi

# 检查CUDA版本
nvcc --version
```

**预期结果**:
- Python版本显示3.11.8
- nvidia-smi显示RTX 3060信息
- CUDA版本显示12.6

---

## 命令2: 升级pip
```bash
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**预期结果**: 显示Successfully installed pip-版本号

---

## 命令3: 安装PaddlePaddle GPU版本
```bash
python -m pip install paddlepaddle-gpu==3.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**预期结果**: 显示Successfully installed paddlepaddle-gpu-3.0.0及相关依赖

---

## 命令4: 验证PaddlePaddle安装
```bash
python -c "import paddle; paddle.utils.run_check()"
```

**预期结果**: 显示PaddlePaddle安装成功，包含GPU信息

---

## 命令5: 安装PaddleOCR
```bash
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**预期结果**: 显示Successfully installed paddleocr-版本号及相关依赖

---

## 命令6: 验证PaddleOCR安装
```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR安装成功')"
```

**预期结果**: 显示PaddleOCR安装成功

---

## 命令7: 测试OCR功能
```bash
python -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True, show_log=False)
print('PaddleOCR PP-OCRv5模型加载成功')
"
```

**预期结果**: 显示PaddleOCR PP-OCRv5模型加载成功

---

## 安装完成后

1. 确认所有命令都执行成功
2. 告知我安装完成，我们将测试OCR脚本
3. 准备data文件夹中的图片
4. 运行OCR脚本进行批量处理