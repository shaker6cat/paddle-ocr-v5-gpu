from paddleocr import PaddleOCR

ocr = PaddleOCR()
result = ocr.predict("0032.png")

# 取第一个识别结果对象
res = result[0]

# 打印类型
print(type(res))

# 打印对象所有属性
print(res.__dict__)
