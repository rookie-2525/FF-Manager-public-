# tests_scripts/ocr/paddle_table.py
import cv2
from ff_manager.services.ocr.paddle_engine_table import PaddleTableEngine


def main():
    img_path = "tests/assets/sample_2024_12_18.png"  # テスト画像パス
    output_path = "tests/assets/output.png"  # テスト画像パス
    ocr = PaddleTableEngine(lang="japan", use_gpu=True)

    print("OCR running...")
    ocr.run(img_path,output_path)
    print("Done")



if __name__ == "__main__":
    main()
