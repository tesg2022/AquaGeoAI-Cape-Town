# AquaGeoAI Cape Town

**GeoAI-Powered Water & Climate Intelligence**

AquaGeoAI Cape Town is a developing WebGIS concept for bringing Earth observation, climate indicators, geospatial analytics, and hydrological modelling together to support water security and climate resilience in Cape Town, South Africa.

## Current website

The current version is a responsive static landing page. Its map-style graphic is illustrative; it is **not** a live GIS map and the page does not yet connect to live datasets or a backend.

## Project structure

```text
AquaGeoAI-Cape-Town/
├── index.html
├── README.md
├── assets/
│   ├── images/
│   │   └── .gitkeep
│   └── logo.svg
├── css/
│   └── styles.css
├── js/
│   └── app.js
├── docs/
│   └── data-sources.md
└── .gitignore
```

## Run locally

No build process is required for the landing page.

1. Download or clone this repository.
2. Open `index.html` in a browser.

For a local development server, if Python is installed, run this from the project directory:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Publish with GitHub Pages

1. Create a GitHub repository named `AquaGeoAI-Cape-Town`.
2. Upload the contents of this project folder to the repository root.
3. In the repository, open **Settings → Pages**.
4. Under the build/deployment source, choose **Deploy from a branch**.
5. Select branch `main` and folder `/(root)`, then save.

The site will usually be available at `https://YOUR-USERNAME.github.io/AquaGeoAI-Cape-Town/` after deployment completes.

## Planned development

- Add a real interactive map using a suitable web mapping library.
- Connect approved geospatial datasets and document their spatial and temporal resolution.
- Develop drought-risk and groundwater-recharge screening workflows.
- Add a backend API for data processing and model services where needed.
- Validate analytical outputs against appropriate local observations and reference datasets.

## Scientific and data-use notes

Rainfall minus evapotranspiration can be used as a preliminary water-availability screening indicator, but it is not a direct measurement of groundwater recharge. NDVI indicates vegetation greenness/condition and is not, by itself, a water-quality measurement. Groundwater-recharge and water-quality assessments require suitable methods, data, and local validation.

Do not commit API keys, Earth Engine service-account keys, passwords, or other secrets to this public repository.
