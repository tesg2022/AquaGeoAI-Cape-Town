document.getElementById("year").textContent = new Date().getFullYear();

// Set this to the deployed FastAPI origin, e.g. https://api.example.org.
// For local development use http://127.0.0.1:8000.
const AQUAGEOAI_API_BASE = "http://127.0.0.1:8000";

(function initializeAquaGeoAIMap() {
  const mapElement = document.getElementById("aquageoai-map");
  if (!mapElement) return;

  const capeTownCenter = [18.4241, -33.9249];
  const statusElement = document.getElementById("map-status");
  const yearSelect = document.getElementById("rainfall-year");
  const loadButton = document.getElementById("load-rainfall");
  let map;

  function setStatus(message, state) {
    if (!statusElement) return;
    statusElement.textContent = message;
    if (state) statusElement.dataset.state = state;
    else delete statusElement.dataset.state;
  }

  function showMapError(message) {
    mapElement.innerHTML = '<div class="map-error"></div>';
    mapElement.querySelector(".map-error").textContent = message;
  }

  if (typeof maplibregl === "undefined") {
    showMapError("Map library did not load. Check your internet connection and refresh.");
    return;
  }

  try {
    map = new maplibregl.Map({
      container: "aquageoai-map",
      style: "https://tiles.openfreemap.org/styles/liberty",
      center: capeTownCenter,
      zoom: 9.5,
      attributionControl: true
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "metric" }), "bottom-left");
    map.addControl(new maplibregl.FullscreenControl(), "top-right");

    map.on("load", function () {
      setStatus("Basemap ready. Select a year and load annual CHIRPS rainfall.", "success");
    });

    map.on("error", function (event) {
      console.warn("AquaGeoAI map error:", event && event.error ? event.error : event);
    });

    const resetButton = document.getElementById("reset-map");
    if (resetButton) {
      resetButton.addEventListener("click", function () {
        map.flyTo({ center: capeTownCenter, zoom: 9.5, pitch: 0, bearing: 0, essential: true });
      });
    }

    async function loadRainfallLayer() {
      if (!map || !map.isStyleLoaded()) {
        setStatus("Map is still loading. Please try again shortly.", "error");
        return;
      }
      const year = yearSelect ? yearSelect.value : "2020";
      loadButton.disabled = true;
      loadButton.textContent = "Loading…";
      setStatus(`Requesting CHIRPS rainfall for ${year}…`);

      try {
        const url = new URL("/api/v1/rainfall/annual/map", AQUAGEOAI_API_BASE);
        url.searchParams.set("year", year);
        const response = await fetch(url.toString());
        if (!response.ok) {
          let detail = `API returned HTTP ${response.status}`;
          try {
            const body = await response.json();
            if (body.detail) detail = body.detail;
          } catch (_) {}
          throw new Error(detail);
        }
        const result = await response.json();
        if (!result.tile_url) throw new Error("API response did not include a raster tile URL.");

        if (map.getLayer("annual-rainfall-layer")) {
          map.removeLayer("annual-rainfall-layer");
        }
        if (map.getSource("annual-rainfall")) {
          map.removeSource("annual-rainfall");
        }

        map.addSource("annual-rainfall", {
          type: "raster",
          tiles: [result.tile_url],
          tileSize: 256,
          attribution: "Rainfall: CHIRPS · Earth Engine"
        });
        map.addLayer({
          id: "annual-rainfall-layer",
          type: "raster",
          source: "annual-rainfall",
          paint: { "raster-opacity": 0.68 }
        });

        setStatus(
          `Annual CHIRPS rainfall layer loaded for ${result.year}. Units: ${result.units}. This is precipitation, not groundwater recharge.`,
          "success"
        );
      } catch (error) {
        console.error("Rainfall layer request failed:", error);
        setStatus(
          `Could not load rainfall. Ensure the FastAPI backend is running and Earth Engine is configured. ${error.message}`,
          "error"
        );
      } finally {
        loadButton.disabled = false;
        loadButton.textContent = "Load rainfall layer";
      }
    }

    if (loadButton) loadButton.addEventListener("click", loadRainfallLayer);
  } catch (error) {
    console.error("Unable to initialize AquaGeoAI map:", error);
    showMapError("The interactive map could not be initialized. Check the browser console and network access.");
  }
})();
