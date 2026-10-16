import sys
import numpy as np
import pandas as pd
import rasterio
import rasterio.windows
import geopandas as gpd
from rasterio.windows import Window
from shapely.geometry import box
from app.feature_stack import build_feature_stack, find_months, get_grid, FEATURE_NAMES, BUILDINGS_PATH, WINDOW, PIXEL

window = (1670, 835, 100, 100)
if len(sys.argv) == 5:
    window = tuple(int(a) for a in sys.argv[1:])
r0, c0, h, w = window

features, meta = build_feature_stack(window=window)
transform, shape, crs = get_grid()

rr, cc = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
rr, cc = rr.ravel(), cc.ravel()
x, y = rasterio.transform.xy(rasterio.Affine(*meta["transform"]), rr, cc)
out = pd.DataFrame({"grid_row": rr + r0, "grid_col": cc + c0, "x": x, "y": y})
for f in FEATURE_NAMES:
    out[f] = features[f][rr, cc]
out.to_csv("subset_features.csv", index=False)
print("\nSaved", len(out), "pixels x", len(FEATURE_NAMES), "features to subset_features.csv")

months = find_months()
buildings = gpd.read_file(BUILDINGS_PATH).to_crs(crs)
centers = buildings.geometry.centroid
rng = np.random.default_rng(1)
for i in rng.choice(len(out), 3, replace=False):
    gr, gc = int(out.grid_row[i]), int(out.grid_col[i])
    print("\n==== pixel row", gr, "col", gc, "(x", round(out.x[i], 1), "y", round(out.y[i], 1), ") ====")
    nd, nw, lu = [], [], []
    px = Window(gc, gr, 1, 1)
    for m in months:
        with rasterio.open(m["ndvi"]) as f:
            nd.append(float(f.read(1, window=px)[0, 0]))
        with rasterio.open(m["ndwi"]) as f:
            nw.append(float(f.read(1, window=px)[0, 0]))
        with rasterio.open(m["lulc"]) as f:
            lu.append(int(f.read(1, window=px)[0, 0]))
    print("month    ndvi    ndwi   lulc(0=built,1=veg,2=water,255=nodata)")
    for k in range(len(months)):
        print(months[k]["name"], " ", round(nd[k], 3), " ", round(nw[k], 3), " ", lu[k])
    lv = [v for v in lu if v != 255]
    print("raw   ndvi mean:", round(float(np.nanmean(nd)), 4), " extracted:", round(float(out.ndvi_mean[i]), 4))
    print("raw   ndwi mean:", round(float(np.nanmean(nw)), 4), " extracted:", round(float(out.ndwi_mean[i]), 4))
    print("raw   built-up %:", round(lv.count(0) / len(lv) * 100, 2), " extracted:", round(float(out.built_up_pct_mean[i]), 2))

    half = WINDOW // 2
    left, bottom, right, top = rasterio.windows.bounds(Window(gc - half, gr - half, WINDOW, WINDOW), transform)
    count = int(centers.within(box(left, bottom, right, top)).sum())
    print("raw   buildings in 9x9 box:", count, "-> per km2:", round(count / ((WINDOW * PIXEL) ** 2 / 1e6), 1), " extracted:", round(float(out.building_density_per_km2[i]), 1))
