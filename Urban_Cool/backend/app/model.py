import os
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from catboost import CatBoostRegressor

from app.feature_stack import FEATURE_NAMES, ROOT, build_feature_stack

MODEL_DIR = os.path.join(ROOT, "backend", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "heat_vulnerability_native10m.cbm")
INFO_PATH = os.path.join(MODEL_DIR, "heat_vulnerability_native10m_metadata.npz")

CORR_LIMIT = 0.5
STRUCTURAL = ["built_up_pct_mean", "building_density_per_km2", "road_density_km_per_km2"]
COOLING = ["ndvi_mean", "ndwi_mean", "albedo_mean"]

BATCH_SIZE = 500000
THREADS = 6

TREES = 150
RATE = 0.05
DEPTH = 6

TEST_SIZE = 0.2
SEED = 42


def normalize(arr):
    low = np.nanmin(arr)
    high = np.nanmax(arr)
    if high - low < 1e-9:
        return np.zeros_like(arr)
    return (arr - low) / (high - low)


def flatten_features(features):
    print("Making the pixel table...")
    data = {}
    for f in FEATURE_NAMES:
        data[f] = features[f].ravel()
    df = pd.DataFrame(data)

    valid = df[["ndvi_mean", "built_up_pct_mean", "albedo_mean"]].notna().all(axis=1)
    print("Valid pixels:", int(valid.sum()), "of", len(df))

    df = df.loc[valid].reset_index(drop=True)
    for f in FEATURE_NAMES:
        df[f] = df[f].fillna(df[f].median())
    return df


def avg_correlation(corr, cols):
    n = len(cols)
    small = corr.loc[cols, cols]
    total = np.abs(small.values).sum() - n
    return total / (n * (n - 1))


def get_weights(df):
    print("Finding the correlations...")
    corr = df[STRUCTURAL + COOLING].corr()
    print(corr.round(3).to_string())

    struct_corr = avg_correlation(corr, STRUCTURAL)
    cooling_corr = avg_correlation(corr, COOLING)
    print("Structural correlation:", round(struct_corr, 3), "Cooling correlation:", round(cooling_corr, 3))

    struct_weight = 1.0 / len(STRUCTURAL)
    if struct_corr > CORR_LIMIT:
        struct_weight = 0.5 / len(STRUCTURAL)

    cooling_weight = 1.0 / len(COOLING)
    if cooling_corr > CORR_LIMIT:
        cooling_weight = 0.5 / len(COOLING)

    weights = {
        "built_up_pct_mean": struct_weight,
        "building_density_per_km2": struct_weight,
        "road_density_km_per_km2": struct_weight,
        "ndvi_mean": -cooling_weight,
        "ndwi_mean": -cooling_weight,
        "albedo_mean": -cooling_weight,
    }
    print("Weights:", weights)
    return weights, corr, struct_corr, cooling_corr


def make_index(df, weights):
    total = 0
    for col in weights:
        total = total + normalize(df[col].values) * weights[col]
    total = pd.Series(total)
    total = total - total.min()
    return total / total.max() * 100.0


def train_in_batches(x_train, y_train):
    print("Training on", len(x_train), "pixels...")
    batches = int(np.ceil(len(x_train) / BATCH_SIZE))
    model = None
    start = time.time()

    for b in range(batches):
        first = b * BATCH_SIZE
        last = min(first + BATCH_SIZE, len(x_train))

        new_model = CatBoostRegressor(
            iterations=TREES,
            learning_rate=RATE,
            depth=DEPTH,
            loss_function="RMSE",
            thread_count=THREADS,
            verbose=False,
            random_state=SEED,
        )
        if model is None:
            new_model.fit(x_train.iloc[first:last], y_train.iloc[first:last])
        else:
            new_model.fit(x_train.iloc[first:last], y_train.iloc[first:last], init_model=model)
        model = new_model

        print("Batch", b + 1, "of", batches, "done,", round(time.time() - start, 1), "seconds")
    return model


def train_model(rebuild=False):
    features, meta = build_feature_stack(rebuild)
    df = flatten_features(features)

    weights, corr, struct_corr, cooling_corr = get_weights(df)
    df["heat_vulnerability_index"] = make_index(df, weights)

    x = df[FEATURE_NAMES]
    y = df["heat_vulnerability_index"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=TEST_SIZE, random_state=SEED)
    print("Train:", len(x_train), "Test:", len(x_test))

    model = train_in_batches(x_train, y_train)

    predicted = model.predict(x_test)
    r2 = r2_score(y_test, predicted)
    mae = mean_absolute_error(y_test, predicted)
    print("R2:", round(r2, 4), "MAE:", round(mae, 4))

    importance = pd.DataFrame({"feature": FEATURE_NAMES, "importance": model.get_feature_importance()})
    importance = importance.sort_values("importance", ascending=False)
    print(importance.to_string(index=False))

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_model(MODEL_PATH)

    info = {
        "r_squared": r2,
        "mae": mae,
        "n_train": len(x_train),
        "n_test": len(x_test),
        "weights": weights,
        "mean_struct_corr": struct_corr,
        "mean_cooling_corr": cooling_corr,
        "feature_names": FEATURE_NAMES,
        "importance": importance.to_dict(orient="records"),
        "self_consistency_caveat": (
            "The target is a deterministic formula built from features this model also trains on. "
            "A high R-squared confirms correct formula reconstruction, not external predictive skill on unseen ground truth."
        ),
    }
    np.savez(INFO_PATH, metadata=np.array([info], dtype=object))
    print("Saved the model and info")
    return model, info


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("No model found at " + MODEL_PATH + ", run train_model() first")
    model = CatBoostRegressor()
    model.load_model(MODEL_PATH)
    info = np.load(INFO_PATH, allow_pickle=True)["metadata"][0]
    return model, info
