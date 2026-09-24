# Urban Cool

Urban Cool is an interactive heat-vulnerability planning tool for the Anna University–OMR–ECR corridor in Chennai. It combines a native 10 m geospatial feature stack with a machine-learning model to help users understand heat vulnerability in a selected area and compare possible cooling interventions.

The application is designed for exploration and planning. It makes the source data, assumptions, and limitations visible instead of presenting modeled results as measured outcomes.

## Highlights

- Draw a region directly on an interactive map.
- Explore heat vulnerability and seven supporting metric layers.
- See a plain-language explanation of the factors influencing a region’s score.
- Compare seven interventions ranked by their modeled improvement.
- Switch between before-and-after simulation layers.
- Inspect the locations within a region that benefit most from an intervention.
- View API documentation through FastAPI’s built-in OpenAPI interface.

## How it works

```text
┌──────────────────────────────┐
│ Next.js frontend              │
│ React · MapLibre · React Query│
└──────────────┬───────────────┘
               │ REST + GeoJSON
┌──────────────▼───────────────┐
│ FastAPI backend               │
│ scoring · SHAP · simulation   │
└──────────────┬───────────────┘
               │ reads cached data
┌──────────────▼───────────────┐
│ Native 10 m feature stack     │
│ satellite, land-cover, OSM    │
└──────────────────────────────┘
```

The backend owns geospatial processing, scoring, explanations, and intervention simulation. The frontend is responsible for interaction and visualization; it receives summaries and GeoJSON overlays rather than reading raw raster data.

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js and npm
- Git LFS, because the cached feature stack and model artifacts are large

Install the dependencies:

```bash
cd backend
python -m pip install -r requirements.txt

cd ../frontend
npm install
```

If the repository was cloned without Git LFS, fetch the large files before starting:

```bash
git lfs install
git lfs pull
```

### Start the full application

From the project root:

```bash
./run.sh
```

On Windows PowerShell:

```powershell
.\run.ps1
```

The launcher starts both services, waits for them to become healthy, and stops them together when you press `Ctrl+C`.

Once running:

- Frontend: <http://localhost:3000>
- Backend: <http://127.0.0.1:8000>
- API docs: <http://127.0.0.1:8000/docs>

### Start each service manually

Backend:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend, in a second terminal:

```bash
cd frontend
npm run dev
```

The frontend uses `http://127.0.0.1:8000` by default. To point it elsewhere, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## User flow

1. Click **Draw region**.
2. Drag a rectangle inside the dashed study-area boundary.
3. Wait for the region analysis and SHAP explanation to load.
4. Switch between metric layers using the panel on the right.
5. Review the intervention ranking and select an option.
6. Toggle between the before and after simulation layers.
7. Sort the location table to inspect the strongest modeled improvements.

## Metrics and interventions

The map supports these metrics:

- Heat Vulnerability
- NDVI
- NDWI
- Albedo
- Built-up percentage
- Building density
- Road density
- Built-up trend

The simulator evaluates all seven interventions for a selected region:

| Intervention | Modeled feature changes |
| --- | --- |
| Add Tree Cover | Increases NDVI across the region |
| Cool Roof | Increases albedo on built-up pixels |
| Add Green Space | Increases vegetation and water signals while reducing built-up percentage |
| Green Roof | Applies a smaller vegetation and albedo improvement to roof areas |
| Cool Pavement | Increases albedo where road density is meaningful |
| Water Feature | Increases water and vegetation signals while reducing built-up percentage |
| Reduce Density | Reduces building density and built-up percentage while increasing NDVI |

These are documented planning assumptions, not measured intervention outcomes for Chennai.

## Project structure

```text
backend/
├── app/
│   ├── api/routes.py       API endpoints
│   ├── feature_stack.py    Cached native-resolution feature data
│   ├── model.py            CatBoost model loading and prediction
│   ├── simulator.py        Intervention scenarios
│   └── main.py             FastAPI application entry point
├── cache/                  Pre-built feature stack
└── models/                 Trained model artifacts

frontend/
├── app/page.tsx            Page state and application wiring
├── components/
│   ├── MapView.tsx         Map and GeoJSON layers
│   ├── InterventionPanel.tsx
│   ├── ExplanationPanel.tsx
│   └── ui/                 Presentational components with no API calls
├── lib/api-client.ts       Typed backend request helpers
├── lib/api-types.ts        Generated OpenAPI types
└── lib/metrics.ts          Metric and intervention display metadata

unnecessary/
└── pipeline/               Offline data preparation and audit scripts
```

The offline pipeline is not run during a user request. The running API loads the prepared feature stack and model once at startup.

## API overview

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/v1/health` | `GET` | Reports model and cache status |
| `/api/v1/region/analyze` | `POST` | Analyzes a drawn GeoJSON polygon |
| `/api/v1/region/{region_id}/metrics/{metric_name}` | `GET` | Loads an additional metric layer on demand |
| `/api/v1/region/{region_id}/simulate` | `POST` | Scores one or more interventions |

The complete request and response schemas are available at `/docs` when the backend is running.

## Development

Frontend type-checking:

```bash
cd frontend
npx tsc --noEmit
```

Frontend linting:

```bash
npm run lint
```

The API types are generated from the backend’s OpenAPI schema:

```bash
cd frontend
npx openapi-typescript http://127.0.0.1:8000/openapi.json -o lib/api-types.ts
```

## Data and model notes

The feature stack was prepared offline from Sentinel-2, Landsat, ECOSTRESS, OpenStreetMap, and WorldPop-derived inputs. The live application does not download satellite data when a region is drawn.

The CatBoost model reconstructs the project’s heat-vulnerability index from the feature stack. Its reported test accuracy reflects reconstruction of that deterministic index; it is not evidence that the index predicts independently measured land-surface temperature.

For full source details, temporal coverage, resolution checks, and provenance, see [`DATA_REPORT.md`](DATA_REPORT.md).

## Limitations

- The heat-vulnerability index has not been validated against measured land-surface temperature.
- Intervention effect sizes are illustrative planning constants, not observed results.
- Region IDs are stored in memory and are lost when the backend restarts.
- Large regions can take longer to analyze because the service scores many native-resolution pixels and calculates SHAP explanations.
- The map is restricted to the Anna University–OMR–ECR study area represented by the cached data.

## Project status

This repository is an active prototype for data-informed urban heat planning. Review the source data, assumptions, and limitations before using results for real-world decisions.

