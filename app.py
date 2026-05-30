"""HealthBuddy Streamlit application — bento layout with theme toggle."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components
from core import HealthBuddyFSM, State
from data import (
    DISEASES,
    CATEGORIES,
    DEFINITIONS,
    FAQ,
    FIRST_AID,
    EMERGENCY_NUMBERS,
    WELLNESS_TIPS,
)

st.set_page_config(
    page_title="HealthBuddy — Asisten Edukasi Kesehatan",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def apply_theme(theme):
    components.html(
        f"""
        <script>
        const root = window.parent.document.documentElement;
        root.setAttribute('data-hb-theme', '{theme}');
        const body = window.parent.document.body;
        body.setAttribute('data-hb-theme', '{theme}');
        </script>
        """,
        height=0,
    )


def init_state():
    if "bot" not in st.session_state:
        st.session_state.bot = HealthBuddyFSM()
        st.session_state.bot.step("")
        st.session_state.history = [
            {"role": "assistant", "content": st.session_state.bot.get_response()}
        ]
        st.session_state.tip_index = 0
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


def handle_user_input(prompt):
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.bot.step(prompt)
    reply = st.session_state.bot.get_response()
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.session_state.tip_index = st.session_state.get("tip_index", 0) + 1
    st.rerun()


def section_topbar():
    cols = st.columns([3, 2])
    with cols[0]:
        st.markdown(
            """
            <div class="hb-topbar-brand">
                <div class="hb-cross" aria-hidden="true"></div>
                <div>
                    <div class="hb-brand-label">HealthBuddy</div>
                    <div class="hb-brand-tag">Asisten Edukasi Berbasis FSM</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        meta_col, btn_col = st.columns([3, 1.4])
        with meta_col:
            st.markdown(
                """
                <div class="hb-topbar-meta" style="justify-content: flex-end; padding-top: 6px;">
                    <span class="hb-pulse-chip"><span class="hb-pulse-dot"></span>Sistem Aktif</span>
                    <span class="hb-chip">TBO &middot; v1.1</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with btn_col:
            current = st.session_state.theme
            label = "Mode Gelap" if current == "light" else "Mode Terang"
            if st.button(label, key="theme_toggle", use_container_width=True):
                st.session_state.theme = "dark" if current == "light" else "light"
                st.rerun()


def section_hero():
    st.markdown(
        """
        <section class="hb-hero">
            <div class="hb-hero-grid">
                <div>
                    <div class="hb-hero-tag">Vol. 01 &mdash; Edukasi Mandiri</div>
                    <h1 class="hb-hero-title">Konsultasi keluhan ringan, <em>dengan tenang.</em></h1>
                </div>
                <p class="hb-hero-lead">
                    Tanpa diagnosis. Tanpa resep. HealthBuddy memandu Anda mengenali keluhan,
                    memahami istilah medis, dan mengetahui kapan harus segera mencari bantuan profesional.
                </p>
            </div>
            <div class="hb-ekg" aria-hidden="true"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_state_indicator(bot):
    state = bot.state
    if state == State.EMERGENCY:
        cls, label, desc = "alert", "Mode Darurat", "Sistem terkunci. Cari bantuan medis."
    elif state == State.TRIAGE:
        cls, label, desc = "active", "Mengakumulasi Gejala", "Sebutkan keluhan tambahan."
    elif state == State.ADVICE:
        cls, label, desc = "active", "Memberi Saran", "Edukasi keluhan ringan."
    elif state in (State.DEFINITION, State.FAQ_VIEW, State.FIRST_AID_VIEW, State.EMERGENCY_INFO):
        cls, label, desc = "active", "Menyajikan Informasi", state.name.replace("_", " ").title()
    elif state == State.GREETING:
        cls, label, desc = "idle", "Menunggu Keluhan", "Silakan mulai percakapan."
    elif state == State.MAIN_MENU:
        cls, label, desc = "idle", "Menu Utama", "Pilih topik atau ceritakan keluhan."
    elif state == State.CLARIFY:
        cls, label, desc = "active", "Meminta Klarifikasi", "Coba reformulasi pertanyaan."
    else:
        cls, label, desc = "idle", state.name.title(), "Sistem siap."

    st.markdown(
        f"""
        <div class="hb-state hb-state-{cls}">
            <div class="hb-state-dot"></div>
            <div>
                <div class="hb-state-label">{label}</div>
                <div class="hb-state-desc">{desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_chat_messages():
    for msg in st.session_state.history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])


def section_disclaimer():
    st.markdown(
        """
        <aside class="hb-disclaimer">
            <div class="hb-disclaimer-mark">!</div>
            <div>
                <strong>Catatan Penting.</strong>
                HealthBuddy adalah alat edukasi berbasis aturan, bukan pengganti tenaga medis.
                Untuk diagnosis dan terapi, konsultasikan dengan dokter atau fasilitas kesehatan.
                Dalam keadaan darurat, hubungi <strong>119</strong>.
            </div>
        </aside>
        """,
        unsafe_allow_html=True,
    )


def section_pullquote():
    tips = WELLNESS_TIPS
    idx = st.session_state.get("tip_index", 0) % len(tips)
    quote = tips[idx]
    st.markdown(
        f"""
        <blockquote class="hb-pullquote">
            <p>&ldquo;{quote}&rdquo;</p>
            <footer>Tips harian #{idx + 1:02d}</footer>
        </blockquote>
        """,
        unsafe_allow_html=True,
    )


def section_quick_actions():
    st.markdown(
        """
        <div class="hb-card hb-card-accent hb-card-tight">
            <div class="hb-bento-eyebrow">Aksi Cepat</div>
            <div class="hb-bento-title">Mulai dari sini</div>
        """,
        unsafe_allow_html=True,
    )

    quick = [
        ("Saya merasa demam", "saya demam dan pusing"),
        ("Perut perih / maag", "perut saya perih, gejala maag"),
        ("Apa itu kolesterol", "apa itu kolesterol"),
        ("P3K luka bakar", "pertolongan pertama luka bakar"),
        ("Tips tidur ideal", "berapa lama tidur ideal"),
        ("Nomor darurat", "nomor darurat kesehatan"),
    ]

    cols = st.columns(2)
    for i, (label, prompt) in enumerate(quick):
        with cols[i % 2]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                handle_user_input(prompt)
    st.markdown("</div>", unsafe_allow_html=True)


def section_stats():
    total_diseases = len(DISEASES)
    total_definitions = len(DEFINITIONS)
    total_first_aid = len(FIRST_AID)
    total_faq = len(FAQ)
    st.markdown(
        f"""
        <div class="hb-stat-bento">
            <div class="hb-stat-tile"><div class="hb-stat-num">{total_diseases}</div><div class="hb-stat-lbl">Kondisi</div></div>
            <div class="hb-stat-tile"><div class="hb-stat-num">{total_definitions}</div><div class="hb-stat-lbl">Istilah</div></div>
            <div class="hb-stat-tile"><div class="hb-stat-num">{total_first_aid}</div><div class="hb-stat-lbl">P3K</div></div>
            <div class="hb-stat-tile"><div class="hb-stat-num">{total_faq}</div><div class="hb-stat-lbl">FAQ</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_categories():
    by_category = {}
    for key, info in DISEASES.items():
        by_category.setdefault(info["kategori"], []).append(info["nama"])
    rows = []
    for cat_key, names in sorted(by_category.items(), key=lambda x: -len(x[1])):
        label = CATEGORIES.get(cat_key, cat_key)
        rows.append(f'<li><span class="hb-cat">{label}</span><span class="hb-count">{len(names)}</span></li>')
    st.markdown(
        f"""
        <div class="hb-card hb-card-tight">
            <div class="hb-bento-eyebrow">Indeks</div>
            <div class="hb-bento-title">Cakupan Pengetahuan</div>
            <ul class="hb-cat-list">{''.join(rows)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_transition_log(bot):
    log = bot.get_transition_log()
    if not log:
        return
    rows = []
    for entry in log[-5:]:
        rows.append(
            f'<li><span class="hb-tr-from">{entry["from"]}</span>'
            f'<span class="hb-arrow">&rarr;</span>'
            f'<span class="hb-tr-to">{entry["to"]}</span>'
            f'<div class="hb-tr-reason">{entry["reason"]}</div></li>'
        )
    st.markdown(
        f"""
        <div class="hb-card hb-card-tight">
            <div class="hb-bento-eyebrow">Log FSM</div>
            <div class="hb-bento-title">Jejak State</div>
            <ol class="hb-tr-list">{''.join(rows)}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_footer():
    st.markdown(
        """
        <footer class="hb-footer">
            <span>HealthBuddy &middot; FSM &middot; Rule-based NLP</span>
            <span><span class="hb-divider">/</span>Tugas Akhir Teori Bahasa &amp; Otomata</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_state()
    load_css()
    apply_theme(st.session_state.theme)

    section_topbar()
    section_hero()

    col_chat, col_side = st.columns([2.05, 1], gap="large")

    with col_chat:
        section_state_indicator(st.session_state.bot)

        chat_box = st.container(height=520)
        with chat_box:
            section_chat_messages()

        prompt = st.chat_input("Ketik keluhan, gejala, atau pertanyaan kesehatan Anda...")
        if prompt:
            handle_user_input(prompt)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Mulai Ulang Konsultasi", use_container_width=True, key="reset_main"):
                st.session_state.clear()
                st.rerun()
        with col_b:
            if st.button("Tampilkan Bantuan", use_container_width=True, key="help_main"):
                handle_user_input("bantuan")

    with col_side:
        section_disclaimer()
        section_pullquote()
        section_quick_actions()
        section_stats()
        section_categories()
        section_transition_log(st.session_state.bot)

    section_footer()


if __name__ == "__main__":
    main()
