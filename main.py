"""AquaGeoAI Cape Town API: annual CHIRPS rainfall summary and map layer.

Earth Engine authentication must be configured in the hosting environment.
Never commit credentials to GitHub.
"""
import logging
import os
from functools import lru_cache
from typing import Any

import ee
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger("aquageoai")

GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "").strip()
AOI_ASSET = "projects/ee-ttgintamo/assets/City_of_Cape_Town"
CHIRPS_COLLECTION = "UCSB-CHG/CHIRPS/DAILY"
FIRST_YEAR = 1981
LAST_COMPLETE_YEAR = 2025  # Use completed calendar years for annual totals.

app = FastAPI(
    title="AquaGeoAI Cape Town API",
    description="Annual CHIRPS rainfall summary and MapLibre raster-layer endpoint.",
    version="0.2.0",
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def initialize_earth_engine() -> None:
    """Initialize EE using credentials configured outside the repository."""
    if not GEE_PROJECT_ID:
        raise RuntimeError("GEE_PROJECT_ID is not configured on the server.")
    # The deployment identity must already be authenticated and have access
    # to the Cloud project, Earth Engine, and the AOI asset.
    ee.Initialize(project=GEE_PROJECT_ID)


def get_aoi() -> Any:
    """Load the configured study area as a FeatureCollection."""
    aoi = ee.FeatureCollection(AOI_ASSET)
    # Force a lightweight server-side evaluation so missing/inaccessible assets
    # fail before a response is reported as successful.
    count = aoi.size().getInfo()
    if not count:
        raise RuntimeError("The City of Cape Town FeatureCollection is empty.")
    return aoi


def annual_rainfall_image(year: int):
    """Return CHIRPS annual total image in mm/year."""
    start = ee.Date.fromYMD(year, 1, 1)
    end = ee.Date.fromYMD(year + 1, 1, 1)
    daily = (
        ee.ImageCollection(CHIRPS_COLLECTION)
        .filterDate(start, end)
        .select("precipitation")
    )
    count = daily.size().getInfo()
    if count == 0:
        raise RuntimeError(f"No CHIRPS daily images were found for {year}.")
    aoi = get_aoi()
    # CHIRPS daily precipitation band is mm/day; summing daily values gives
    # a calendar-year accumulated precipitation estimate in mm/year.
    return daily.sum().rename("rainfall_mm").clip(aoi.geometry()), aoi, count


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AquaGeoAI Cape Town API"}


@app.get("/api/v1/rainfall/annual")
def annual_rainfall(
    year: int = Query(2020, ge=FIRST_YEAR, le=LAST_COMPLETE_YEAR)
):
    """Return mean of per-pixel annual CHIRPS totals over the City AOI."""
    try:
        initialize_earth_engine()
        image, aoi, image_count = annual_rainfall_image(year)
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi.geometry(),
            # CHIRPS nominal grid spacing is about 0.05 degrees (~5.6 km).
            scale=5566,
            maxPixels=10_000_000,
            tileScale=2,
        ).getInfo()

        value = stats.get("rainfall_mm")
        if value is None:
            raise RuntimeError(
                "Rainfall statistic is null; check AOI overlap and valid pixels."
            )

        return {
            "year": year,
            "mean_annual_rainfall_mm": round(float(value), 3),
            "units": "mm/year",
            "dataset": CHIRPS_COLLECTION,
            "study_area_asset": AOI_ASSET,
            "aggregation": "Mean of annual pixel totals over the AOI",
            "daily_images_used": image_count,
            "status": "computed",
            "caveat": (
                "CHIRPS is a gridded precipitation estimate. This statistic "
                "is not a groundwater-recharge estimate."
            ),
        }
    except Exception as exc:
        logger.exception("Annual rainfall calculation failed for year=%s", year)
        raise HTTPException(
            status_code=503,
            detail=(
                "Rainfall calculation unavailable. Check Earth Engine "
                "authentication, project access, AOI asset type/permissions, "
                "and CHIRPS data availability."
            ),
        ) from exc


@app.get("/api/v1/rainfall/annual/map")
def annual_rainfall_map(
    year: int = Query(2020, ge=FIRST_YEAR, le=LAST_COMPLETE_YEAR)
):
    """Return a short-lived Earth Engine tile URL template for MapLibre.

    The tile URL is browser-visible and may contain a temporary token. Do not
    use this approach for private raster data requiring strict secrecy. For
    higher-security deployments, proxy tile requests through an authenticated
    backend instead.
    """
    try:
        initialize_earth_engine()
        image, _aoi, image_count = annual_rainfall_image(year)

        # CHIRPS annual totals are typically displayed with a sequential
        # precipitation palette; these are display settings, not classifications.
        vis = {
            "min": 0,
            "max": 1500,
            "palette": [
                "fff7ec", "fee8c8", "fdd49e", "fdbb84",
                "fc8d59", "ef6548", "d7301f", "990000"
            ],
        }
        map_info = image.getMapId(vis)
        tile_url = map_info["tile_fetcher"].url_format
        if not tile_url:
            raise RuntimeError("Earth Engine did not return a tile URL.")

        return JSONResponse(
            content={
                "year": year,
                "dataset": CHIRPS_COLLECTION,
                "units": "mm/year",
                "layer_type": "raster",
                "tile_url": tile_url,
                "daily_images_used": image_count,
                "status": "computed",
                "display": {
                    "min": vis["min"],
                    "max": vis["max"],
                    "palette": vis["palette"],
                },
                "caveat": (
                    "CHIRPS precipitation estimate; not groundwater recharge. "
                    "The map tile URL may contain a temporary access token."
                ),
            },
            headers={"Cache-Control": "no-store"},
        )
    except Exception as exc:
        logger.exception("Rainfall map generation failed for year=%s", year)
        raise HTTPException(
            status_code=503,
            detail=(
                "Rainfall map unavailable. Check Earth Engine authentication, "
                "AOI asset permissions, and CHIRPS availability."
            ),
        ) from exc


@app.get("/api/v1/layers")
def list_layers():
    return {
        "layers": [
            {
                "id": "annual-rainfall",
                "label": "Annual rainfall (CHIRPS)",
                "endpoint": "/api/v1/rainfall/annual/map",
                "units": "mm/year",
                "status": "implemented; requires Earth Engine configuration",
            },
            {
                "id": "ndvi",
                "label": "Vegetation / NDVI",
                "status": "planned",
            },
            {
                "id": "recharge-screening",
                "label": "Groundwater recharge screening",
                "status": "not implemented; requires method and local validation",
            },
        ]
    }
