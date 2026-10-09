import numpy as np
import pandas as pd

MAX_POINTS = 800000


def pixel_to_lonlat(transform, rows, cols):
    rows = np.asarray(rows, dtype=np.float64) + 0.5
    cols = np.asarray(cols, dtype=np.float64) + 0.5
    lon = transform.a * cols + transform.b * rows + transform.c
    lat = transform.d * cols + transform.e * rows + transform.f
    return lon, lat


def make_grid(rows, cols, transform, values, max_points=MAX_POINTS):
    rows = np.asarray(rows)
    cols = np.asarray(cols)
    n = len(rows)
    names = list(values.keys())

    aggregated = n > max_points
    cell_size = 10.0

    if aggregated:
        factor = int(np.ceil(np.sqrt(n / max_points)))
        cell_size = 10.0 * factor

        df = pd.DataFrame({"block_row": rows // factor, "block_col": cols // factor})
        for name in names:
            df[name] = values[name]
        blocks = df.groupby(["block_row", "block_col"], as_index=False).mean()

        center_row = blocks["block_row"].to_numpy() * factor + factor / 2.0
        center_col = blocks["block_col"].to_numpy() * factor + factor / 2.0
        lon, lat = pixel_to_lonlat(transform, center_row, center_col)
        columns = [blocks[name].to_numpy() for name in names]
    else:
        lon, lat = pixel_to_lonlat(transform, rows, cols)
        columns = [np.asarray(values[name], dtype=np.float64) for name in names]

    keep = np.ones(len(lon), dtype=bool)
    for c in columns:
        keep = keep & ~pd.isna(c)

    lon = np.round(lon[keep], 6).tolist()
    lat = np.round(lat[keep], 6).tolist()
    columns = [np.round(c[keep], 4).tolist() for c in columns]

    features = []
    for i in range(len(lon)):
        props = {}
        for j in range(len(names)):
            props[names[j]] = columns[j][i]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon[i], lat[i]]},
            "properties": props,
        })

    return {"type": "FeatureCollection", "features": features}, aggregated, cell_size
