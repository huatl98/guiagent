import os
from paddleocr import PaddleOCR

def main():
    output_dir = "output"  # 这是相对路径

    os.makedirs(output_dir, exist_ok=True)  # 会在当前工作目录下创建

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )

    img_url = "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/general_ocr_002.png"

    result = ocr.predict(input=img_url)

    for res in result:
        res.print()
        res.save_to_json(output_dir)

    print(f"OCR 结果已保存到: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
