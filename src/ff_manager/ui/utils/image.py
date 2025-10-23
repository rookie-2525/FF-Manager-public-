# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
import numpy as np

try:
    from PySide6.QtGui import QImage
except Exception as e:
    QImage = None  # 型ヒント用のフォールバック
from PySide6 import QtGui


def qimage_to_ndarray(
    qimg: QtGui.QImage,
    *,
    as_bgr: bool = True,
    copy: bool = True,
) -> np.ndarray:
    """
    QImage -> numpy.ndarray (H, W, C), dtype=uint8
    - デフォルトで OpenCV/Paddle 想定の BGR チャンネル順にします (as_bgr=True)。
    - α付き(QImage.Format_ARGB32 など)は 4ch のまま返します（C=4）。
      ※ as_bgr=True の場合は BGRA 順になります。
    - copy=False にすると QImage の裏メモリを参照するビューを返す（寿命に注意）。

    Parameters
    ----------
    qimg : QImage
    as_bgr : bool
        True なら RGB→BGR / RGBA→BGRA の順に並べ替えます。
    copy : bool
        True なら安全のため numpy 側に完全コピー（QImage解放の影響を受けない）。

    Returns
    -------
    np.ndarray
        shape=(H, W, C), dtype=uint8
    """
    if qimg is None:
        raise ValueError("qimage_to_ndarray: qimg is None")
    if qimg.isNull():
        raise ValueError("qimage_to_ndarray: qimg isNull()")

    fmt = qimg.format()
    w = qimg.width()
    h = qimg.height()
    bpl = qimg.bytesPerLine()  # バイト/行（行パディングを含む）

    # QImage.bits() は sip.voidptr を返す→Python側でバッファとして扱う
    ptr = qimg.bits()
    ptr.setsize(h * bpl)
    arr = np.frombuffer(ptr, dtype=np.uint8)

    # 主要フォーマットを分岐
    # 参考: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QImage.html#PySide6.QtGui.PySide6.QtGui.QImage.Format
    if fmt in (QImage.Format.Format_RGB888,):
        # 1行が bpl バイト、実データは 3ch
        arr = arr.reshape((h, bpl))[:, : w * 3]          # 行パディングを除去
        arr = arr.reshape((h, w, 3))                     # HWC
        if as_bgr:
            arr = arr[:, :, ::-1]                        # RGB -> BGR

    elif fmt in (
        QImage.Format.Format_ARGB32,
        QImage.Format.Format_ARGB32_Premultiplied,
        QImage.Format.Format_RGBA8888,
        QImage.Format.Format_RGBA8888_Premultiplied,
    ):
        # 4ch: ARGB32/RGBA8888 系はメモリ上の並びが実装依存で紛らわしいが、
        # Qt6 は RGBA として解釈できる配置になることが多い。
        # → まず4chとして整形し、必要なら RGBA->BGRA に並べ替え。
        arr = arr.reshape((h, bpl))[:, : w * 4]
        arr = arr.reshape((h, w, 4))
        if as_bgr:
            # RGBA -> BGRA（RとBを入れ替えるだけ、Aはそのまま末尾）
            arr = arr[:, :, [2, 1, 0, 3]]

    elif fmt in (QImage.Format.Format_Grayscale8,):
        # 1ch（グレースケール）。呼び出し側が3chを想定することが多いので、3chに展開する。
        arr = arr.reshape((h, bpl))[:, : w]              # 1ch * W
        arr = arr.reshape((h, w, 1))
        arr = np.repeat(arr, 3, axis=2)                  # → (H, W, 3)
        # as_bgr の概念は 3chと同じ（同一値なので並べ替えの必要なし）

    else:
        # あまり使われない/未対応のフォーマットは、とりあえず 32bit として読む
        # → RGBA と見なして 4chにし、必要なら BGRA へ並べ替え。
        arr = arr.reshape((h, bpl))[:, : w * 4]
        arr = arr.reshape((h, w, 4))
        if as_bgr:
            arr = arr[:, :, [2, 1, 0, 3]]

    # copy=True なら独立コピーにして QImage 解放の影響を避ける
    if copy:
        arr = arr.copy()

    return arr


def ndarray_to_qimage(img: np.ndarray) -> QtGui.QImage:
    """
    numpy.ndarray (H, W, C) -> QImage
    - C=3 は BGR または RGB を想定（自動推定できないので RGB が欲しい場合は呼び出し側で変換してから渡すのが安全）
    - C=4 は BGRA または RGBA を想定
    - dtype=uint8 のみ対応
    """
    from PySide6.QtGui import QImage

    if img.dtype != np.uint8:
        raise ValueError("ndarray_to_qimage: dtype must be uint8")
    if img.ndim != 3 or img.shape[2] not in (3, 4):
        raise ValueError("ndarray_to_qimage: shape must be (H, W, 3|4)")

    h, w, c = img.shape

    if c == 3:
        # ここでは RGB 前提の QImage を作る（BGR を渡す場合は事前に RGB へ変換しておく）
        rgb = img[:, :, ::-1].copy()  # BGR->RGB 変換（必要なら）
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888)
        # QImage はデフォルトでは外部メモリ参照になるため、deep copy して独立させる
        return qimg.copy()

    else:  # c == 4
        # BGRA -> RGBA へ（必要なら）入れ替え
        rgba = img[:, :, [2, 1, 0, 3]].copy()  # BGRA->RGBA
        qimg = QImage(rgba.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
        return qimg.copy()
