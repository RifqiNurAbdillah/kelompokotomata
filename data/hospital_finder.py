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


def find_nearby_hospitals(lat, lon, limit=3):
    """Query Overpass API untuk mencari rumah sakit terdekat tanpa batas radius kaku.
    Akan memperbesar radius pencarian secara otomatis jika belum menemukan jumlah yang cukup.
    """
    # Cari dengan radius yang semakin membesar: 5km, 25km, 100km, 500km
    for radius_m in [5000, 25000, 100000, 500000]:
        query = f"""
        [out:json][timeout:15];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          relation["amenity"="hospital"](around:{radius_m},{lat},{lon});
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
            name = tags.get("name", "Rumah Sakit (tanpa nama)")
            
            # Ekstrak alamat lengkap
            address = tags.get("addr:full") or tags.get("addr:street")
            if not address:
                address = "Alamat detail tidak tersedia di sistem satelit."
            else:
                city = tags.get("addr:city")
                if city and city not in address:
                    address += f", {city}"
                    
            dist = _haversine_km(lat, lon, h_lat, h_lon)
            
            hospitals.append({
                "name": name,
                "lat": h_lat,
                "lon": h_lon,
                "distance_km": round(dist, 2),
                "address": address
            })
            
        # Sort berdasarkan jarak
        hospitals.sort(key=lambda h: h["distance_km"])
        
        # Jika sudah menemukan setidaknya 'limit' RS, atau ini iterasi terakhir, kembalikan.
        if len(hospitals) >= limit or radius_m == 500000:
            return hospitals[:limit]
            
    return []
