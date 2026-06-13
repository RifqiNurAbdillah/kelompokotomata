"""NLP Engine: tokenize, stem, score, dan deteksi intent."""

import re
from rapidfuzz import fuzz
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from data import DISEASES, RED_FLAGS, FIRST_AID, DEFINITIONS, FAQ
from data.expanded_knowledge import (
    EXPANDED_SYMPTOM_RULES,
    FACILITY_ACTION_TERMS_EXPANDED,
    FACILITY_LOCATION_TERMS_EXPANDED,
    FACILITY_REQUEST_PHRASES,
    FACILITY_TARGET_TERMS_EXPANDED,
    TYPO_ALIASES,
)


STOPWORDS = {
    "yang", "di", "ke", "dari", "untuk", "dengan", "dan", "atau", "ini", "itu",
    "saya", "aku", "kamu", "dia", "kita", "kami", "mereka", "adalah", "ialah",
    "merupakan", "ada", "akan", "sudah", "belum", "tidak", "bukan", "juga",
    "saja", "lagi", "pun", "pula", "deh", "sih", "kok", "ya", "ga", "gak",
    "nya", "nih", "tuh", "loh", "lho", "dong", "ok", "oke", "halo", "hai",
    "selamat", "pagi", "siang", "sore", "malam", "permisi", "maaf", "tolong",
    "mohon", "bantu", "tanya", "ingin", "mau", "pengen", "ingin", "boleh",
    "apa", "apakah", "siapa", "kapan", "dimana", "kemana", "bagaimana",
    "kenapa", "mengapa", "berapa", "tahu", "info", "informasi", "tentang",
}

INTENT_KEYWORDS = {
    "RESET": [r"\b(reset|ulang|mulai lagi|mulai kembali|bersihkan|clear)\b"],
    "GREETING": [r"\b(halo|hai|hi|selamat (pagi|siang|sore|malam))\b"],
    "THANKS": [r"\b(terima kasih|makasih|thanks|thank you|tq|trims)\b"],
    "GOODBYE": [r"\b(bye|sampai jumpa|dadah|sudahan|cukup|selesai|udahan)\b"],
    "HELP": [r"\b(bantuan|help|panduan|cara pakai|menu)\b"],
    "IDENTITY": [r"\b(siapa kamu|kamu siapa|apa itu healthbuddy|apa itu health buddy|tentang healthbuddy|tentang health buddy|healthbuddy itu apa|health buddy itu apa)\b"],
    "CAPABILITY": [r"\b(bisa apa|kamu bisa apa|fitur apa|bantu apa|apa yang bisa kamu bantu|fungsi kamu|cara kerja kamu)\b"],
    "EMERGENCY_INFO": [r"\b(nomor (darurat|emergency)|igd|ambulans|119|nomor penting)\b"],
    "ASK_HOSPITAL": [r"\b(rumah sakit|rs |rs\b|cari rs|rs terdekat|rumah sakit terdekat|puskesmas|klinik terdekat|faskes|fasilitas kesehatan|lokasi rs|lokasi rumah sakit)\b"],
    "ASK_DEFINITION": [r"\b(apa itu|apakah itu|definisi|arti|pengertian|maksud (dari|dengan))\b"],
    "ASK_FIRST_AID": [r"\b(p3k|pertolongan pertama|cara mengatasi|cara menangani|kalau .* bagaimana)\b"],
    "ASK_FAQ": [r"\b(berapa lama|berapa banyak|tips|cara hidup sehat|gaya hidup|saran sehat)\b"],
    "MORE_DETAIL": [r"\b(lebih lanjut|detail|jelaskan|lengkap|info lebih)\b"],
    "AFFIRM": [r"\b(iya|ya|betul|benar|setuju|oke saja|cocok)\b"],
    "DENY": [r"\b(tidak|enggak|nggak|bukan|tidak juga|engga)\b"],
}

FACILITY_ACTION_TERMS = [
    "cari", "carikan", "temukan", "rekomendasikan", "rekomendasi", "sarankan", "saranin",
    "tunjukkan", "tampilkan", "lihatkan", "butuh", "perlu", "minta", "tolong", "bantu cari",
]

FACILITY_TARGET_TERMS = [
    "rumah sakit", "rs", "hospital", "klinik", "puskesmas", "dokter", "igd", "faskes",
    "fasilitas kesehatan", "layanan kesehatan", "tempat berobat", "tempat periksa", "unit gawat darurat",
    "dokter gigi", "dentis", "doket gigi", "dokter mata", "klinik mata", "dokter tht", "klinik tht",
    "spesialis mata", "spesialis gigi", "spesialis tht", "optik", "igd terdekat",
]

