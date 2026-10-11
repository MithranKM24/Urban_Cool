import time
import numpy as np
from app.feature_stack import build_feature_stack, FEATURE_NAMES
from app.model import load_model
from app.simulator import simulate, INTERVENTIONS

window = (1670, 835, 100, 100)

t = time.time()
features, meta = build_feature_stack(window=window)
print("\nExtracted", len(FEATURE_NAMES), "features on the spot for", meta["height"], "x", meta["width"], "pixels in", round(time.time() - t, 1), "s")
for f in FEATURE_NAMES:
    a = features[f]
    print("  ", f, "min", round(float(np.nanmin(a)), 3), "mean", round(float(np.nanmean(a)), 3), "max", round(float(np.nanmax(a)), 3))

model, info = load_model()
rows, cols = np.meshgrid(np.arange(meta["height"]), np.arange(meta["width"]), indexing="ij")
rows, cols = rows.ravel(), cols.ravel()
print("\nSimulator on the subset")
for name in INTERVENTIONS:
    res = simulate(features, meta, model, rows, cols, name, 3)
    print("  ", name, "- mean score drop:", round(res["mean"], 3))

full, _ = build_feature_stack()
r0, c0, h, w = window
for f in FEATURE_NAMES:
    d = np.nanmax(np.abs(full[f][r0:r0 + h, c0:c0 + w] - features[f]))
    print("check", f, "max diff vs full grid:", round(float(d), 4))
