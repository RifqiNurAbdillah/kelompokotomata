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
    bot_anim = (Path(__file__).parent / "assets" / "animation" / "boticonanim.json").read_text(encoding="utf-8")
    user_anim = (Path(__file__).parent / "assets" / "animation" / "usericonanim.json").read_text(encoding="utf-8")
    html_messages = []
    for idx, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        label = "Anda" if role == "user" else "HealthBuddy"
        avatar_id = f"avatar_{idx}_{role}"
        is_latest_assistant = role == "assistant" and idx == len(st.session_state.messages) - 1 and msg.get("animate")
        body = animated_words(msg["content"]) if is_latest_assistant else md_to_html(msg["content"])
        html_messages.append(
            f'<div class="hb-chat-row hb-chat-{role}" data-avatar="{avatar_id}" data-role="{role}">'
            f'<div class="hb-chat-avatar" id="{avatar_id}"></div>'
            f'<div class="hb-chat-bubble"><div class="hb-chat-name">{label}</div><div class="hb-chat-body">{body}</div></div>'
            f'</div>'
        )
    if st.session_state.pending_prompt:
        thinking_id = "avatar_thinking"
        html_messages.append(
            f'<div class="hb-chat-row hb-chat-assistant hb-thinking-row" data-avatar="{thinking_id}" data-role="assistant">'
            f'<div class="hb-chat-avatar" id="{thinking_id}"></div>'
            f'<div class="hb-chat-bubble hb-thinking-bubble"><div class="hb-chat-name">HealthBuddy sedang membaca keluhan</div>'
            f'<div class="hb-thinking-dots"><span></span><span></span><span></span></div></div></div>'
        )
    theme = st.session_state.theme
    colors = {
        "light": {
            "bg": "#f4f1ec", "surface": "#fffdfa", "surface2": "#f9f6ef", "fg": "#0f1b1e",
            "fgSoft": "#2c3a3e", "muted": "#687173", "border": "#d7d0c5", "accent": "#00a884",
            "accentDeep": "#0f6b5a", "accentSoft": "#d8f0e9"
        },
        "dark": {
            "bg": "#081214", "surface": "#132123", "surface2": "#182a2d", "fg": "#f3eee4",
            "fgSoft": "#d6d0c5", "muted": "#979b98", "border": "#26383c", "accent": "#2cd4ad",
            "accentDeep": "#8ee9cf", "accentSoft": "#123a33"
        },
    }[theme]
    height = min(640, max(430, len(st.session_state.messages) * 118 + 130))
    rows = "".join(html_messages)
    components.html(
        f"""
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
        <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; background: transparent; color: {colors['fg']}; }}
        .hb-chat-window {{ height: {height}px; overflow-y: auto; padding: 18px; border: 1px solid {colors['border']}; border-radius: 28px 10px 28px 28px; background: linear-gradient(180deg, {colors['surface']} 0%, {colors['surface2']} 100%); scroll-behavior: smooth; }}
        .hb-chat-row {{ display: flex; align-items: flex-start; gap: 12px; margin-bottom: 18px; animation: rowIn 360ms ease both; }}
        .hb-chat-user {{ flex-direction: row-reverse; }}
        .hb-chat-avatar {{ width: 46px; height: 46px; flex: 0 0 46px; border-radius: 999px; overflow: hidden; border: 1px solid {colors['accent']}; background: {colors['accentSoft']}; }}
        .hb-chat-user .hb-chat-avatar {{ border-color: {colors['fg']}; background: {colors['fg']}; }}
        .hb-chat-bubble {{ max-width: min(78%, 760px); width: fit-content; padding: 14px 16px; border: 1px solid {colors['border']}; border-radius: 4px 18px 18px 18px; background: {colors['surface']}; color: {colors['fg']}; }}
        .hb-chat-user .hb-chat-bubble {{ border-color: {colors['fg']}; border-radius: 18px 4px 18px 18px; background: {colors['fg']}; color: {colors['surface']}; }}
        .hb-chat-name {{ margin-bottom: 8px; font: 700 10px/1 JetBrains Mono, monospace; letter-spacing: .14em; text-transform: uppercase; color: {colors['accentDeep']}; }}
        .hb-chat-user .hb-chat-name {{ color: rgba(255,255,255,.68); }}
        .hb-chat-body p {{ margin: 0 0 8px; line-height: 1.62; font-size: 14px; }}
        .hb-chat-body p:last-child {{ margin-bottom: 0; }}
        .hb-chat-body ul, .hb-chat-body ol {{ margin: 8px 0 10px; padding-left: 20px; }}
        .hb-chat-body li {{ margin-bottom: 5px; line-height: 1.55; }}
        .hb-chat-body em {{ color: {colors['accentDeep']}; }}
        .hb-chat-user .hb-chat-body em {{ color: {colors['accent']}; }}
        .hb-word-stream span {{ display: inline-block; opacity: 0; transform: translateY(5px); animation: wordIn 260ms ease forwards; }}
        .hb-thinking-dots {{ display: inline-flex; align-items: center; gap: 6px; height: 22px; }}
        .hb-thinking-dots span {{ width: 8px; height: 8px; border-radius: 999px; background: {colors['accent']}; animation: thinking 1s ease-in-out infinite; }}
        .hb-thinking-dots span:nth-child(2) {{ animation-delay: .15s; }}
        .hb-thinking-dots span:nth-child(3) {{ animation-delay: .3s; }}
        @keyframes rowIn {{ from {{ opacity: 0; transform: translateY(10px); filter: blur(2px); }} to {{ opacity: 1; transform: translateY(0); filter: blur(0); }} }}
        @keyframes wordIn {{ to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes thinking {{ 0%, 80%, 100% {{ opacity: .32; transform: translateY(0); }} 40% {{ opacity: 1; transform: translateY(-4px); }} }}
        </style>
        </head>
        <body>
        <main class="hb-chat-window" id="chatWindow">{rows}</main>
        <script>
        const botAnim = {bot_anim};
        const userAnim = {user_anim};
        document.querySelectorAll('.hb-chat-row').forEach((row) => {{
          const avatar = row.querySelector('.hb-chat-avatar');
          const data = row.dataset.role === 'user' ? userAnim : botAnim;
          if (avatar && window.lottie) {{
            lottie.loadAnimation({{ container: avatar, renderer: 'svg', loop: true, autoplay: true, animationData: data }});
          }}
        }});
        const chat = document.getElementById('chatWindow');
        chat.scrollTop = chat.scrollHeight;
        </script>
        </body>
        </html>
        """,
        height=height + 4,
        scrolling=False,
    )


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