FACILITY_LOCATION_TERMS = [
    "terdekat", "dekat", "sekitar", "di sekitar", "dari lokasiku", "dari lokasi saya",
    "dekat saya", "near me", "yang paling dekat", "sekitar sini", "area saya", "lokasi sekarang",
]

FACILITY_CONTEXT_TERMS = [
    "keluhan", "kendala", "kondisi", "gejala", "sakit", "darurat", "butuh bantuan",
    "periksa", "kontrol", "berobat", "penanganan", "rujukan", "sekarang", "secepatnya",
]


def _is_healthcare_facility_request(text):
    text = text.lower()
    text = _apply_typo_aliases(text)
    if text in FACILITY_REQUEST_PHRASES:
        return True
    has_target = any(term in text for term in FACILITY_TARGET_TERMS + FACILITY_TARGET_TERMS_EXPANDED)
    has_location = any(term in text for term in FACILITY_LOCATION_TERMS + FACILITY_LOCATION_TERMS_EXPANDED)
    has_action = any(term in text for term in FACILITY_ACTION_TERMS + FACILITY_ACTION_TERMS_EXPANDED)
    has_context = any(term in text for term in FACILITY_CONTEXT_TERMS)
    if has_target and (has_location or has_action or has_context):
        return True
    if has_location and has_action and has_context:
        return True
    return False


def _apply_typo_aliases(text):
    normalized = text.lower()
    for wrong, correct in TYPO_ALIASES.items():
        normalized = re.sub(rf"\b{re.escape(wrong)}\b", correct, normalized)
    return normalized


BODY_PART_RULES = [
    (r"\b(mata|mataku|mata saya|kelopak|penglihatan|konjungtiva)\b", [("konjungtivitis", 4.5)]),
    (r"\b(gigi|gigiku|gigi saya|geraham|gusi|ngilu|dentis|dokter gigi)\b", [("sakit gigi", 5.0)]),
    (r"\b(hidung|hidungku|hidung saya|ingus|meler|pilek|bersin|sinus)\b", [("flu", 4.2), ("alergi", 2.0)]),
    (r"\b(telinga|kuping|pendengaran|berdengung)\b", [("vertigo", 2.5)]),
    (r"\b(tenggorokan|menelan|amandel|serak)\b", [("radang tenggorokan", 4.0), ("flu", 1.5)]),
    (r"\b(perut|lambung|ulu hati|kembung|begah|mual|perih)\b", [("maag", 4.0)]),
    (r"\b(mencret|bab cair|diare)\b", [("diare", 5.0)]),
    (r"\b(kulit|gatal|ruam|bentol|biduran|alergi)\b", [("alergi", 3.0), ("biduran", 3.0)]),
    (r"\b(kepala|pusing|migrain|berdenyut)\b", [("sakit kepala", 3.5), ("migrain", 2.0)]),
    (r"\b(sendi|lutut|pergelangan|jempol kaki|asam urat)\b", [("asam urat", 3.5)]),
    (r"\b(otot|kram|pegal|kaku)\b", [("kram otot", 3.5)]),
    (r"\b(dada sesak|mengi|napas berbunyi|asma)\b", [("asma", 4.5)]),
    (r"\b(sariawan|luka mulut|mulut pedih)\b", [("sariawan", 4.5)]),
]


