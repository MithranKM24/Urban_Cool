from dataclasses import dataclass
from typing import Any, Dict

import shap

from app.feature_stack import build_feature_stack
from app.model import load_model


@dataclass
class AppState:
    features: Dict[str, Any]
    meta: Dict[str, Any]
    model: Any
    model_info: Dict[str, Any]
    explainer: Any


_state: AppState | None = None


def get_state() -> AppState:
    global _state
    if _state is None:
        features, meta = build_feature_stack()
        model, model_info = load_model()
        _state = AppState(features=features, meta=meta, model=model, model_info=model_info, explainer=shap.TreeExplainer(model))
    return _state
