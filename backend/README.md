# Backend (Feature Engineering, Model, API)

This part builds the feature stack from the raw rasters, trains the
CatBoost heat vulnerability model, runs the intervention simulator,
and exposes the region-analysis API route.

## Layout

```
app/
  feature_stack.py   builds the 10m feature stack and caches it
  model.py            trains and loads the CatBoost model
  simulator.py         applies interventions and ranks their effect
  api/
    routes.py          FastAPI route for region analysis
```

## Setup

```
pip install -r requirements.txt
```
