"""Finite State Machine HealthBuddy.

State diagram:

    [IDLE] --start--> [GREETING]
    [GREETING] --any input--> [MAIN_MENU]
    [MAIN_MENU] --symptom mentioned--> [TRIAGE]
                --ask definition--> [DEFINITION]
                --ask first aid--> [FIRST_AID]
                --ask faq--> [FAQ]
                --emergency info--> [EMERGENCY_INFO]
                --red flag--> [EMERGENCY]
    [TRIAGE] --more symptoms--> [TRIAGE] (accumulate)
             --confident match--> [ADVICE]
             --no match--> [CLARIFY]
    [CLARIFY] --user clarifies--> [TRIAGE]
    [ADVICE] --any followup--> [MAIN_MENU]
    [EMERGENCY] --reset--> [IDLE]
    Any state --red flag detected--> [EMERGENCY]
    Any state --reset intent--> [IDLE]
"""

from enum import Enum, auto
from data import DISEASES, RED_FLAGS, FIRST_AID, DEFINITIONS, FAQ, EMERGENCY_NUMBERS, CATEGORIES, WELLNESS_TIPS
from data import check_needs_hospital_recommendation, HOSPITAL_RECOMMENDATION_TEXT
from .nlp import NLPEngine


class State(Enum):
    IDLE = auto()
    GREETING = auto()
    MAIN_MENU = auto()
    TRIAGE = auto()
    CLARIFY = auto()
    ADVICE = auto()
    DEFINITION = auto()
    FIRST_AID_VIEW = auto()
    FAQ_VIEW = auto()
    EMERGENCY_INFO = auto()
    EMERGENCY = auto()


CONFIDENCE_THRESHOLD = 4.0
TOP_K_SUGGESTIONS = 3


