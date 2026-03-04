import pandas as pd
import requests
import folium
from folium import IFrame
from urllib.parse import quote

# =========================
# EDIT THESE 3 VALUES
# =========================
ACCESS_TOKEN = "pk.eyJ1IjoiY29sYnlyZXlub2xkcyIsImEiOiJjbWx0d25oamkwNG9rM2dxM2RlaWEyaTBxIn0.Nd3YnjS_PE585HLQ4j9qeQ"

# Your style URL looks like: mapbox://styles/username/styleid
MAPBOX_USERNAME = "colbyreynolds"
MAPBOX_STYLE_ID = "cmmb2inik002x01s6fq3ph5aq"

CSV_PATH = "hometown_locations.csv"
OUTPUT_HTML = "lab6_hometown_map.html"

# Colorado centered-ish (map auto-fits to your markers anyway)
START_LOCATION = [39.0, -105.5]
START_ZOOM = 7

# Mapbox tiles (custom basemap)
TILES_URL = (
    f"https://api.mapbox.com/styles/v1/{MAPBOX_USERNAME}/{MAPBOX_STYLE_ID}"
    f"/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={ACCESS_TOKEN}"
)

# Marker colors by Type
TYPE_COLORS = {
    "Restaurant": "red",
    "Recreation": "green",
    "Cultural": "purple",
    "Historical": "orange",
}

def geocode_address(address: str):
    """Geocode an address using Mapbox Geocoding API v6 forward search.
    Returns (lat, lon) or (None, None)."""
    url = f"https://api.mapbox.com/search/geocode/v6/forward?q={quote(address)}&access_token={ACCESS_TOKEN}"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        print(f"Geocode failed ({r.status_code}): {address}")
        return None, None

    data = r.json()
    features = data.get("features", [])
    if not features:
        print(f"No results: {address}")
        return None, None

    coords = features[0].get("geometry", {}).get("coordinates", None)  # [lon, lat]
    if not coords or len(coords) < 2:
        print(f"Bad coords: {address}")
        return None, None

    lon, lat = coords[0], coords[1]
    return lat, lon

# -------------------------
# 1) Read CSV
# -------------------------
df = pd.read_csv(CSV_PATH)

# -------------------------
# 2) Geocode
# -------------------------
lats, lons = [], []
print("Geocoding addresses...")
for addr in df["Address"].astype(str):
    lat, lon = geocode_address(addr)
    lats.append(lat)
    lons.append(lon)

df["Latitude"] = lats
df["Longitude"] = lons

# Drop any rows that failed geocoding
df = df.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)

# -------------------------
# 3) Build Folium map with custom Mapbox basemap
# -------------------------
m = folium.Map(location=START_LOCATION, zoom_start=START_ZOOM, tiles=None, control_scale=True)

folium.TileLayer(
    tiles=TILES_URL,
    attr="Mapbox",
    name="Custom Basemap",
    overlay=False,
    control=True
).add_to(m)

# -------------------------
# 4) Add markers + popups
# -------------------------
bounds = []

for _, row in df.iterrows():
    name = str(row["Name"])
    loc_type = str(row["Type"])
    desc = str(row["Description"])
    img = str(row["Image_URL"])

    color = TYPE_COLORS.get(loc_type, "gray")

    popup_html = f"""
    <div style="width: 260px;">
        <h4 style="margin: 0 0 6px 0;">{name}</h4>
        <p style="margin: 0 0 6px 0; font-size: 12px;"><b>Type:</b> {loc_type}</p>
        <img src="{img}" style="width: 100%; border-radius: 10px; margin: 6px 0 8px 0;" />
        <p style="margin: 0; font-size: 12px; line-height: 1.3;">{desc}</p>
    </div>
    """

    iframe = IFrame(html=popup_html, width=280, height=320)
    popup = folium.Popup(iframe, max_width=300)

    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    bounds.append([lat, lon])

    folium.Marker(
        location=[lat, lon],
        popup=popup,
        tooltip=name,
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

if bounds:
    m.fit_bounds(bounds, padding=(30, 30))

folium.LayerControl().add_to(m)

# -------------------------
# 5) Save HTML
# -------------------------
m.save(OUTPUT_HTML)
print(f"Saved map to: {OUTPUT_HTML}")