#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 批量图片识别脚本（命令行完整版）
功能：支持通配符、页码范围、模型切换、CPU/GPU
作者：iFlow CLI
版本：2.0
"""

import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
import argparse
import textwrap
from paddleocr import PaddleOCR

# ---------- 命令行参数 ----------
def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="PaddleOCR 批量图片识别（命令行版）",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""
        示例：
        python3 ocr_cli.py \
            --input-dir "/Users/diessen/temp" \
            --pattern "*.png" \
            --out "/Users/diessen/中国文学史名词解释.md" \
            --model PP-OCRv5_mobile \
            --batch-size 10 \
            --device gpu \
            --page-range 1-10,15,20-25
        """))
    parser.add_argument("--input-dir",  required=True, help="图片目录")
    parser.add_argument("--pattern",   default="*.png", help="文件通配符（默认 *.png）")
    parser.add_argument("--out",       required=True, help="输出 markdown 路径")
    parser.add_argument("--model",
                        choices=["PP-OCRv5_mobile", "PP-OCRv5_server"],
                        default="PP-OCRv5_mobile",
                        help="检测+识别模型组合（默认 mobile）")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="内部 batch size（默认 10）")
    parser.add_argument("--device", choices=["cpu", "gpu"], default="gpu",
                        help="推理设备（默认 gpu）")
    parser.add_argument("--cpu-threads", type=int, default=10,
                        help="mkldnn 线程数（CPU 时生效）")
    parser.add_argument("--page-range", type=str,
                        help="页码范围，如 1-10,15,20-25（按文件名数字排序后）")
    return parser.parse_args()

# ---------- 工具函数 ----------
def natural_numeric_key(p: Path):
    nums = re.findall(r"\d+", p.stem)
    return tuple(int(n) for n in nums) if nums else (float('inf'),)

def parse_page_range(text: str):
    if not text:
        return None
    pages = set()
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            a, b = map(int, part.split("-", 1))
            pages.update(range(min(a, b), max(a, b) + 1))
        else:
            pages.add(int(part))
    # 0-based 索引
    return sorted({p - 1 for p in pages if p > 0})

# ---------- OCR 处理器 ----------
class OCRProcessor:
    def __init__(self, args):
        self.data_folder = Path(args.input_dir).expanduser().resolve()
        self.output_file = Path(args.out).expanduser().resolve()
        self.pattern     = args.pattern
        self.batch_size  = args.batch_size
        self.page_range  = parse_page_range(args.page_range)
        self.log_file = Path("/home/featurize/work") / f"ocr_{datetime.now():%Y%m%d_%H%M%S}.log"


        # 模型映射
        det_model, rec_model = {
            "PP-OCRv5_mobile": ("PP-OCRv5_mobile_det", "PP-OCRv5_mobile_rec"),
            "PP-OCRv5_server": ("PP-OCRv5_server_det", "PP-OCRv5_server_rec"),
        }[args.model]

        print("正在初始化 PaddleOCR...")
        self._log_message("开始初始化 PaddleOCR")
        try:
            self.ocr = PaddleOCR(
                lang='ch',
                device=args.device,
                use_textline_orientation=True,
                text_detection_model_name=det_model,
                text_recognition_model_name=rec_model,
                enable_mkldnn=args.device == "cpu",
                cpu_threads=args.cpu_threads
            )
            self._log_message("PaddleOCR 初始化成功")
            print("✅ PaddleOCR 初始化成功")
        except Exception as e:
            error_msg = f"❌ PaddleOCR 初始化失败: {str(e)}"
            print(error_msg)
            self._log_message(error_msg)
            sys.exit(1)

    def _log_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"⚠️ 无法写入日志文件: {str(e)}")
            
    def _get_image_files(self):
        try:
            files = sorted(self.data_folder.glob(self.pattern), key=natural_numeric_key)
    
            if self.page_range is not None:
                # 提取文件名中的数字部分
                def extract_num(f):
                    nums = re.findall(r"\d+", f.stem)
                    return int(nums[-1]) if nums else None
    
                selected = []
                for f in files:
                    num = extract_num(f)
                    if num is not None and (num in [p + 1 for p in self.page_range]):
                        selected.append(f)
    
                files = selected
    
            png_files = [f.name for f in files if f.is_file()]
            self._log_message(f"找到 {len(png_files)} 张图片：{[f.name for f in files]}")
            return png_files
    
        except Exception as e:
            error_msg = f"❌ 获取图片文件失败: {str(e)}"
            self._log_message(error_msg)
            sys.exit(1)
        
    def _process_single_image(self, image_file):
        image_path = self.data_folder / image_file
        try:
            start = time.time()
            self._log_message(f"开始处理图片: {image_file}")
            result = self.ocr.predict(str(image_path))
            recognized_text = ""
    
            if result and len(result) > 0:
                res = result[0]
    
                # 1. 新接口：OCRResult 对象
                if hasattr(res, 'rec_texts') and res.rec_texts:
                    recognized_text = "\n\n".join(res.rec_texts)
                # 2. 少数版本封装在 .json['res']['rec_texts']
                elif hasattr(res, 'json') and isinstance(res.json, dict):
                    rec_texts = res.json.get('res', {}).get('rec_texts', [])
                    recognized_text = "\n\n".join(rec_texts)
                # 3. 旧版 list fallback
                elif isinstance(res, (list, tuple)):
                    recognized_text = "\n\n".join([line[1][0] for line in res if len(line) > 1])
                else:
                    self._log_message(f"⚠️ 未识别的 OCR 结果结构: {type(res)}")
    
                # 统一清理空行
                recognized_text = re.sub(r'\n{3,}', '\n\n', recognized_text.strip())
    
            cost = time.time() - start
            self._log_message(f"✅ 图片 {image_file} 处理完成，耗时 {cost:.2f} 秒")
            return recognized_text
    
        except Exception as e:
            error_msg = f"❌ 处理图片 {image_file} 失败: {e}"
            self._log_message(error_msg)
            return ""

    def _save_results(self, results):
        try:
            self._log_message("开始保存识别结果到 Markdown 文件")
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# 中国文学史名词解释\n\n")
                f.write(f"生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
                f.write("---\n\n")
                for image_file, text in results:
                    f.write(f"## {image_file}\n\n")
                    f.write(f"{text or '（未识别到文字内容）'}\n\n")
                    f.write("---\n\n")
            print(f"✅ 识别结果已保存到: {self.output_file}")
        except Exception as e:
            error_msg = f"❌ 保存结果失败: {str(e)}"
            self._log_message(error_msg)
            sys.exit(1)

    def process_all_images(self):
        print("=" * 60)
        print("🚀 开始批量 OCR 识别")
        print("=" * 60)
        image_files = self._get_image_files()
        total = len(image_files)
        if total == 0:
            print("❌ 未找到任何图片")
            return
        print(f"📊 共 {total} 张图片 | 日志: {self.log_file}")
        print("=" * 60)

        results = []
        for img in image_files:
            text = self._process_single_image(img)
            results.append((img, text))

        self._save_results(results)
        print("=" * 60)
        print("🎉 所有图片处理完成！")
        print("=" * 60)

# ---------- 入口 ----------
def main():
    args = parse_cli_args()
    try:
        OCRProcessor(args).process_all_images()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()