class HealthBuddyFSM:
    def __init__(self):
        self.nlp = NLPEngine()
        self.state = State.IDLE
        self.symptom_scores = {}
        self.last_disease = None
        self.transition_log = []
        self.response = ""

    # ---------- Public API ----------

    def get_response(self):
        return self.response

    def get_state_label(self):
        return self.state.name

    def get_transition_log(self):
        return list(self.transition_log)

    def reset(self):
        self.__init__()

    def step(self, user_input=""):
        text = user_input.strip()

        if self.state == State.IDLE:
            self._transition(State.GREETING, "start")
            self.response = self._render_greeting()
            return

        intent = self.nlp.detect_intent(text)

        if intent == "RESET":
            self.reset()
            self._transition(State.GREETING, "user_reset")
            self.response = self._render_greeting()
            return

        red_flag = self.nlp.detect_red_flag(text)
        if red_flag:
            self._transition(State.EMERGENCY, f"red_flag:{red_flag}")
            self.response = self._render_emergency(red_flag)
            return

        if self.state == State.EMERGENCY:
            self.response = (
                "Sistem masih dalam mode peringatan darurat. "
                "Pastikan Anda atau orang terdekat sudah mendapat bantuan medis. "
                "Ketik **mulai ulang** untuk konsultasi baru."
            )
            return

        if intent == "GREETING":
            self._transition(State.MAIN_MENU, "intent_greeting")
            self.response = self._render_main_menu(personal=True)
            return

        if intent == "GOODBYE":
            self._transition(State.MAIN_MENU, "intent_goodbye")
            self.response = (
                "Terima kasih sudah berkonsultasi. Jaga kesehatan Anda dengan istirahat cukup, "
                "makan bergizi, dan banyak minum air putih. Sampai jumpa kembali."
            )
            return

        if intent == "THANKS":
            self.response = "Sama-sama. Ada keluhan lain yang ingin Anda tanyakan?"
            return

        if intent == "HELP":
            self.response = self._render_help()
            return

        if intent == "EMERGENCY_INFO":
            self._transition(State.EMERGENCY_INFO, "intent_emergency_info")
            self.response = self._render_emergency_info()
            return

        if intent == "ASK_HOSPITAL":
            self.response = (
                "Untuk mencari rumah sakit atau klinik terdekat dari lokasi Anda, "
                "silakan klik tombol **📍 Cari RS Terdekat** di bawah kolom chat.\n\n"
                "Sistem akan meminta izin akses lokasi dari browser Anda, "
                "lalu menampilkan daftar rumah sakit terdekat lengkap dengan peta dan jarak."
            )
            return

        if intent == "ASK_DEFINITION":
            term = self.nlp.find_definition(text)
            if term:
                self._transition(State.DEFINITION, f"definition:{term}")
                self.response = self._render_definition(term)
            else:
                self.response = (
                    "Saya belum menemukan istilah yang Anda maksud di glosarium. "
                    "Coba sebutkan istilah secara langsung, contoh: *apa itu kolesterol*."
                )
            return

        if intent == "ASK_FIRST_AID":
            topic = self.nlp.find_first_aid(text)
            if topic:
                self._transition(State.FIRST_AID_VIEW, f"first_aid:{topic}")
                self.response = self._render_first_aid(topic)
            else:
                self.response = self._render_first_aid_menu()
            return

        if intent == "ASK_FAQ":
            topic = self.nlp.find_faq(text)
            if topic:
                self._transition(State.FAQ_VIEW, f"faq:{topic}")
                self.response = self._render_faq(topic)
            else:
                self.response = self._render_faq_menu()
            return

        # Direct lookup probes regardless of intent
        first_aid_topic = self.nlp.find_first_aid(text)
        if first_aid_topic and self.state in (State.GREETING, State.MAIN_MENU):
            self._transition(State.FIRST_AID_VIEW, f"first_aid_direct:{first_aid_topic}")
            self.response = self._render_first_aid(first_aid_topic)
            return

        definition_term = self.nlp.find_definition(text)
        disease_direct = self.nlp.find_disease(text)
        # Disease takes precedence over definition when both match
        if disease_direct:
            self._transition(State.ADVICE, f"disease_direct:{disease_direct}")
            self.last_disease = disease_direct
            self.response = self._render_advice(disease_direct, direct=True)
            return
        if definition_term and self.state in (State.GREETING, State.MAIN_MENU):
            self._transition(State.DEFINITION, f"definition_direct:{definition_term}")
            self.response = self._render_definition(definition_term)
            return

        # Symptom-based triage flow
        ranked, updated_scores = self.nlp.score_diseases(text, self.symptom_scores)
        if ranked:
            self.symptom_scores = updated_scores
            top = ranked[0]
            if top["score"] >= CONFIDENCE_THRESHOLD or len(ranked) == 1:
                self._transition(State.ADVICE, f"triage_advice:{top['disease']}")
                self.last_disease = top["disease"]
                self.response = self._render_advice(top["disease"], ranked=ranked)
                self.symptom_scores = {}
            else:
                self._transition(State.TRIAGE, f"triage_accum:{top['disease']}")
                self.response = self._render_triage(ranked)
            return

        # Affirmative response to a previous suggestion
        if intent == "AFFIRM" and self.last_disease:
            self.response = self._render_advice(self.last_disease, direct=True)
            return

        # Fallback: no intent, no symptom, no direct match
        self._transition(State.CLARIFY, "fallback_no_match")
        self.response = self._render_clarify()

    # ---------- Transition helpers ----------

    def _transition(self, new_state, reason):
        old = self.state.name
        self.state = new_state
        self.transition_log.append({
            "from": old,
            "to": new_state.name,
            "reason": reason,
        })
        if len(self.transition_log) > 20:
            self.transition_log = self.transition_log[-20:]

    # ---------- Renderers ----------

    def _render_greeting(self):
        return (
            "Halo, saya HealthBuddy. Asisten edukasi kesehatan berbasis Finite State Machine. "
            "Saya bisa membantu Anda mengenali gejala ringan, menjelaskan istilah medis, "
            "memberikan panduan P3K, dan menjawab pertanyaan kesehatan umum.\n\n"
            "**Ceritakan apa yang sedang Anda rasakan**, atau gunakan panel **Aksi Cepat** di samping."
        )

    def _render_main_menu(self, personal=False):
        prefix = "Hai, senang bertemu Anda. " if personal else ""
        return (
            f"{prefix}Ada beberapa hal yang bisa saya bantu:\n\n"
            "- Konsultasi gejala ringan, contoh: *saya batuk berdahak dan demam ringan*\n"
            "- Definisi istilah medis, contoh: *apa itu kolesterol*\n"
            "- Pertolongan pertama, contoh: *cara mengatasi luka bakar*\n"
            "- Tips gaya hidup sehat, contoh: *berapa lama tidur ideal*"
        )

    def _render_help(self):
        return (
            "**Cara berinteraksi dengan HealthBuddy:**\n\n"
            "1. Sebutkan gejala dengan bahasa sehari-hari, sistem akan mengenali kata kunci.\n"
            "2. Jika gejala kurang spesifik, sistem akan menanyakan informasi tambahan.\n"
            "3. Sebutkan beberapa gejala sekaligus untuk akurasi yang lebih baik.\n"
            "4. Ketik **mulai ulang** untuk membersihkan riwayat dan memulai konsultasi baru.\n\n"
            "Sistem ini berbasis FSM dengan 11 state utama dan akan otomatis berpindah ke "
            "**mode darurat** jika mendeteksi gejala kritis."
        )

    def _render_emergency(self, flag_key):
        info = RED_FLAGS[flag_key]
        text = (
            f"**PERINGATAN GEJALA KRITIS: {flag_key.upper()}**\n\n"
            f"Kategori: {info['kategori']}\n\n"
            f"**Mengapa ini darurat:**\n{info['alasan']}\n\n"
            f"**Tindakan segera:**\n{info['tindakan']}\n\n"
            "**Hubungi sekarang:**\n"
            "- Ambulans / Gawat Darurat: **119**\n"
            "- Atau langsung ke IGD rumah sakit terdekat\n\n"
            "Sistem dikunci dalam mode darurat. Keselamatan Anda yang utama. "
            "Ketik **mulai ulang** setelah situasi aman."
        )
        # Selalu tampilkan rekomendasi RS untuk kondisi darurat
        text += HOSPITAL_RECOMMENDATION_TEXT
        return text

    def _render_emergency_info(self):
        lines = ["**Daftar Nomor Penting Kesehatan:**\n"]
        for label, number in EMERGENCY_NUMBERS.items():
            lines.append(f"- {label}: **{number}**")
        lines.append(
            "\nSimpan nomor ini di kontak darurat ponsel Anda. Untuk situasi mengancam nyawa, "
            "hubungi 119 lebih dulu sebelum melakukan tindakan apapun."
        )
        return "\n".join(lines)

    def _render_triage(self, ranked):
        top = ranked[:TOP_K_SUGGESTIONS]
        lines = [
            "Berdasarkan keluhan yang Anda sampaikan, ada beberapa kemungkinan kondisi yang sedang saya pertimbangkan:",
            "",
        ]
        for i, item in enumerate(top, 1):
            d = DISEASES[item["disease"]]
            lines.append(f"{i}. **{d['nama']}** (skor kecocokan: {item['score']:.1f})")
        lines.append("")
        lines.append(
            "Untuk mempersempit, mohon ceritakan **gejala lain** yang Anda rasakan, "
            "misal: durasi (sudah berapa hari), intensitas, atau pemicu yang Anda curigai."
        )
        return "\n".join(lines)

    def _render_advice(self, disease_key, ranked=None, direct=False):
        d = DISEASES[disease_key]
        lines = []
        if direct:
            lines.append(f"Berikut ringkasan tentang **{d['nama']}**:")
        else:
            lines.append(f"Kondisi yang paling cocok dengan keluhan Anda adalah **{d['nama']}**.")
        lines.append("")
        lines.append(f"_{d['definisi']}_")
        lines.append("")
        lines.append("**Gejala umum yang menyertai:**")
        for s in d.get("gejala_utama", []):
            lines.append(f"- {s}")
        lines.append("")
        lines.append("**Saran perawatan mandiri:**")
        for s in d.get("saran", []):
            lines.append(f"- {s}")
        lines.append("")
        lines.append(f"**Kapan harus ke dokter:** {d.get('kapan_ke_dokter', '-')}")
        lines.append("")
        lines.append(f"**Pencegahan:** {d.get('pencegahan', '-')}")

        if ranked and len(ranked) > 1:
            others = ranked[1:TOP_K_SUGGESTIONS]
            lines.append("")
            lines.append("Kemungkinan lain yang juga cocok dengan keluhan Anda:")
            for item in others:
                lines.append(f"- {DISEASES[item['disease']]['nama']}")

        lines.append("")
        lines.append(
            "_Catatan: informasi ini bersifat edukatif, bukan pengganti diagnosis dokter. "
            "Jika gejala memburuk atau tidak membaik dalam 2-3 hari, segera periksa ke fasilitas kesehatan._"
        )
        # Tambahkan rekomendasi RS jika disease terkait dengan kondisi overlap
        if check_needs_hospital_recommendation(disease_key):
            lines.append(HOSPITAL_RECOMMENDATION_TEXT)
        return "\n".join(lines)

    def _render_clarify(self):
        return (
            "Saya belum menangkap kata kunci kesehatan dari pesan Anda. Bisa Anda jelaskan dengan kata-kata berbeda?\n\n"
            "Contoh format yang efektif:\n"
            "- *kepala saya pusing dan badan demam sejak kemarin*\n"
            "- *perut saya perih kalau telat makan*\n"
            "- *saya batuk kering sudah seminggu*"
        )

    def _render_definition(self, term):
        meaning = DEFINITIONS[term]
        return f"**{term.title()}**\n\n{meaning}"

    def _render_first_aid(self, topic):
        info = FIRST_AID[topic]
        lines = [f"**P3K: {info['judul']}**\n", "**Langkah penanganan:**"]
        for i, step in enumerate(info["langkah"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append(f"**Peringatan:** {info['warning']}")
        # Tambahkan rekomendasi RS jika kondisi juga ada di RED_FLAGS
        if check_needs_hospital_recommendation(topic):
            lines.append(HOSPITAL_RECOMMENDATION_TEXT)
        return "\n".join(lines)

    def _render_first_aid_menu(self):
        lines = ["**Topik P3K yang tersedia:**\n"]
        for key, info in FIRST_AID.items():
            lines.append(f"- {info['judul']}")
        lines.append("\nSebutkan topik yang Anda butuhkan, contoh: *cara mengatasi mimisan*.")
        return "\n".join(lines)

    def _render_faq(self, topic):
        info = FAQ[topic]
        return f"**{info['judul']}**\n\n{info['jawaban']}"

    def _render_faq_menu(self):
        lines = ["**FAQ kesehatan yang sering ditanyakan:**\n"]
        for key, info in FAQ.items():
            lines.append(f"- {info['judul']}")
        lines.append("\nKetik salah satu topik untuk informasi lengkapnya.")
        return "\n".join(lines)
