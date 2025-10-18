#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 批量图片识别脚本
功能：批量识别data文件夹中的PNG图片，生成Markdown文档
作者：iFlow CLI
版本：1.0
"""

import os
import sys
import time
from datetime import datetime
from paddleocr import PaddleOCR

class OCRProcessor:
    """OCR处理器类"""
    
    def __init__(self):
        """初始化OCR处理器"""
        self.data_folder = "/home/featurize/data"
        self.output_file = "/home/featurize/data/中国文学史名词解释.md"
        self.batch_size = 5  # 每次处理5张图片
        self.log_file = f"/home/featurize/work/ocr_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 初始化PaddleOCR
        print("正在初始化PaddleOCR...")
        self._log_message("开始初始化PaddleOCR")
        try:
            self.ocr = PaddleOCR(
                use_textline_orientation=True,  # 启用文字方向分类（新版本参数）
                lang='ch',           # 中文识别
                device='gpu:0'       # 使用GPU加速（新版本参数）
            )
            self._log_message("PaddleOCR初始化成功")
            print("✅ PaddleOCR初始化成功")
        except Exception as e:
            error_msg = f"❌ PaddleOCR初始化失败: {str(e)}"
            print(error_msg)
            self._log_message(error_msg)
            sys.exit(1)
    
    def _log_message(self, message):
        """记录日志信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # 写入日志文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"⚠️ 无法写入日志文件: {str(e)}")
    
    def _get_image_files(self):
        """获取所有PNG图片文件列表"""
        try:
            # 获取data文件夹中所有PNG文件
            all_files = os.listdir(self.data_folder)
            png_files = [f for f in all_files if f.endswith('.png')]
            
            # 按文件名排序（确保按自然顺序处理）
            png_files.sort()
            
            self._log_message(f"找到 {len(png_files)} 张PNG图片")
            return png_files
        except Exception as e:
            error_msg = f"❌ 获取图片文件失败: {str(e)}"
            self._log_message(error_msg)
            sys.exit(1)
    
    def _process_single_image(self, image_file):
        """处理单张图片"""
        image_path = os.path.join(self.data_folder, image_file)
        
        try:
            # 记录开始处理
            start_time = time.time()
            self._log_message(f"开始处理图片: {image_file}")
            
            # 执行OCR识别
            result = self.ocr.ocr(image_path, use_textline_orientation=True)
            
            # 提取识别的文字
            recognized_text = ""
            if result and result[0]:
                ocr_result = result[0]
                # 从rec_texts提取所有识别的文字
                if hasattr(ocr_result, 'rec_texts'):
                    texts = ocr_result.get('rec_texts', [])
                    recognized_text = "\n".join(texts)
                else:
                    # 兼容旧版本的访问方式
                    for line in result[0]:
                        if line[1][0]:  # 确保文字内容不为空
                            recognized_text += line[1][0] + "\n"
            
            # 记录处理结果
            processing_time = time.time() - start_time
            self._log_message(f"✅ 图片 {image_file} 处理完成，耗时 {processing_time:.2f} 秒")
            self._log_message(f"识别内容: {recognized_text[:50]}..." if len(recognized_text) > 50 else f"识别内容: {recognized_text}")
            
            return recognized_text.strip()
            
        except Exception as e:
            error_msg = f"❌ 处理图片 {image_file} 失败: {str(e)}"
            self._log_message(error_msg)
            print(f"\n{error_msg}")
            print("程序已停止，请检查错误后重试")
            sys.exit(1)
    
    def _save_results(self, results):
        """保存识别结果到Markdown文件"""
        try:
            self._log_message("开始保存识别结果到Markdown文件")
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # 写入文件头部
                f.write("# 中国文学史名词解释\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                # 写入每个图片的识别结果
                for image_file, text in results:
                    f.write(f"## {image_file}\n\n")
                    if text:
                        f.write(f"{text}\n\n")
                    else:
                        f.write("（未识别到文字内容）\n\n")
                    f.write("---\n\n")
            
            self._log_message(f"✅ 识别结果已保存到: {self.output_file}")
            print(f"✅ 识别结果已保存到: {self.output_file}")
            
        except Exception as e:
            error_msg = f"❌ 保存结果失败: {str(e)}"
            self._log_message(error_msg)
            sys.exit(1)
    
    def process_all_images(self):
        """处理所有图片"""
        print("=" * 60)
        print("🚀 开始批量OCR识别")
        print("=" * 60)
        
        # 获取所有图片文件
        image_files = self._get_image_files()
        total_images = len(image_files)
        
        if total_images == 0:
            self._log_message("❌ 未找到任何PNG图片文件")
            print("❌ 未找到任何PNG图片文件")
            return
        
        print(f"📊 总共需要处理 {total_images} 张图片")
        print(f"📦 每批处理 {self.batch_size} 张图片")
        print(f"📝 日志文件: {self.log_file}")
        print(f"📄 输出文件: {self.output_file}")
        print("=" * 60)
        
        # 分批处理图片
        results = []
        for i in range(0, total_images, self.batch_size):
            batch_files = image_files[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (total_images + self.batch_size - 1) // self.batch_size
            
            self._log_message(f"开始处理第 {batch_num}/{total_batches} 批图片")
            print(f"\n🔄 正在处理第 {batch_num}/{total_batches} 批图片...")
            
            # 处理当前批次的每张图片
            for j, image_file in enumerate(batch_files):
                current_index = i + j + 1
                print(f"  📸 [{current_index}/{total_images}] 处理图片: {image_file}")
                
                # 处理单张图片
                recognized_text = self._process_single_image(image_file)
                results.append((image_file, recognized_text))
            
            self._log_message(f"第 {batch_num}/{total_batches} 批图片处理完成")
            print(f"✅ 第 {batch_num}/{total_batches} 批图片处理完成")
        
        # 保存所有结果
        self._save_results(results)
        
        print("=" * 60)
        print("🎉 所有图片处理完成！")
        print(f"📊 处理统计: {total_images} 张图片")
        print(f"📄 输出文件: {self.output_file}")
        print(f"📝 日志文件: {self.log_file}")
        print("=" * 60)

def main():
    """主函数"""
    try:
        # 创建OCR处理器
        processor = OCRProcessor()
        
        # 处理所有图片
        processor.process_all_images()
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()