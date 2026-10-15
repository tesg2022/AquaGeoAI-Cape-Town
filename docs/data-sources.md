# Data sources and analytical notes

This document is a starting point for documenting data used by AquaGeoAI Cape Town. The current landing page does not fetch or process any datasets. Before adding a layer, record its authoritative source, licence, spatial/temporal resolution, coverage, processing method, and known limitations.

## Candidate data categories

| Theme | Candidate source/product | Intended use | Important caveat |
|---|---|---|---|
| Rainfall | CHIRPS precipitation | Rainfall totals and anomalies | Check version, period, units, and suitability for the study area. |
| Evapotranspiration | MODIS or another documented ET product | ET indicator and water-balance screening | ET products differ in units, temporal aggregation, and uncertainty. |
| Vegetation | MODIS NDVI or another validated vegetation product | Vegetation condition and change | NDVI is not a direct measure of water quality or groundwater recharge. |
| Land cover | ESA WorldCover or a documented land-cover product | Land-cover context and stratification | Confirm year, class definitions, resolution, and change-comparison limitations. |
| Groundwater/hydrology | Appropriate local groundwater observations, hydrogeological maps, and model outputs | Recharge assessment and validation | Recharge cannot be reliably inferred from a single satellite indicator alone. |
| Water quality | Accredited in-situ observations or validated sensor-specific retrievals | Water-quality assessment | State the measured parameter, method, validation data, and uncertainty. |
| Boundaries | Official City of Cape Town or other authoritative administrative boundary | Area of interest (AOI) | Record source, date, coordinate reference system, and licence. |

## Minimum metadata to record for every layer

- Dataset/product name and provider
- Source URL or catalogue identifier
- Access date and licence/terms of use
- Spatial coverage and coordinate reference system
- Spatial resolution and temporal frequency/coverage
- Units, scale factors, quality flags, and missing-data handling
- Pre-processing steps and aggregation method
- Validation approach, uncertainty, and known limitations

## Google Earth Engine

If Earth Engine is used in a later version, keep authentication and credentials outside the repository. Never upload service-account JSON keys, private tokens, or other credentials to GitHub. A public static GitHub Pages website cannot securely hold private server credentials; protected Earth Engine workflows should run in an appropriately secured environment.

## Status

The data categories above are suggested candidates, not confirmation that the current landing page is connected to them. Document actual products and methods as they are selected and implemented.
