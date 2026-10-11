import glob
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform as warp
from app.feature_stack import build_feature_stack, find_months, get_grid, FEATURE_NAMES, DATA_DIR
from app.model import load_model

window = (1670, 835, 100, 100)
r0, c0, h, w = window
win = Window(c0, r0, w, h)

features, meta = build_feature_stack(window=window)
months = find_months()

ndvi, ndwi, lulc = [], [], []
for m in months:
    with rasterio.open(m["ndvi"]) as f:
        ndvi.append(f.read(1, window=win).astype("float64"))
    with rasterio.open(m["ndwi"]) as f:
        ndwi.append(f.read(1, window=win).astype("float64"))
    with rasterio.open(m["lulc"]) as f:
        lulc.append(f.read(1, window=win))
ndvi, ndwi, lulc = np.array(ndvi), np.array(ndwi), np.array(lulc)
valid = lulc != 255
raw = {
    "ndvi_mean": np.nanmean(ndvi, axis=0),
    "ndwi_mean": np.nanmean(ndwi, axis=0),
    "built_up_pct_mean": (lulc == 0).sum(0) / np.maximum(valid.sum(0), 1) * 100,
    "vegetation_pct_mean": (lulc == 1).sum(0) / np.maximum(valid.sum(0), 1) * 100,
}
print("A) features vs raw rasters (max abs diff over", h * w, "pixels)")
for k in raw:
    print("  ", k, round(float(np.nanmax(np.abs(raw[k] - features[k]))), 5))

model, info = load_model()
df = np.column_stack([features[f].ravel() for f in FEATURE_NAMES])
ok = ~np.isnan(df).any(axis=1)
score = model.predict(df[ok])

transform, shape, crs = get_grid()
rr, cc = np.divmod(np.arange(h * w), w)
x, y = rasterio.transform.xy(meta_t := rasterio.Affine(*meta["transform"]), rr, cc)
lon, lat = warp(crs, "EPSG:4326", x, y)
lst_files = sorted(glob.glob(DATA_DIR + "/lst_30m_monthly/*/*.tif"))
lst = []
for p in lst_files:
    with rasterio.open(p) as f:
        v = np.array([a[0] for a in f.sample(zip(lon, lat))], dtype="float64")
    v[v == 0] = np.nan
    lst.append(v)
lst = np.nanmean(lst, axis=0)[ok]
good = ~np.isnan(lst)
print("B) model score vs mean LST from", len(lst_files), "months,", int(good.sum()), "pixels")
print("   pearson r:", round(float(np.corrcoef(score[good], lst[good])[0, 1]), 3))
from scipy.stats import spearmanr
print("   spearman r:", round(float(spearmanr(score[good], lst[good])[0]), 3))
