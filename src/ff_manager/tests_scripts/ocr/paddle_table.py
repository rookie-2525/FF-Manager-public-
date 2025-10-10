# tests_scripts/ocr/paddle_table.py
import cv2
from pathlib import Path
import numpy as np
from PIL import Image
from ff_manager.services.ocr.paddle_engine_table import PaddleTableEngine
from ff_manager.services.ocr.preprocess import preprocess_for_ocr,_deskew


def main():
    img_path = "tests/assets/sample_2024_12_18.png"  # テスト画像パス
    output_path = "tests/assets/output/"  # テスト画像パス
    output_pre_img_path = "tests/assets/output/pre_img/img_0.png"  # テスト画像パス
    # ocr = PaddleTableEngine()

    pil_img=Image.open(img_path).convert("RGB")


    # 前処理
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    img=preproc(pil_img,output_pre_img_path)





def crop_tablet_screen(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150)

    # 輪郭を抽出
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:  # 4点ならタブレットの枠とみなす
            pts = np.array([p[0] for p in approx], dtype="float32")
            break
    else:
        print("[WARN] 四角形が検出できませんでした")
        return img

    # 台形補正（透視変換）
    (tl, tr, br, bl) = pts
    width = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    height = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (int(width), int(height)))

    print("[INFO] タブレット画面を抽出しました")
    return warped

def preproc(pil_img,out_img_path):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    #グレースケール
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ノイズ除去
    # img = cv2.fastNlMeansDenoising(img, None, h=15)

    # 傾き補正
    img = _deskew(img)

    
    # out = Path(out_img_path)
    # out.parent.mkdir(parents=True, exist_ok=True)  # フォルダ作成
    # cv2.imwrite(str(out), img)  # これで出力完了
    # cv2.imwrite(os.path.join(out_img_path,"preproc/img.png"), img)  # これで出力完了
    # cv2.imwrite("output/preproc/img.png", img)  # これで出力完了
    # print(f"[INFO] 前処理済み画像を保存しました → {out_img_path}")

    # save_path = Path(out_img_path) / "pre_img/img.png"

    ok = cv2.imwrite(str(out_img_path), img)
    if ok:
        print(f"[✅] 前処理済み画像を保存しました → {out_img_path}")
    else:
        print(f"[❌] 画像の保存に失敗しました。ディレクトリを確認してください → {out_img_path}")


    return img



if __name__ == "__main__":
    main()
