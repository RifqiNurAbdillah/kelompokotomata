"""HealthBuddy Streamlit application."""

import html
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components

from core import HealthBuddyFSM, State
from data import (
    CATEGORIES,
    DEFINITIONS,
    DISEASES,
    EMERGENCY_NUMBERS,
    FAQ,
    FIRST_AID,
    WELLNESS_TIPS,
    find_nearby_hospitals,
)

st.set_page_config(
    page_title="HealthBuddy - Asisten Edukasi Kesehatan",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)


PAGES = {
    "HOME": "Beranda",
    "CHAT": "Chatbot",
    "KNOWLEDGE": "Knowledge",
    "FIRST_AID": "P3K",
}


def load_styles():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def inject_runtime(theme):
    components.html(
        f"""
        <script>
        const doc = window.parent.document;
        doc.documentElement.setAttribute('data-hb-theme', '{theme}');
        doc.body.setAttribute('data-hb-theme', '{theme}');
        </script>
        """,
        height=0,
    )


def init_state():
    if "bot" not in st.session_state:
        st.session_state.bot = HealthBuddyFSM()
        st.session_state.bot.step("")
        st.session_state.messages = [
            {"role": "assistant", "content": st.session_state.bot.get_response()}
        ]
    if "page" not in st.session_state:
        st.session_state.page = "HOME"
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "tip_index" not in st.session_state:
        st.session_state.tip_index = 0
    if "hospital_lookup" not in st.session_state:
        st.session_state.hospital_lookup = False
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def preserve_theme_reset(page="CHAT"):
    theme = st.session_state.theme
    st.session_state.clear()
    init_state()
    st.session_state.theme = theme
    st.session_state.page = page


def icon(name, size=18):
    paths = {
        "cross": '<path d="M12 5v14M5 12h14"/>',
        "activity": '<path d="M22 12h-4l-3 8L9 4l-3 8H2"/>',
        "shield-check": '<path d="M20 13c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V5l8-3 8 3v8Z"/><path d="m9 12 2 2 4-4"/>',
        "workflow": '<rect width="8" height="8" x="3" y="3" rx="2"/><rect width="8" height="8" x="13" y="13" rx="2"/><path d="M11 7h4a2 2 0 0 1 2 2v4M7 11v4a2 2 0 0 0 2 2h4"/>',
        "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
        "message-circle": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5Z"/>',
        "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
        "shield-plus": '<path d="M20 13c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V5l8-3 8 3v8Z"/><path d="M9 12h6M12 9v6"/>',
        "user-round": '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
        "triangle-alert": '<path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3Z"/><path d="M12 9v4M12 17h.01"/>',
        "phone-call": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z"/>',
    }
    body = paths.get(name, paths["activity"])
    return f'<svg class="hb-icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'


def lottie_html(file_name, class_name, height=240):
    anim_path = Path(__file__).parent / "assets" / "animation" / file_name
    if not anim_path.exists():
        return f'<div class="{class_name} hb-lottie-missing"></div>'
    data = anim_path.read_text(encoding="utf-8")
    holder_id = f"lottie_{file_name.replace('.', '_').replace('-', '_')}"
    components.html(
        f"""
        <div id="{holder_id}" style="width:100%;height:{height}px"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
        <script>
        const container = document.getElementById('{holder_id}');
        lottie.loadAnimation({{
          container,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          animationData: {data}
        }});
        </script>
        """,
        height=height,
    )
    return ""


def md_to_html(text):
    safe = html.escape(text or "")
    safe = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"\*(.*?)\*", r"<em>\1</em>", safe)
    lines = safe.splitlines()
    output = []
    in_ul = False
    in_ol = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if in_ol:
                output.append("</ol>")
                in_ol = False
            continue
        if stripped.startswith("- "):
            if not in_ul:
                output.append("<ul>")
                in_ul = True
            output.append(f"<li>{stripped[2:]}</li>")
            continue
        if re.match(r"^\d+\.\s", stripped):
            if not in_ol:
                output.append("<ol>")
                in_ol = True
            item_text = re.sub(r"^\d+\.\s", "", stripped)
            output.append(f"<li>{item_text}</li>")
            continue
        if in_ul:
            output.append("</ul>")
            in_ul = False
        if in_ol:
            output.append("</ol>")
            in_ol = False
        output.append(f"<p>{stripped}</p>")
    if in_ul:
        output.append("</ul>")
    if in_ol:
        output.append("</ol>")
    return "".join(output)


