from bert_score import score
from typing import List, Dict, Optional

def evaluate_summary_bert_score(
    candidates: List[str],
    references: List[str],
    model_type: str = "xlm-roberta-base",
    lang: str = "vi",
    rescale_with_baseline: bool = False,
    num_layers: Optional[int] = None  # ✅ Cho phép None
) -> Dict[str, List[float]]:
    if len(candidates) != len(references):
        raise ValueError("Số lượng candidates và references phải bằng nhau.")

    # ✅ Tự gán số layers phù hợp nếu chưa truyền
    if num_layers is None:
        default_layers = {
            "vinai/phobert-base": 12,
            "xlm-roberta-base": 12,
            "bert-base-multilingual-cased": 12,
            "distilbert-base-multilingual-cased": 6,
            # Thêm mô hình nếu cần
        }
        if model_type in default_layers:
            num_layers = default_layers[model_type]
        else:
            raise ValueError(f"Vui lòng chỉ định num_layers cho mô hình không hỗ trợ: {model_type}")

    P, R, F1 = score(
        cands=candidates,
        refs=references,
        model_type=model_type,
        lang=lang,
        verbose=True,
        rescale_with_baseline=rescale_with_baseline,
        num_layers=num_layers
    )

    return {
        "precision": [round(p.item(), 4) for p in P],
        "recall": [round(r.item(), 4) for r in R],
        "f1": [round(f.item(), 4) for f in F1]
    }
