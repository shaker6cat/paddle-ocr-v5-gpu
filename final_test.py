#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试GPU版本PaddleOCR功能
"""

import os
from paddleocr import PaddleOCR

def test_ocr():
    print("开始测试GPU版本PaddleOCR...")
    
    # 初始化OCR (GPU模式)
    ocr = PaddleOCR(lang='ch', device='gpu:0')
    print("✅ PaddleOCR GPU版本初始化成功")
    
    # 测试图片
    test_image = "/home/featurize/data/0032.png"
    
    if os.path.exists(test_image):
        print(f"正在处理测试图片: {test_image}")
        
        # 执行OCR识别
        result = ocr.ocr(test_image, use_textline_orientation=True)
        
        if result and result[0]:
            ocr_result = result[0]
            print("✅ OCR识别成功")
            
            # 获取识别的文字
            texts = ocr_result.get('rec_texts', [])
            scores = ocr_result.get('rec_scores', [])
            
            print(f"识别到 {len(texts)} 行文字:")
            for i in range(min(5, len(texts))):  # 只显示前5行
                print(f"  {texts[i]} (置信度: {scores[i]:.2f})")
                
            # 保存结果到文件
            output_file = "/home/featurize/data/test_result.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# OCR识别结果\n\n")
                f.write(f"图片: {test_image}\n\n")
                f.write("---\n\n")
                for text in texts:
                    f.write(f"{text}\n")
            
            print(f"✅ 结果已保存到: {output_file}")
        else:
            print("❌ 未识别到文字")
    else:
        print(f"❌ 测试图片不存在: {test_image}")

if __name__ == "__main__":
    test_ocr()