def plain_text(text):
    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text or "")
    clean = re.sub(r"\*(.*?)\*", r"\1", clean)
    clean = re.sub(r"^[-\d.\s]+", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def animated_words(text):
    words = plain_text(text).split()
    spans = []
    for idx, word in enumerate(words[:180]):
        spans.append(f'<span style="animation-delay:{idx * 0.035:.3f}s">{html.escape(word)} </span>')
    return '<p class="hb-word-stream">' + ''.join(spans) + '</p>'


def warm_response(raw):
    text = raw.strip()
    emergency = "PERINGATAN GEJALA KRITIS" in text or "mode peringatan darurat" in text.lower()
    if emergency:
        return text
    if text.startswith("Halo"):
        return text
    return (
        "Baik, saya bantu rangkum dengan tenang. Informasi berikut bersifat edukatif dan tidak menggantikan pemeriksaan tenaga medis.\n\n"
        f"{text}\n\n"
        "Jika keluhan terasa memburuk, berlangsung beberapa hari, atau disertai tanda bahaya, sebaiknya segera periksa ke fasilitas kesehatan terdekat."
    )


def run_prompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.session_state.tip_index += 1
    st.rerun()


def nav_button(label, page, key, icon_name):
    active = st.session_state.page == page
    btn_type = "primary" if active else "secondary"
    if st.button(f"{label}", key=key, type=btn_type, use_container_width=True):
        st.session_state.page = page
        st.rerun()


def render_header():
    st.markdown(
        f"""
        <header class="hb-shell hb-header">
            <div class="hb-brand">
                <span class="hb-brand-mark">{icon('cross', 22)}</span>
                <span class="hb-brand-copy"><strong>HealthBuddy</strong><small>Rule-based medical assistant</small></span>
            </div>
            <div class="hb-status-pill">{icon('activity', 16)} FSM aktif</div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 1, 1, 1, 0.9], gap="small")
    with cols[0]:
        nav_button("Beranda", "HOME", "nav_home", "layout-dashboard")
    with cols[1]:
        nav_button("Chatbot", "CHAT", "nav_chat", "message-circle")
    with cols[2]:
        nav_button("Knowledge", "KNOWLEDGE", "nav_knowledge", "database")
    with cols[3]:
        nav_button("P3K", "FIRST_AID", "nav_p3k", "shield-plus")
    with cols[4]:
        label = "Gelap" if st.session_state.theme == "light" else "Terang"
        if st.button(label, key="theme_toggle", use_container_width=True):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()


def render_home():
    st.markdown(
        f"""
        <section class="hb-shell hb-hero">
            <div class="hb-hero-copy">
                <span class="hb-kicker">Teori Bahasa dan Otomata</span>
                <h1>Asisten kesehatan yang bekerja dari aturan, bukan dari API AI.</h1>
                <p>HealthBuddy mengenali keluhan ringan, istilah medis, dan panduan P3K melalui Finite State Machine, stemming Bahasa Indonesia, serta pencocokan pola.</p>
                <div class="hb-hero-actions">
                    <span>{icon('shield-check', 17)} Tanpa diagnosis</span>
                    <span>{icon('workflow', 17)} FSM transparan</span>
                    <span>{icon('database', 17)} Knowledge base lokal</span>
                </div>
            </div>
            <div class="hb-hero-board">
                <div class="hb-mini-chart"><span></span><span></span><span></span><span></span><span></span></div>
                <strong>30</strong><small>kondisi kesehatan</small>
                <strong>{len(DEFINITIONS)}</strong><small>istilah medis</small>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    lottie_html("landingpageanim.json", "hb-landing-lottie", height=260)

    c1, c2, c3 = st.columns([1.15, 0.85, 1], gap="medium")
    cards = [
        (c1, "message-circle", "Mulai konsultasi", "Ceritakan keluhan seperti demam, batuk, mual, pusing, atau gejala ringan lain.", "Buka chatbot", "CHAT", "home_chat"),
        (c2, "book-open", "Baca knowledge", "Telusuri penyakit, definisi istilah, dan FAQ kesehatan dengan bahasa ringkas.", "Lihat data", "KNOWLEDGE", "home_data"),
        (c3, "shield-plus", "Panduan P3K", "Ikuti langkah pertolongan pertama untuk luka, mimisan, tersedak, dan kondisi darurat ringan.", "Buka P3K", "FIRST_AID", "home_p3k"),
    ]
    for col, ico, title, desc, btn, page, key in cards:
        with col:
            st.markdown(
                f"""
                <article class="hb-card hb-service-card reveal-card">
                    <div class="hb-card-icon">{icon(ico, 22)}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if st.button(btn, key=key, use_container_width=True, type="primary" if page == "CHAT" else "secondary"):
                st.session_state.page = page
                st.rerun()

    st.markdown('<div class="hb-section-gap"></div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4, gap="small")
    stats = [(len(DISEASES), "kondisi"), (len(FIRST_AID), "P3K"), (len(FAQ), "FAQ"), ("11", "state FSM")]
    for col, (num, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f'<div class="hb-stat"><strong>{num}</strong><span>{label}</span></div>', unsafe_allow_html=True)


def state_label():
    state = st.session_state.bot.state
    if state == State.EMERGENCY:
        return "danger", "Mode darurat", "Percakapan dikunci untuk mengutamakan rujukan medis."
    if state in (State.TRIAGE, State.CLARIFY):
        return "active", "Menelaah keluhan", "Sistem sedang mengumpulkan gejala tambahan."
    if state == State.ADVICE:
        return "active", "Saran tersedia", "Baca catatan dan pertimbangkan pemeriksaan bila memburuk."
    return "idle", "Siap menerima pesan", "Tulis keluhan dengan bahasa sehari-hari."


def render_chat_messages():
    html_messages = []
    for idx, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        label = "Anda" if role == "user" else "HealthBuddy"
        avatar_icon = "user-round" if role == "user" else "cross"
        is_latest_assistant = role == "assistant" and idx == len(st.session_state.messages) - 1 and msg.get("animate")
        body = animated_words(msg["content"]) if is_latest_assistant else md_to_html(msg["content"])
        html_messages.append(
            f"""
            <div class="hb-chat-row hb-chat-{role}">
                <div class="hb-chat-avatar">{icon(avatar_icon, 17)}</div>
                <div class="hb-chat-bubble">
                    <div class="hb-chat-name">{label}</div>
                    <div class="hb-chat-body">{body}</div>
                </div>
            </div>
            """
        )
    if st.session_state.pending_prompt:
        html_messages.append(
            f"""
            <div class="hb-chat-row hb-chat-assistant hb-thinking-row">
                <div class="hb-chat-avatar">{icon('cross', 17)}</div>
                <div class="hb-chat-bubble hb-thinking-bubble">
                    <div class="hb-chat-name">HealthBuddy sedang membaca keluhan</div>
                    <div class="hb-thinking-dots"><span></span><span></span><span></span></div>
                </div>
            </div>
            """
        )
    st.markdown('<div class="hb-chat-window">' + "".join(html_messages) + "</div>", unsafe_allow_html=True)


def complete_pending_reply():
    prompt = st.session_state.get("pending_prompt")
    if not prompt:
        return
    time.sleep(0.75)
    st.session_state.bot.step(prompt)
    reply = warm_response(st.session_state.bot.get_response())
    st.session_state.messages.append({"role": "assistant", "content": reply, "animate": True})
    st.session_state.pending_prompt = None
    st.rerun()


def render_chat():
    status, title, desc = state_label()
    left, right = st.columns([1.8, 1], gap="medium")
    with left:
        st.markdown(
            f"""
            <section class="hb-shell hb-chat-page">
                <div class="hb-panel-head"><span>Ruang konsultasi</span><strong>{title}</strong></div>
                <div class="hb-state-line hb-state-{status}">{icon('activity', 16)}<span>{desc}</span></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        render_chat_messages()
        complete_pending_reply()
        prompt = st.chat_input("Tulis keluhan atau pertanyaan kesehatan Anda")
        if prompt:
            run_prompt(prompt)
        b1, b2, b3 = st.columns([1, 1, 1.2], gap="small")
        with b1:
            if st.button("Mulai ulang", key="reset_chat", use_container_width=True):
                preserve_theme_reset("CHAT")
                st.rerun()
        with b2:
            if st.button("Panduan", key="help_chat", use_container_width=True):
                run_prompt("bantuan")
        with b3:
            if st.session_state.bot.state == State.EMERGENCY and st.button("Cari rumah sakit terdekat", key="lookup_hospital", type="primary", use_container_width=True):
                st.session_state.hospital_lookup = True
                st.rerun()
        render_hospital_lookup()

    with right:
        lottie_html("boticonanim.json", "hb-bot-lottie", height=170)
        lottie_html("usericonanim.json", "hb-user-lottie", height=120)
        st.markdown(
            f"""
            <aside class="hb-aside-card hb-warning-card">
                <div class="hb-card-icon">{icon('triangle-alert', 20)}</div>
                <h3>Catatan medis</h3>
                <p>HealthBuddy bersifat edukatif. Untuk diagnosis, terapi, dan resep, tetap gunakan layanan tenaga kesehatan profesional.</p>
            </aside>
            """,
            unsafe_allow_html=True,
        )
        quick = [
            ("Saya demam dan pusing", "saya demam dan pusing"),
            ("Perut terasa perih", "perut saya perih dan mual"),
            ("Batuk berdahak", "saya batuk berdahak dan pilek"),
            ("Apa itu kolesterol", "apa itu kolesterol"),
        ]
        st.markdown('<div class="hb-aside-card"><div class="hb-panel-head"><span>Prompt cepat</span><strong>Pilih topik</strong></div>', unsafe_allow_html=True)
        for idx, (label, prompt_text) in enumerate(quick):
            if st.button(label, key=f"quick_{idx}", use_container_width=True):
                run_prompt(prompt_text)
        st.markdown('</div>', unsafe_allow_html=True)

        log_rows = []
        for entry in st.session_state.bot.get_transition_log()[-6:]:
            log_rows.append(f"<li><span>{entry['from']}</span><b>{entry['to']}</b><small>{html.escape(entry['reason'])}</small></li>")
        st.markdown(
            f"""
            <div class="hb-aside-card">
                <div class="hb-panel-head"><span>FSM log</span><strong>Transisi</strong></div>
                <ol class="hb-fsm-log">{''.join(log_rows)}</ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tip = WELLNESS_TIPS[st.session_state.tip_index % len(WELLNESS_TIPS)]
        st.markdown(f'<blockquote class="hb-tip">{html.escape(tip)}</blockquote>', unsafe_allow_html=True)


def render_hospital_lookup():
    if not st.session_state.hospital_lookup:
        return
    try:
        from streamlit_js_eval import get_geolocation
    except Exception:
        st.info("Fitur lokasi membutuhkan paket streamlit-js-eval.")
        return
    loc = get_geolocation()
    if not loc or "coords" not in loc:
        st.info("Izinkan akses lokasi pada browser untuk melihat rumah sakit terdekat.")
        return
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    with st.spinner("Mencari rumah sakit terdekat..."):
        hospitals = find_nearby_hospitals(lat, lon, limit=3)
    cards = []
    for item in hospitals:
        cards.append(
            f"<article><strong>{html.escape(item['name'])}</strong><span>{item['distance_km']} km</span><small>{html.escape(item['address'])}</small></article>"
        )
    st.markdown(f'<div class="hb-hospital-list">{"".join(cards) or "<p>Data rumah sakit tidak ditemukan.</p>"}</div>', unsafe_allow_html=True)


def render_knowledge():
    st.markdown(
        f"""
        <section class="hb-shell hb-page-title">
            <span>Knowledge base</span>
            <h1>Direktori kesehatan yang dapat ditelusuri.</h1>
            <p>Cari penyakit, kategori keluhan, definisi istilah, dan pertanyaan umum.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    query = st.text_input("Cari penyakit atau istilah", placeholder="Contoh: flu, lambung, kolesterol, tekanan darah").strip().lower()
    tab_disease, tab_definition, tab_faq = st.tabs(["Penyakit", "Istilah", "FAQ"])
    with tab_disease:
        render_disease_grid(query)
    with tab_definition:
        render_definition_grid(query)
    with tab_faq:
        render_faq_grid(query)


def render_disease_grid(query):
    filtered = []
    for key, info in DISEASES.items():
        haystack = " ".join([str(key), str(info["nama"]), str(info["kategori"]), str(info.get("definisi") or "")]).lower()
        if not query or query in haystack:
            filtered.append((key, info))
    cols = st.columns(2, gap="medium")
    for idx, (_, info) in enumerate(filtered[:24]):
        with cols[idx % 2]:
            category = str(CATEGORIES.get(info["kategori"], info["kategori"]))
            st.markdown(
                f"""
                <article class="hb-data-card">
                    <span>{html.escape(category)}</span>
                    <h3>{html.escape(info['nama'])}</h3>
                    <p>{html.escape(str(info.get('definisi') or ''))}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
    if not filtered:
        st.info("Tidak ada data penyakit yang cocok dengan kata kunci tersebut.")


def render_definition_grid(query):
    rows = [(term, desc) for term, desc in DEFINITIONS.items() if not query or query in term.lower() or query in desc.lower()]
    cols = st.columns(2, gap="medium")
    for idx, (term, desc) in enumerate(rows[:30]):
        with cols[idx % 2]:
            st.markdown(f'<article class="hb-data-card compact"><h3>{html.escape(term.title())}</h3><p>{html.escape(desc)}</p></article>', unsafe_allow_html=True)
    if not rows:
        st.info("Tidak ada istilah yang cocok dengan kata kunci tersebut.")


def render_faq_grid(query):
    rows = [(key, item) for key, item in FAQ.items() if not query or query in key.lower() or query in item["judul"].lower() or query in item["jawaban"].lower()]
    for _, item in rows:
        with st.expander(item["judul"]):
            st.write(item["jawaban"])
    if not rows:
        st.info("Tidak ada FAQ yang cocok dengan kata kunci tersebut.")


def render_first_aid():
    st.markdown(
        f"""
        <section class="hb-shell hb-page-title hb-firstaid-head">
            <span>Pertolongan pertama</span>
            <h1>Panduan ringkas sebelum bantuan profesional tiba.</h1>
            <p>Gunakan hanya untuk kondisi awal. Jika terdapat tanda bahaya, segera hubungi layanan darurat.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.7, 1], gap="medium")
    with left:
        for key, info in FIRST_AID.items():
            steps = "".join(f"<li>{html.escape(step)}</li>" for step in info["langkah"][:6])
            st.markdown(
                f"""
                <article class="hb-aid-card">
                    <div><span>{html.escape(key)}</span><h3>{html.escape(info['judul'])}</h3></div>
                    <ol>{steps}</ol>
                    <p>{html.escape(info['warning'])}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
    with right:
        phone_rows = "".join(f"<li><span>{html.escape(name)}</span><strong>{html.escape(num)}</strong></li>" for name, num in EMERGENCY_NUMBERS.items())
        st.markdown(
            f"""
            <aside class="hb-emergency-card">
                <div class="hb-card-icon">{icon('phone-call', 22)}</div>
                <h3>Nomor darurat</h3>
                <ul>{phone_rows}</ul>
            </aside>
            """,
            unsafe_allow_html=True,
        )


def render_footer():
    st.markdown(
        """
        <footer class="hb-footer">
            <span>HealthBuddy</span>
            <span>Finite State Machine</span>
            <span>Rule-based NLP</span>
            <span>Teori Bahasa dan Otomata</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_state()
    load_styles()
    inject_runtime(st.session_state.theme)
    render_header()

    page = st.session_state.page
    if page == "HOME":
        render_home()
    elif page == "CHAT":
        render_chat()
    elif page == "KNOWLEDGE":
        render_knowledge()
    elif page == "FIRST_AID":
        render_first_aid()

    render_footer()


if __name__ == "__main__":
    main()
