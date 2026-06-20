import requests
from pathlib import Path

API_URL = "https://www.geoboundaries.org/api/current/gbOpen/UKR/ADM1/"
OUTPUT = "data/reference/ukraine_oblasts.geojson"

print("Requesting GeoJSON metadata...")

response = requests.get(API_URL, timeout=30)
response.raise_for_status()

metadata = response.json()
geojson_url = metadata["gjDownloadURL"]

print("Downloading GeoJSON...")
geojson = requests.get(geojson_url, timeout=60)
geojson.raise_for_status()

Path("data/reference").mkdir(parents=True, exist_ok=True)
Path(OUTPUT).write_bytes(geojson.content)

print("Saved:")
print(OUTPUT)