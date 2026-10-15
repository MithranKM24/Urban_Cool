import hashlib
import json
from typing import Any, Dict, Tuple

import numpy as np
import rasterio.features
import rasterio.transform
import rasterio.windows
from rasterio.windows import Window
from shapely.geometry import shape


REGIONS: Dict[str, Dict[str, np.ndarray]] = {}


def get_region(region_geojson: Dict[str, Any], meta: Dict[str, Any]) -> Tuple[str, Dict[str, np.ndarray]]:
    geometry = region_geojson.get("geometry", region_geojson)
    polygon = shape(geometry)
    if polygon.geom_type != "Polygon" or polygon.is_empty or not polygon.is_valid:
        raise ValueError("Region must be a valid GeoJSON Polygon.")

    transform = rasterio.transform.Affine(*meta["transform"])
    height, width = int(meta["height"]), int(meta["width"])
    min_x, min_y, max_x, max_y = polygon.bounds
    top, left = rasterio.transform.rowcol(transform, min_x, max_y, op=np.floor)
    bottom, right = rasterio.transform.rowcol(transform, max_x, min_y, op=np.ceil)
    top = max(0, min(height, int(top)))
    bottom = max(0, min(height, int(bottom) + 1))
    left = max(0, min(width, int(left)))
    right = max(0, min(width, int(right) + 1))
    if bottom <= top or right <= left:
        rows, cols = np.array([], dtype=np.int32), np.array([], dtype=np.int32)
    else:
        window_transform = rasterio.windows.transform(Window(left, top, right - left, bottom - top), transform)
        inside = rasterio.features.geometry_mask([polygon.__geo_interface__], out_shape=(bottom - top, right - left), transform=window_transform, invert=True)
        local_rows, local_cols = np.where(inside)
        rows, cols = local_rows + top, local_cols + left

    region_id = hashlib.sha1(json.dumps(region_geojson, sort_keys=True).encode()).hexdigest()[:16]
    region = {"rows": rows.astype(np.int32), "cols": cols.astype(np.int32)}
    REGIONS[region_id] = region
    return region_id, region


def find_region(region_id: str) -> Dict[str, np.ndarray]:
    if region_id not in REGIONS:
        raise KeyError("Unknown or expired region: " + region_id)
    return REGIONS[region_id]
