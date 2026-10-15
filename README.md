# AquaGeoAI Cape Town API

## Implemented in this starter version

- `GET /api/health`: API health check.
- `GET /api/v1/layers`: catalogue of implemented/planned layers.
- `GET /api/v1/rainfall/annual?year=2020`: mean of annual CHIRPS pixel totals over the City of Cape Town AOI.
- `GET /api/v1/rainfall/annual/map?year=2020`: creates a temporary Earth Engine raster tile URL for the MapLibre rainfall overlay.

The API requires Earth Engine authentication configured outside the source tree, a valid Cloud project ID, and read access to `projects/ee-ttgintamo/assets/City_of_Cape_Town`. The code assumes the AOI is an Earth Engine FeatureCollection. Verify the asset type in the Earth Engine Assets panel first.

## Local run

From this directory:

```bash
python -m venv .venv
# Activate the virtual environment
pip install -r requirements.txt
earthengine authenticate
```

Set `GEE_PROJECT_ID` to your actual Google Cloud project ID in your shell or local `.env` loader. Do not commit real `.env` files or credentials.

Run:

```bash
uvicorn app.main:app --reload
```

Try `http://127.0.0.1:8000/api/health`, `http://127.0.0.1:8000/docs`, and `http://127.0.0.1:8000/api/v1/rainfall/annual?year=2020`.

## Frontend connection

In `../js/app.js`, set `AQUAGEOAI_API_BASE` to the backend origin. The default points to `http://127.0.0.1:8000` for local development. For production, use HTTPS and add your frontend origin to the backend's `FRONTEND_ORIGINS` setting.

## Important limitations

- The annual statistic is the mean of annual pixel totals within the AOI, not a catchment water balance.
- CHIRPS rainfall is an estimate; document its limitations and spatial scale.
- The raster map endpoint returns a browser-usable Earth Engine tile URL which may contain a temporary token. For sensitive data or stricter access controls, proxy tile requests through an authenticated backend.
- The current map styling is illustrative; adjust the palette/range for local rainfall distributions and include a visible legend before operational use.
- `P - ET` is only a screening indicator, not direct groundwater recharge.
- Water-quality analysis and a validated recharge model are not implemented by this API scaffold.
