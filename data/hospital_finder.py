"""Helper untuk mendeteksi kondisi yang ada di kedua FIRST_AID dan RED_FLAGS,
serta query rumah sakit terdekat via Overpass API (OpenStreetMap)."""

import requests
import math
from .first_aid import FIRST_AID
from .red_flags import RED_FLAGS


# ---------------------------------------------------------------------------
# Deteksi overlap antara FIRST_AID dan RED_FLAGS
# ---------------------------------------------------------------------------

def _build_overlap_map():
    """Membuat mapping kondisi yang ada di kedua dictionary.
    
    Menggunakan substring matching sehingga:
    - "pingsan" (FIRST_AID) cocok dengan "pingsan" (RED_FLAGS)
    - "luka bakar" (FIRST_AID) cocok dengan "luka bakar luas" (RED_FLAGS)
    - "muntah" (FIRST_AID) cocok dengan "muntah darah" (RED_FLAGS)
    - "demam anak" (FIRST_AID) cocok dengan "demam tinggi anak" (RED_FLAGS)
    """
    overlap = {}
    
    for fa_key in FIRST_AID:
        for rf_key in RED_FLAGS:
            # Cek substring match di kedua arah
            if fa_key in rf_key or rf_key in fa_key:
                # Gunakan key yang lebih pendek sebagai key utama
                main_key = fa_key if len(fa_key) <= len(rf_key) else rf_key
                overlap[main_key] = {
                    "first_aid_key": fa_key,
                    "red_flag_key": rf_key,
                    "first_aid_title": FIRST_AID[fa_key]["judul"],
                    "red_flag_category": RED_FLAGS[rf_key]["kategori"],
                }
    
    return overlap


OVERLAPPING_CONDITIONS = _build_overlap_map()


def check_needs_hospital_recommendation(text):
    """Cek apakah teks terkait dengan kondisi yang overlap antara FIRST_AID dan RED_FLAGS.
    
    Args:
        text: Bisa berupa key dari FIRST_AID, key dari RED_FLAGS, atau teks bebas.
    
    Returns:
        dict info overlap jika ditemukan, None jika tidak.
    """
    text_lower = text.lower().strip()
    
    # Cek exact match dulu
    if text_lower in OVERLAPPING_CONDITIONS:
        return OVERLAPPING_CONDITIONS[text_lower]
    
    # Cek substring match
    for key, info in OVERLAPPING_CONDITIONS.items():
        if key in text_lower or text_lower in key:
            return info
        # Cek juga terhadap key asli first_aid dan red_flag
        if info["first_aid_key"] in text_lower or text_lower in info["first_aid_key"]:
            return info
        if info["red_flag_key"] in text_lower or text_lower in info["red_flag_key"]:
            return info
    
    return None


# ---------------------------------------------------------------------------
# Hospital Recommendation Text
# ---------------------------------------------------------------------------

HOSPITAL_RECOMMENDATION_TEXT = (
    "\n\n---\n"
    "🏥 **Butuh rumah sakit terdekat dari lokasi Anda saat ini?**\n\n"
    "Kondisi ini memerlukan penanganan medis segera. "
    "Klik tombol **🗺️ Aktifkan Gmaps** di bawah pesan ini untuk mendeteksi lokasi Anda secara otomatis.\n\n"
    "Sistem akan langsung mengirimkan daftar 3 rumah sakit terdekat beserta alamat lengkapnya ke dalam obrolan ini."
)


# ---------------------------------------------------------------------------
# Overpass API query untuk rumah sakit terdekat
# ---------------------------------------------------------------------------

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"


