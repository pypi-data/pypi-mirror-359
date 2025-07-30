from bert_score import score
from typing import List, Dict

def evaluate_summary_bert_score(
    candidates: List[str],
    references: List[str],
    model_type: str = "xlm-roberta-base",
    lang: str = "vi",
    rescale_with_baseline: bool = False,
    num_layers: int = 12  # ✅ tránh KeyError
) -> Dict[str, List[float]]:
    if len(candidates) != len(references):
        raise ValueError("Số lượng candidates và references phải bằng nhau.")

    P, R, F1 = score(
        cands=candidates,
        refs=references,
        model_type=model_type,
        lang=lang,
        verbose=True,
        rescale_with_baseline=rescale_with_baseline,
        num_layers=num_layers  # ✅ fix lỗi KeyError
    )

    return {
        "precision": [round(p.item(), 4) for p in P],
        "recall": [round(r.item(), 4) for r in R],
        "f1": [round(f.item(), 4) for f in F1]
    }
