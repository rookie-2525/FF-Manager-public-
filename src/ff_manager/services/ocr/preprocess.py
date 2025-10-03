# services/ocr/preprocess.py
import cv2
import numpy as np

def _deskew(gray: np.ndarray) -> np.ndarray:
    # 2値化→白黒反転→回転角推定→回転
    thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    thr = cv2.bitwise_not(thr)
    coords = np.column_stack(np.where(thr > 0))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def preprocess_for_ocr(bgr: np.ndarray) -> np.ndarray:
    # 1) グレースケール
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # 2) 軽いノイズ除去
    gray = cv2.fastNlMeansDenoising(gray, None, h=15)
    # 3) 傾き補正
    gray = _deskew(gray)
    # 4) 局所的二値化（薄い文字に強い）
    bin_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 35, 11
    )
    # 5) 細いゴミを除去（モルフォロジー開運算）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel, iterations=1)
    return bin_img