def _haversine_km(lat1, lon1, lat2, lon2):
    """Hitung jarak antara dua titik koordinat dalam kilometer."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _facility_type(tags):
    amenity = tags.get("amenity", "")
    healthcare = tags.get("healthcare", "")
    name = tags.get("name", "").lower()
    if "puskesmas" in name:
        return "Puskesmas"
    if amenity == "hospital" or healthcare == "hospital":
        return "Rumah sakit"
    if amenity == "clinic" or healthcare == "clinic":
        return "Klinik"
    if amenity == "doctors" or healthcare == "doctor":
        return "Praktik dokter"
    return "Fasilitas kesehatan"


def _compose_address(tags, lat, lon):
    parts = []
    direct = tags.get("addr:full") or tags.get("address")
    if direct:
        return direct
    for key in ["addr:street", "addr:hamlet", "addr:village", "addr:subdistrict", "addr:district", "addr:city", "addr:county", "addr:state"]:
        value = tags.get(key)
        if value and value not in parts:
            parts.append(value)
    if parts:
        return ", ".join(parts)
    operator = tags.get("operator")
    if operator:
        return f"Area layanan {operator}. Koordinat: {lat:.6f}, {lon:.6f}"
    return f"Koordinat lokasi: {lat:.6f}, {lon:.6f}"


def _google_maps_url(lat, lon, name=""):
    query = f"{lat},{lon}"
    if name:
        query = f"{name} {query}"
    return "https://www.google.com/maps/search/?api=1&query=" + requests.utils.quote(query)


def _is_duplicate(candidate, existing_items):
    cand_name = candidate["name"].strip().lower()
    for item in existing_items:
        same_name = item["name"].strip().lower() == cand_name
        very_close = _haversine_km(candidate["lat"], candidate["lon"], item["lat"], item["lon"]) <= 0.25
        if same_name and very_close:
            return True
    return False


def find_nearby_hospitals(lat, lon, limit=6):
    """Query Overpass API untuk mencari fasilitas kesehatan terdekat.

    Cakupan: rumah sakit, klinik, puskesmas (berdasarkan nama), dan praktik dokter.
    Radius diperbesar bertahap agar tetap ada hasil pada area yang datanya jarang.
    """
    for radius_m in [4000, 10000, 25000, 75000, 150000]:
        query = f"""
        [out:json][timeout:15];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          relation["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="clinic"](around:{radius_m},{lat},{lon});
          way["amenity"="clinic"](around:{radius_m},{lat},{lon});
          relation["amenity"="clinic"](around:{radius_m},{lat},{lon});
          node["amenity"="doctors"](around:{radius_m},{lat},{lon});
          way["amenity"="doctors"](around:{radius_m},{lat},{lon});
          relation["amenity"="doctors"](around:{radius_m},{lat},{lon});
          node["healthcare"="hospital"](around:{radius_m},{lat},{lon});
          way["healthcare"="hospital"](around:{radius_m},{lat},{lon});
          relation["healthcare"="hospital"](around:{radius_m},{lat},{lon});
          node["healthcare"="clinic"](around:{radius_m},{lat},{lon});
          way["healthcare"="clinic"](around:{radius_m},{lat},{lon});
          relation["healthcare"="clinic"](around:{radius_m},{lat},{lon});
          node["healthcare"="doctor"](around:{radius_m},{lat},{lon});
          way["healthcare"="doctor"](around:{radius_m},{lat},{lon});
          relation["healthcare"="doctor"](around:{radius_m},{lat},{lon});
        );
        out center body;
        """
        
        try:
            headers = {'User-Agent': 'HealthBuddy-App/1.0'}
            resp = requests.post(OVERPASS_API_URL, data={"data": query}, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            continue  # Jika error timeout, coba radius lain (walau biasanya error juga, tapi kita skip)
            
        hospitals = []
        for element in data.get("elements", []):
            h_lat = element.get("lat") or element.get("center", {}).get("lat")
            h_lon = element.get("lon") or element.get("center", {}).get("lon")
            
            if h_lat is None or h_lon is None:
                continue
            
            tags = element.get("tags", {})
            name = tags.get("name", "Fasilitas kesehatan tanpa nama")
            facility_type = _facility_type(tags)
            
            address = _compose_address(tags, h_lat, h_lon)
            dist = _haversine_km(lat, lon, h_lat, h_lon)
            candidate = {
                "name": name,
                "type": facility_type,
                "lat": h_lat,
                "lon": h_lon,
                "distance_km": round(dist, 2),
                "address": address,
                "maps_url": _google_maps_url(h_lat, h_lon, name),
            }
            if _is_duplicate(candidate, hospitals):
                continue
            hospitals.append(candidate)
            
        # Sort berdasarkan jarak
        hospitals.sort(key=lambda h: h["distance_km"])
        
        # Jika sudah menemukan setidaknya 'limit' RS, atau ini iterasi terakhir, kembalikan.
        if len(hospitals) >= limit or radius_m == 150000:
            return hospitals[:limit]
            
    return []
