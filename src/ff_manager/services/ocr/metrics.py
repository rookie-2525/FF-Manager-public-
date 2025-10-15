# # services/ocr/metrics.py
# from rapidfuzz.distance import Levenshtein

# def cer(pred: str, truth: str) -> float:
#     if not truth: return 1.0 if pred else 0.0
#     dist = Levenshtein.distance(pred, truth)
#     return dist / len(truth)

# def wer(pred: str, truth: str) -> float:
#     p = pred.split()
#     t = truth.split()
#     if not t: return 1.0 if p else 0.0
#     dist = Levenshtein.distance(p, t)  # シーケンス距離
#     return dist / len(t)
