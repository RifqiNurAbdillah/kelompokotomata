"""NLP Engine: tokenize, stem, score, dan deteksi intent."""

import re
from rapidfuzz import fuzz
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from data import DISEASES, RED_FLAGS, FIRST_AID, DEFINITIONS, FAQ


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
    "EMERGENCY_INFO": [r"\b(nomor (darurat|emergency)|igd|ambulans|119|nomor penting)\b"],
    "ASK_HOSPITAL": [r"\b(rumah sakit|rs |rs\b|cari rs|rs terdekat|rumah sakit terdekat|puskesmas|klinik terdekat|lokasi rs|lokasi rumah sakit)\b"],
    "ASK_DEFINITION": [r"\b(apa itu|apakah itu|definisi|arti|pengertian|maksud (dari|dengan))\b"],
    "ASK_FIRST_AID": [r"\b(p3k|pertolongan pertama|cara mengatasi|cara menangani|kalau .* bagaimana)\b"],
    "ASK_FAQ": [r"\b(berapa lama|berapa banyak|tips|cara hidup sehat|gaya hidup|saran sehat)\b"],
    "MORE_DETAIL": [r"\b(lebih lanjut|detail|jelaskan|lengkap|info lebih)\b"],
    "AFFIRM": [r"\b(iya|ya|betul|benar|setuju|oke saja|cocok)\b"],
    "DENY": [r"\b(tidak|enggak|nggak|bukan|tidak juga|engga)\b"],
}


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
        for intent, patterns in INTENT_KEYWORDS.items():
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
            score = fuzz.partial_ratio(stemmed_key, normalized)
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

        for stemmed_term, payloads in self.symptom_to_disease.items():
            if not stemmed_term:
                continue
            hit = False
            if stemmed_term in normalized:
                hit = True
            else:
                # fuzzy partial match for typo tolerance
                if len(stemmed_term) >= 5:
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
        for stemmed_key, original in self.disease_aliases.items():
            if stemmed_key and stemmed_key in normalized:
                return original
        for stemmed_key, original in self.disease_aliases.items():
            if not stemmed_key:
                continue
            if fuzz.partial_ratio(stemmed_key, normalized) >= 90:
                return original
        return None

    def find_definition(self, raw_text):
        normalized = self.normalize(raw_text)
        # cari yang paling panjang dulu biar "tekanan darah" menang dari "darah"
        candidates = sorted(self.definition_index.keys(), key=len, reverse=True)
        for stemmed_key in candidates:
            if stemmed_key and stemmed_key in normalized:
                return self.definition_index[stemmed_key]
        # fuzzy fallback
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
        for stemmed_key, original in self.first_aid_index.items():
            if stemmed_key and stemmed_key in normalized:
                return original
        for stemmed_key, original in self.first_aid_index.items():
            if not stemmed_key:
                continue
            if fuzz.partial_ratio(stemmed_key, normalized) >= 88:
                return original
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