class NLPEngine:
    def __init__(self):
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()

        self._build_symptom_index()
        self._build_disease_index()
        self._build_red_flag_index()
        self._build_first_aid_index()
        self._build_definition_index()
        self._build_faq_index()

    # ---------- Index builders ----------

    def _build_symptom_index(self):
        # Map: stemmed keyword -> list of (disease_key, weight)
        self.symptom_to_disease = {}
        for key, info in DISEASES.items():
            for sym in info.get("gejala_utama", []):
                self._index_term(self.symptom_to_disease, sym, (key, 2.0))
            for sym in info.get("gejala_pendukung", []):
                self._index_term(self.symptom_to_disease, sym, (key, 1.0))
            self._index_term(self.symptom_to_disease, info["nama"], (key, 3.0))
            self._index_term(self.symptom_to_disease, key, (key, 3.0))

    def _build_disease_index(self):
        self.disease_aliases = {}
        for key, info in DISEASES.items():
            self.disease_aliases[self._stem_phrase(key)] = key
            self.disease_aliases[self._stem_phrase(info["nama"])] = key

    def _build_red_flag_index(self):
        self.red_flag_index = {}
        for key in RED_FLAGS.keys():
            self.red_flag_index[self._stem_phrase(key)] = key

    def _build_first_aid_index(self):
        self.first_aid_index = {}
        for key, info in FIRST_AID.items():
            self.first_aid_index[self._stem_phrase(key)] = key
            self.first_aid_index[self._stem_phrase(info["judul"])] = key
            for kw in info.get("kata_kunci", []):
                self.first_aid_index[self._stem_phrase(kw)] = key

    def _build_definition_index(self):
        self.definition_index = {}
        for term in DEFINITIONS.keys():
            self.definition_index[self._stem_phrase(term)] = term

    def _build_faq_index(self):
        self.faq_index = {}
        for key, info in FAQ.items():
            self.faq_index[self._stem_phrase(key)] = key
            self.faq_index[self._stem_phrase(info["judul"])] = key

    def _index_term(self, index_dict, term, payload):
        stemmed = self._stem_phrase(term)
        index_dict.setdefault(stemmed, []).append(payload)

    # ---------- Text processing ----------

    def _stem_phrase(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return self.stemmer.stem(text)

    def normalize(self, text):
        return self._stem_phrase(text)

    def tokenize(self, text):
        text = self.normalize(text)
        tokens = [t for t in text.split() if t and t not in STOPWORDS and len(t) > 1]
        return tokens

    # ---------- Intent detection ----------

    def detect_intent(self, raw_text):
        text = raw_text.lower()
        raw_lower = _apply_typo_aliases(text)
        
        # 1. PRIORITAS UTAMA: Cek System/Urgent Perintah (RESET & EMERGENCY_INFO)
        # Jangan sampai user mau reset bot atau butuh nomor darurat malah terhadang deteksi gejala
        for urgent_intent in ["RESET", "EMERGENCY_INFO"]:
            if urgent_intent in INTENT_KEYWORDS:
                for pat in INTENT_KEYWORDS[urgent_intent]:
                    if re.search(pat, text):
                        return urgent_intent

        # 2. PRIORITAS KEDUA: Fasilitas Kesehatan / Pencarian RS
        if _is_healthcare_facility_request(text):
            return "ASK_HOSPITAL"
            
        # 3. INTERUPSI GEJALA: Cek apakah mengandung gejala klinis dari database?
        # Jika user bilang "cara mengatasi nyeri haid", fungsi ini akan memotong di sini
        for rule in EXPANDED_SYMPTOM_RULES:
            if rule["phrase"] in raw_lower:
                # Mengembalikan None memaksa FSM masuk ke alur diagnosis/score_diseases()
                return None 
                
        # 4. PRIORITAS TERAKHIR: Proses Keyword Intent Umum (GREETING, FIRST_AID, DEFINITION, dll)
        # Bagian ini hanya dieksekusi jika input bersih dari gejala penyakit spesifik
        for intent, patterns in INTENT_KEYWORDS.items():
            # Lewati yang sudah dicek di langkah awal
            if intent in ["RESET", "EMERGENCY_INFO"]:
                continue
            for pat in patterns:
                if re.search(pat, text):
                    return intent
                    
        return None

    # ---------- Red flag detection (priority) ----------

    def detect_red_flag(self, raw_text):
        normalized = self.normalize(raw_text)
        # exact / substring on stemmed form
        for stemmed_key, original in self.red_flag_index.items():
            if stemmed_key and stemmed_key in normalized:
                return original
        # fuzzy fallback
        for stemmed_key, original in self.red_flag_index.items():
            if not stemmed_key:
                continue
            score = fuzz.token_set_ratio(stemmed_key, normalized)
            if score >= 90 and len(stemmed_key) >= 5:
                return original
        return None

    # ---------- Symptom scoring ----------

    def score_diseases(self, raw_text, accumulated=None):
        """Skor kemungkinan penyakit berdasarkan gejala yang disebutkan.

        accumulated: dict {disease_key: score} dari turn sebelumnya.
        Return: list sorted of (disease_key, score, matched_terms).
        """
        normalized = self.normalize(raw_text)
        scores = dict(accumulated) if accumulated else {}
        matched_terms = {}

        raw_lower = raw_text.lower()
        raw_lower = _apply_typo_aliases(raw_lower)
        for rule in EXPANDED_SYMPTOM_RULES:
            phrase = rule["phrase"]
            if phrase in raw_lower:
                disease_key = rule["disease"]
                scores[disease_key] = scores.get(disease_key, 0) + float(rule["weight"])
                matched_terms.setdefault(disease_key, set()).add(phrase)

        for pattern, disease_weights in BODY_PART_RULES:
            if re.search(pattern, raw_lower):
                for disease_key, weight in disease_weights:
                    scores[disease_key] = scores.get(disease_key, 0) + weight
                    matched_terms.setdefault(disease_key, set()).add(pattern)

        for stemmed_term, payloads in self.symptom_to_disease.items():
            if not stemmed_term:
                continue
            hit = False
            if stemmed_term in normalized:
                hit = True
            else:
                # fuzzy partial match for typo tolerance
                if len(stemmed_term) >= 5 and " " not in stemmed_term:
                    ratio = fuzz.partial_ratio(stemmed_term, normalized)
                    if ratio >= 88:
                        hit = True
            if not hit:
                continue
            for disease_key, weight in payloads:
                scores[disease_key] = scores.get(disease_key, 0) + weight
                matched_terms.setdefault(disease_key, set()).add(stemmed_term)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for dkey, score in ranked:
            result.append({
                "disease": dkey,
                "score": score,
                "matched": sorted(matched_terms.get(dkey, set())),
            })
        return result, scores

    # ---------- Direct lookups ----------

    def find_disease(self, raw_text):
        normalized = self.normalize(raw_text)
        for stemmed_key, original in sorted(self.disease_aliases.items(), key=lambda item: len(item[0]), reverse=True):
            if stemmed_key and stemmed_key in normalized:
                return original
        for stemmed_key, original in sorted(self.disease_aliases.items(), key=lambda item: len(item[0]), reverse=True):
            if not stemmed_key:
                continue
            if fuzz.partial_ratio(stemmed_key, normalized) >= 90:
                return original
        return None

    def find_definition(self, raw_text):
            normalized = self.normalize(raw_text)
            raw_lower = raw_text.lower()
            
            # Tambahkan guard/pelindung: Jangan berikan definisi jika teks mengandung kata keluhan
            # seperti "tinggi", "rendah", "naik", "turun", atau "sakit"
            indikator_keluhan = ["tinggi", "rendah", "naik", "turun", "kumat", "sakit"]
            if any(kata in raw_lower for kata in indikator_keluhan):
                return None # Paksa return None agar dialihkan ke scoring penyakit (TRIAGE)

            # Cari yang paling panjang dulu biar "tekanan darah" menang dari "darah"
            candidates = sorted(self.definition_index.keys(), key=len, reverse=True)
            for stemmed_key in candidates:
                if stemmed_key and stemmed_key in normalized:
                    return self.definition_index[stemmed_key]
            
            # Fuzzy fallback
            best = (None, 0)
            for stemmed_key, original in self.definition_index.items():
                if len(stemmed_key) < 4:
                    continue
                score = fuzz.partial_ratio(stemmed_key, normalized)
                if score > best[1]:
                    best = (original, score)
            if best[1] >= 88:
                return best[0]
            return None

    def find_first_aid(self, raw_text):
        normalized = self.normalize(raw_text)
        raw_lower = raw_text.lower()
        
        #  GUARD 1: Jika ini adalah keluhan tensi/tekanan darah, 
        # JANGAN ijinkan masuk ke modul P3K Luka/Cedera fisik.
        if "tekanan darah" in raw_lower or "tensi" in raw_lower:
            return None

        tokenized = self.tokenize(raw_text)
        candidates = sorted(self.first_aid_index.keys(), key=lambda x: len(x) if x else 0, reverse=True)
        
        # PERBAIKAN: Gunakan regex word boundary (\b) agar mencocokkan kata utuh,
        # bukan potongan karakter di dalam kata lain (mencegah partial substring match)
        for stemmed_key in candidates:
            if stemmed_key:
                # Membuat pola regex kata utuh dari kata kunci p3k
                pattern = rf"\b{re.escape(stemmed_key)}\b"
                if re.search(pattern, normalized):
                    return self.first_aid_index[stemmed_key]
                    
        # Fuzzy fallback (hanya jalankan jika kata cukup panjang untuk menghindari salah deteksi)
        for stemmed_key in candidates:
            if not stemmed_key or len(stemmed_key) < 5:
                continue
            if fuzz.token_set_ratio(stemmed_key, normalized) >= 90: # Naikkan batasan ke 90
                return self.first_aid_index[stemmed_key]
                
        return None

    def find_faq(self, raw_text):
        normalized = self.normalize(raw_text)
        candidates = sorted(self.faq_index.keys(), key=len, reverse=True)
        for stemmed_key in candidates:
            if stemmed_key and stemmed_key in normalized:
                return self.faq_index[stemmed_key]
        best = (None, 0)
        for stemmed_key, original in self.faq_index.items():
            score = fuzz.partial_ratio(stemmed_key, normalized)
            if score > best[1]:
                best = (original, score)
        if best[1] >= 86:
            return best[0]
        return None
