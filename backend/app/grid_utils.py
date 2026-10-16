import numpy as np
import pandas as pd

MAX_UNAGGREGATED_PIXELS = 800000


def affine_pixel_centers_to_lonlat(transform, rows, cols):
    rows_c = np.asarray(rows, dtype=np.float64) + 0.5
    cols_c = np.asarray(cols, dtype=np.float64) + 0.5
    lon = transform.a * cols_c + transform.b * rows_c + transform.c
    lat = transform.d * cols_c + transform.e * rows_c + transform.f
    return lon, lat


def build_grid_geojson(row_indices, col_indices, transform, metric_arrays_by_name, max_features=MAX_UNAGGREGATED_PIXELS):
    row_indices = np.asarray(row_indices)
    col_indices = np.asarray(col_indices)
    n_pixels = len(row_indices)
    aggregated = n_pixels > max_features
    cell_size_meters = 10.0
    names = list(metric_arrays_by_name.keys())

    if aggregated:
        aggregation_factor = int(np.ceil(np.sqrt(n_pixels / max_features)))
        cell_size_meters = 10.0 * aggregation_factor
        agg_row = row_indices // aggregation_factor
        agg_col = col_indices // aggregation_factor
        df = pd.DataFrame({"key_row": agg_row, "key_col": agg_col})
        for name in names:
            df[name] = metric_arrays_by_name[name]
        grouped = df.groupby(["key_row", "key_col"], as_index=False).mean()
        center_row = grouped["key_row"].to_numpy() * aggregation_factor + aggregation_factor / 2.0
        center_col = grouped["key_col"].to_numpy() * aggregation_factor + aggregation_factor / 2.0
        lon_arr, lat_arr = affine_pixel_centers_to_lonlat(transform, center_row, center_col)
        value_columns = [grouped[name].to_numpy() for name in names]
    else:
        lon_arr, lat_arr = affine_pixel_centers_to_lonlat(transform, row_indices, col_indices)
        value_columns = [np.asarray(metric_arrays_by_name[name], dtype=np.float64) for name in names]

    valid_mask = np.ones(len(lon_arr), dtype=bool)
    for col in value_columns:
        valid_mask &= ~pd.isna(col)

    lon_list = np.round(lon_arr[valid_mask], 6).tolist()
    lat_list = np.round(lat_arr[valid_mask], 6).tolist()
    value_lists = [np.round(col[valid_mask], 4).tolist() for col in value_columns]

    features = []
    for i in range(len(lon_list)):
        props = {names[j]: value_lists[j][i] for j in range(len(names))}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon_list[i], lat_list[i]]},
            "properties": props,
        })

    return {"type": "FeatureCollection", "features": features}, aggregated, cell_size_meters
