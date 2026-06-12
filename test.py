import requests
query = """
[out:json][timeout:10];
(
  node["amenity"="hospital"](around:5000,-6.2,106.816666);
  way["amenity"="hospital"](around:5000,-6.2,106.816666);
  relation["amenity"="hospital"](around:5000,-6.2,106.816666);
);
out center body;
"""
try:
    headers = {'User-Agent': 'HealthBuddy-App/1.0'}
    resp = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, headers=headers)
    print("Status:", resp.status_code)
    print("Response:", resp.text[:200])
except Exception as e:
    print("Error:", e)
