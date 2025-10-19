#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 批量图片识别脚本
功能：批量识别data文件夹中的PNG图片，生成Markdown文档
作者：iFlow CLI
版本：1.4 (最终修正版)
"""

import os
import sys
import time
from datetime import datetime
from paddleocr import PaddleOCR
import concurrent.futures

class OCRProcessor:
    """OCR处理器类"""
    
    def __init__(self):
        """初始化OCR处理器"""
        self.data_folder = "/home/featurize/data"
        self.output_file = "/home/featurize/data/中国文学史名词解释.md"
        self.batch_size = 1
        self.log_file = f"/home/featurize/work/ocr_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 初始化PaddleOCR
        print("正在初始化PaddleOCR...")
        self._log_message("开始初始化PaddleOCR")
        try:
            # 修正1: 使用官方推荐的新版参数
            self.ocr = PaddleOCR(
                lang='ch',
                device='gpu',
                use_textline_orientation=True,
                # 保持使用server模型以保证质量，但添加内存优化参数
                #text_detection_model_name="PP-OCRv5_server_det",
                #text_recognition_model_name="PP-OCRv5_server_rec",
                text_detection_model_name="PP-OCRv5_mobile_det",  # 👈 换轻量模型
                text_recognition_model_name="PP-OCRv5_mobile_rec",  # 👈 换轻量模型
                enable_mkldnn=True,
                cpu_threads=10
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
            all_files = os.listdir(self.data_folder)
            png_files = [f for f in all_files if f.endswith('.png')]
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
            start_time = time.time()
            self._log_message(f"开始处理图片: {image_file}")
            
            # 执行OCR识别
            result = self.ocr.predict(image_path)
            
            # 修正2: 采用官方推荐的结果解析方式
            recognized_text = ""
            if result and len(result) > 0:
                res = result[0]
                # 使用官方推荐的方法处理结果
                try:
                    # 如果结果对象有json属性，尝试从中获取文本
                    if hasattr(res, 'json'):
                        result_json = res.json
                        if 'res' in result_json and 'rec_texts' in result_json['res']:
                            # 使用两个换行符连接，形成更好的段落分隔
                            recognized_text = "\n\n".join(result_json['res']['rec_texts'])
                    # 如果结果对象有rec_texts属性，直接使用
                    elif hasattr(res, 'rec_texts'):
                        # 使用两个换行符连接，形成更好的段落分隔
                        recognized_text = "\n\n".join(res.rec_texts)
                    # 回退到旧的解析方式
                    else:
                        recognized_lines = [
                            line[1][0] for line in res
                        ]
                        # 使用两个换行符连接，形成更好的段落分隔
                        recognized_text = "\n\n".join(recognized_lines)
                except Exception as e:
                    # 如果以上方法都失败，记录错误并使用空文本
                    self._log_message(f"结果解析失败: {str(e)}")
                    recognized_text = ""
            
            # 进一步处理文本，移除多余的空白行并规范化段落
            if recognized_text:
                # 将多个连续的换行符替换为两个换行符（段落分隔）
                import re
                recognized_text = re.sub(r'\n{3,}', '\n\n', recognized_text)
                # 移除行首行尾的空白字符
                recognized_text = recognized_text.strip()
                # 进一步优化段落格式
                lines = recognized_text.split('\n')
                processed_lines = []
                for line in lines:
                    # 移除行首行尾的空白字符
                    line = line.strip()
                    # 如果行不为空，则添加到结果中
                    if line:
                        processed_lines.append(line)
                    # 如果行为空且结果中最后一个元素不是空行，则添加一个空行作为段落分隔
                    elif processed_lines and processed_lines[-1] != "":
                        processed_lines.append("")
                # 重新组合文本
                recognized_text = "\n".join(processed_lines)
            
            processing_time = time.time() - start_time
            self._log_message(f"✅ 图片 {image_file} 处理完成，耗时 {processing_time:.2f} 秒")
            
            # 修正3: 修复f-string语法错误，并安全地记录日志
            log_preview = recognized_text.replace('\n', ' ')
            if len(log_preview) > 50:
                log_content = f"{log_preview[:50]}..."
            else:
                log_content = log_preview
            self._log_message(f"识别内容: {log_content}")
            
            return recognized_text.strip()
            
        except Exception as e:
            error_msg = f"❌ 处理图片 {image_file} 失败: {str(e)}"
            self._log_message(error_msg)
            print(f"\n{error_msg}")
            return ""
    
    def _save_results(self, results):
        """保存识别结果到Markdown文件"""
        try:
            self._log_message("开始保存识别结果到Markdown文件")
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# 中国文学史名词解释\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
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
        
        image_files = self._get_image_files()
        total_images = len(image_files)
        
        if total_images == 0:
            self._log_message("❌ 未找到任何PNG图片文件")
            print("❌ 未找到任何PNG图片文件")
            return
        
        test_image_files = [f for f in image_files if f in ['0032.png', '0033.png', '0034.png', '0035.png']]
        if test_image_files:
            image_files = test_image_files
            total_images = len(image_files)
            self._log_message(f"筛选出 {total_images} 张测试图片: {', '.join(image_files)}")
            print(f"📝 筛选出 {total_images} 张测试图片: {', '.join(image_files)}")
        
        print(f"📊 总共需要处理 {total_images} 张图片")
        print(f"📝 日志文件: {self.log_file}")
        print(f"📄 输出文件: {self.output_file}")
        print("=" * 60)
        
        results = []
        self._log_message("开始按顺序逐张处理图片")
        print("🔄 开始按顺序逐张处理图片")
        
        # 按顺序逐张处理图片，避免多线程带来的顺序问题
        for image_file in image_files:
            try:
                recognized_text = self._process_single_image(image_file)
                results.append((image_file, recognized_text))
            except Exception as e:
                error_msg = f"❌ 处理图片 {image_file} 时发生异常: {str(e)}"
                self._log_message(error_msg)
                print(f"\n{error_msg}")
                results.append((image_file, ""))

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
        processor = OCRProcessor()
        processor.process_all_images()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()