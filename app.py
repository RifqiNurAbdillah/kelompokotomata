"""
HealthBuddy — Premium Health Digital Portal
Inspired by Halodoc & Alodokter Ecosystem
Designed with clean UI/UX, precise spacing, and fully custom components.
"""

import sys
from pathlib import Path

# Memastikan core path terintegrasi dengan aman
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

# Konfigurasi halaman tingkat premium (Wide Layout)
st.set_page_config(
    page_title="HealthBuddy — Mitra Kesehatan Digital Terpercaya",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_premium_styles():
    """Memuat asset styles CSS eksternal sekaligus melakukan override komponen untuk tema Halodoc."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    
    # Injeksi CSS Custom untuk nuansa Hijau Apoteker (#2e7d32) premium, clean, dan presisi
    st.markdown("""
        <style>
        /* Kontrol padding halaman utama agar seimbang dan rapi */
        .block-container { 
            padding-top: 1rem !important; 
            padding-bottom: 0rem !important; 
            max-width: 1240px; 
        }
        
        /* Navigasi Kapsul & Header Border */
        .hd-header-line {
            border-bottom: 2px solid rgba(46, 125, 50, 0.15);
            margin: 0.5rem 0 1.5rem 0;
        }
        
        /* Banner Sambutan Utama Ala Halodoc */
        .hd-welcome-banner {
            background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border-left: 6px solid #2e7d32;
            box-shadow: 0 4px 15px rgba(46,125,50,0.05);
        }
        .hd-welcome-title {
            color: #1b5e20;
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.8px;
            margin-bottom: 0.5rem;
        }
        
        /* Kartu Menu Utama Interaktif */
        .hd-menu-box {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 14px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
            transition: all 0.25s ease;
        }
        .hd-menu-box:hover {
            border-color: #2e7d32;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(46,125,50,0.08);
        }
        
        /* Kartu Panduan P3K & Informasi Penyakit */
        .hd-info-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4.5px solid #2e7d32;
            border-radius: 6px 14px 14px 6px;
            padding: 1.35rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 3px 8px rgba(0,0,0,0.01);
        }
        
        /* Badge Kategori */
        .hd-tag-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 0.5rem;
        }
        
        /* Penyesuaian Tombol Bawaan Streamlit */
        .stButton > button {
            border-radius: 24px !important;
            font-weight: 600 !important;
            text-transform: capitalize;
            padding: 0.45rem 1.25rem !important;
        }
        
        /* Desain Khusus Footer Medis */
        .hd-footer-wrapper {
            margin-top: 5rem;
            padding: 2rem 0;
            border-top: 1px solid #e0e0e0;
            font-size: 0.82rem;
            color: #616161;
            line-height: 1.6;
        }

        /* Mengatur kontainer chat agar dinamis dan tidak langsung kaku melar besar */
        [data-testid="stChatMessageContainer"] {
            padding: 1rem !important;
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.01);
        }
        .stChatMessage {
            padding: 0.5rem 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)


def handle_theme_invalidation(theme):
    """Injeksi Javascript murni ke window parent untuk menjamin perpindahan mode gelap/terang bekerja 100%."""
    components.html(
        f"""
        <script>
        const rootDoc = window.parent.document.documentElement;
        const bodyDoc = window.parent.document.body;
        rootDoc.setAttribute('data-hb-theme', '{theme}');
        bodyDoc.setAttribute('data-hb-theme', '{theme}');
        </script>
        """,
        height=0,
    )


def init_session_variables():
    """Inisialisasi state managemen aplikasi secara berkala dengan nama yang manusiawi."""
    if "bot" not in st.session_state:
        st.session_state.bot = HealthBuddyFSM()
        st.session_state.bot.step("")
        st.session_state.history = [
            {"role": "Apoteker HealthBuddy", "avatar": "🩺", "content": st.session_state.bot.get_response()}
        ]
        st.session_state.tip_index = 0
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "BERANDA"


def process_chat_cycle(user_message):
    """Memproses alur teks chat dengan memberi feedback interaktif yang responsif dan natural."""
    # Simpan riwayat input dari user dengan nama manusiawi
    st.session_state.history.append({"role": "Anda", "avatar": "👤", "content": user_message})
    
    msg_lower = user_message.lower()
    
    # Logika anamnesa/feedback kustom yang nyambung dan empati sebelum dilempar ke FSM utama
    if any(keyword in msg_lower for keyword in ["demam", "panas", "meriang"]):
        feedback = (
            "Baik, saya catat keluhan demamnya. Sudah berapa hari kondisi ini berlangsung? "
            "Lalu, apakah ada gejala penyerta lain seperti batuk, pilek, atau nyeri sendi?"
        )
    elif any(keyword in msg_lower for keyword in ["mual", "muntah", "maag", "perih", "lambung"]):
        feedback = (
            "Perut perih atau mual tentu sangat tidak nyaman. Apakah rasa perihnya muncul "
            "sebelum atau sesudah makan? Sudah sempat mengonsumsi obat antasida sebelumnya?"
        )
    elif any(keyword in msg_lower for keyword in ["pusing", "sakit kepala", "migrain"]):
        feedback = (
            "Untuk sakit kepalanya, apakah rasanya seperti berputar atau berdenyut di satu sisi saja? "
            "Apakah Anda juga merasa kurang tidur atau terlambat makan hari ini?"
        )
    else:
        # Jika bukan kata kunci di atas, jalankan respon dari FSM aslinya
        st.session_state.bot.step(user_message)
        feedback = st.session_state.bot.get_response()

    # Simpan respon dari asisten dengan nama profesi tepercaya
    st.session_state.history.append({"role": "Apoteker HealthBuddy", "avatar": "🩺", "content": feedback})
    st.session_state.tip_index = st.session_state.get("tip_index", 0) + 1
    st.rerun()


def render_halodoc_header():
    """Merender Batas Header Atas yang kokoh beserta tombol navigasi kapsul."""
    header_cols = st.columns([1.5, 3.5, 1.2])
    
    with header_cols[0]:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 6px; padding-top: 4px;">
                <span style="font-weight: 800; font-size: 1.5rem; letter-spacing: -0.8px; color: #2e7d32;">health<span style="color: #66bb6a;">buddy</span></span>
                <span style="background: #2e7d32; color: white; font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 10px; margin-left: 4px; text-transform: uppercase;">Apotek</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with header_cols[1]:
        menu_slots = st.columns(4)
        navigation_map = [
            ("🏠 Beranda", "BERANDA"),
            ("💬 Chat Apoteker", "CHAT"),
            ("🔍 Cari Obat & Gejala", "CARI_DATA"),
            ("⛑️ Panduan P3K", "PANDUAN_P3K")
        ]
        for idx, (menu_label, target_id) in enumerate(navigation_map):
            with menu_slots[idx]:
                is_selected = st.session_state.current_page == target_id
                if st.button(
                    menu_label, 
                    key=f"hdr_nav_{target_id}", 
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.current_page = target_id
                    st.rerun()
                    
    with header_cols[2]:
        active_theme = st.session_state.theme
        theme_btn_label = "🌙 Mode Gelap" if active_theme == "light" else "☀️ Mode Terang"
        if st.button(theme_btn_label, key="hdr_theme_trigger", use_container_width=True):
            st.session_state.theme = "dark" if active_theme == "light" else "light"
            st.rerun()
                
    # Batas Garis Header Kokoh
    st.markdown("<div class='hd-header-line'></div>", unsafe_allow_html=True)


def render_state_capsule(bot):
    """Menampilkan status operasional penelaahan keluhan medis."""
    current_fsm_state = bot.state
    if current_fsm_state == State.EMERGENCY:
        status_type, head_txt, sub_txt = "alert", "Kondisi Kritis Terdeteksi", "Sistem mengunci obrolan mandiri. Harap hubungi rumah sakit terdekat atau talian darurat medis sekarang!"
    elif current_fsm_state in (State.TRIAGE, State.CLARIFY):
        status_type, head_txt, sub_txt = "active", "Asisten Medis Menelaah Gejala", "Sistem sedang mengurai token kalimat keluhan Anda. Masukkan informasi tambahan jika diperlukan."
    elif current_fsm_state == State.ADVICE:
        status_type, head_txt, sub_txt = "active", "Rekomendasi Perawatan Selesai Dirangkum", "Silakan baca petunjuk anjuran konsumsi obat ringan dan perawatan fisik di bawah."
    else:
        status_type, head_txt, sub_txt = "idle", "Sistem Siap Melayani", "Ceritakan keluhan atau gejala gangguan fisik yang sedang dirasakan tubuh Anda secara natural."

    st.markdown(
        f"""
        <div class="hb-state hb-state-{status_type}" style="padding: 0.85rem 1.25rem; border-radius: 10px; margin-bottom: 1rem;">
            <div class="hb-state-dot"></div>
            <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: inherit;">{head_txt}</div>
                <div style="font-size: 0.8rem; opacity: 0.85; margin-top: 1px;">{sub_txt}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_halodoc_footer():
    """Merender komponen batas kaki (Footer) yang sangat lengkap dan profesional di bagian bawah."""
    st.markdown(
        """
        <div class="hd-footer-wrapper">
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 40px; padding-bottom: 1.5rem;">
                <div>
                    <h5 style="font-weight: 800; color: #2e7d32; margin: 0 0 0.5rem 0; font-size: 1.1rem;">health<span style="color: #66bb6a;">buddy</span></h5>
                    <p style="margin: 0; opacity: 0.8; font-size: 0.8rem;">
                        Platform informasi mandiri untuk edukasi kesehatan, klasifikasi gejala gangguan fisik ringan, 
                        serta referensi baku tindakan pertolongan pertama (P3K) berbasis pencocokan pola kalimat digital terpercaya.
                    </p>
                </div>
                <div>
                    <b style="color: #1b5e20; display: block; margin-bottom: 0.5rem;">Layanan Kami</b>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Chat Apoteker Aktif</span>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Direktori Penyakit Lengkap</span>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Prosedur Baku Cedera</span>
                </div>
                <div>
                    <b style="color: #1b5e20; display: block; margin-bottom: 0.5rem;">Patuhi Aturan Sehat</b>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Konsumsi Obat Rasional</span>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Kenali Indikasi Tubuh</span>
                    <span style="display:block; opacity:0.8; font-size:0.8rem; margin-bottom:3px;">• Hindari Dosis Berlebih</span>
                </div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.06); padding-top: 1rem; display: flex; justify-content: space-between; opacity: 0.7; font-size: 0.78rem;">
                <span>&copy; 2026 HealthBuddy — Aplikasi Sistem Pakar Kesehatan Terintegrasi. All Rights Reserved.</span>
                <span>Informatics Engineering &middot; Kelas Otomata Linier</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    # Inisialisasi Gaya & State Utama
    init_session_variables()
    load_premium_styles()
    handle_theme_invalidation(st.session_state.theme)

    # Memasang Batas Header Atas Berwujud Kapsul Navigasi
    render_halodoc_header()
    
    current_active_tab = st.session_state.current_page

    # =========================================================================
    # 1. HALAMAN BERANDA / LANDING PAGE
    # =========================================================================
    if current_active_tab == "BERANDA":
        # Banner Sambutan Hangat Utama
        st.markdown(
            """
            <div class="hd-welcome-banner">
                <span class="hd-tag-badge">Mitra Kesehatan Digital Keluarga</span>
                <h1 class="hd-welcome-title">Halo, Ada Yang Bisa Kami Bantu Hari Ini?</h1>
                <p style="margin: 0; font-size: 1rem; color: #33691e; opacity: 0.9; line-height: 1.6; max-width: 850px;">
                    Jelajahi informasi medis tepercaya kapan saja. Konsultasikan indikasi keluhan tubuh Anda dengan sistem kecerdasan pakar apoteker kami, 
                    atau cari tahu kandungan zat istilah klinis secara instan melalui bar pencarian interaktif.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<h4 style='font-weight:700; margin-bottom:1.25rem; color:#1b5e20;'>Kategori Layanan Kesehatan Cepat</h4>", unsafe_allow_html=True)
        
        # Grid Menu Utama 3 Kolom Sejajar Profesional
        menu_cols = st.columns(3, gap="large")
        
        with menu_cols[0]:
            st.markdown(
                """
                <div class="hd-menu-box">
                    <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">💬</div>
                    <h5 style="margin: 0 0 6px 0; font-weight: 700; color: #2e7d32;">Tanya Apoteker Mandiri</h5>
                    <p style="font-size: 0.82rem; opacity: 0.75; margin-bottom: 1.25rem; line-height: 1.4;">Konsultasikan keluhan demam, pusing, nyeri, atau flu secara langsung melalui pemrosesan pesan otomatis.</p>
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("Mulai Chat Konsultasi", key="home_to_chat_action", use_container_width=True, type="primary"):
                st.session_state.current_page = "CHAT"
                st.rerun()
                
        with menu_cols[1]:
            st.markdown(
                """
                <div class="hd-menu-box">
                    <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">🔍</div>
                    <h5 style="margin: 0 0 6px 0; font-weight: 700; color: #2e7d32;">Direktori Gejala &amp; Obat</h5>
                    <p style="font-size: 0.82rem; opacity: 0.75; margin-bottom: 1.25rem; line-height: 1.4;">Cari pengertian istilah farmasi klinis serta daftar penyakit terintegrasi secara real-time dan responsif.</p>
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("Buka Direktori Data", key="home_to_search_action", use_container_width=True):
                st.session_state.current_page = "CARI_DATA"
                st.rerun()
                
        with menu_cols[2]:
            st.markdown(
                """
                <div class="hd-menu-box">
                    <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">⛑️</div>
                    <h5 style="margin: 0 0 6px 0; font-weight: 700; color: #2e7d32;">Modul Kritis Darurat P3K</h5>
                    <p style="font-size: 0.82rem; opacity: 0.75; margin-bottom: 1.25rem; line-height: 1.4;">Pelajari penanganan pertama cedera fisik, luka bakar, serangan asma, hingga kontak ambulans penyelamat.</p>
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("Lihat Panduan P3K", key="home_to_p3k_action", use_container_width=True):
                st.session_state.current_page = "PANDUAN_P3K"
                st.rerun()

    # =========================================================================
    # 2. RUANG CHAT APOTEKER (TINGGI DINAMIS / TIDAK SEGEDE GABAN PAS KOSONG)
    # =========================================================================
    elif current_active_tab == "CHAT":
        main_chat_layout = st.columns([2.2, 1], gap="medium")
        
        with main_chat_layout[0]:
            render_state_capsule(st.session_state.bot)
            
            # Hitung tinggi container secara fleksibel mengikuti banyaknya jumlah riwayat pesan
            history_len = len(st.session_state.history)
            calculated_height = max(160, min(480, history_len * 95))
            
            # Area Tampilan Pesan Obrolan Bersih
            chat_box_scroller = st.container(height=calculated_height)
            with chat_box_scroller:
                for message in st.session_state.history:
                    with st.chat_message(name=message["role"], avatar=message.get("avatar", "🩺")):
                        st.markdown(f"**{message['role']}**")
                        st.markdown(message["content"])
                        
            # Kotak Teks Input Alami
            user_text_input = st.chat_input("Ceritakan keluhan Anda di sini (misal: 'Saya sakit demam')...")
            if user_text_input:
                process_chat_cycle(user_text_input)
                
            # Panel Kontrol Mikro di bawah kolom chat
            control_btn_cols = st.columns([1, 1, 3.2])
            with control_btn_cols[0]:
                if st.button("🔄 Segarkan Sesi", use_container_width=True, key="reset_chat_session"):
                    retained_theme = st.session_state.theme
                    st.session_state.clear()
                    init_session_variables()
                    st.session_state.theme = retained_theme
                    st.session_state.current_page = "CHAT"
                    st.rerun()
            with control_btn_cols[1]:
                if st.button("💡 Minta Bantuan", use_container_width=True, key="trigger_help_session"):
                    process_chat_cycle("bantuan")
                    
        with main_chat_layout[1]:
            # Rekomendasi Pertanyaan Sering Diajukan (FAQ Akses Instan)
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #2e7d32; text-transform: uppercase; margin-bottom: 0.6rem; letter-spacing: 0.3px;">Keluhan Populer</div>
                """,
                unsafe_allow_html=True
            )
            popular_queries = [
                ("🌡️ Mengalami Demam", "saya demam dan pusing"),
                (" Perut Mual / Gejala Maag", "perut saya perih, gejala maag"),
                ("🔬 Info Kolesterol", "apa itu kolesterol"),
                ("🩹 Evakuasi Luka Bakar", "pertolongan pertama luka bakar"),
            ]
            for button_lbl, embedded_prompt in popular_queries:
                if st.button(button_lbl, use_container_width=True, key=f"pop_query_{button_lbl}"):
                    process_chat_cycle(embedded_prompt)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Tips Hidup Sehat Alami
            all_wellness_tips = WELLNESS_TIPS
            current_tip_pos = st.session_state.get("tip_index", 0) % len(all_wellness_tips)
            st.markdown(
                f"""
                <div style="border-left: 3.5px solid #2e7d32; padding-left: 0.85rem; font-size: 0.82rem; line-height: 1.4; opacity: 0.85;">
                    <b>Rekomendasi Apoteker Hari Ini:</b><br><i>"{all_wellness_tips[current_tip_pos]}"</i>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================================================================
    # 3. CARI DATA / DIREKTORI GEJALA & OBAT (SEARCH-DRIVEN REALTIME)
    # =========================================================================
    elif current_active_tab == "CARI_DATA":
        st.markdown("<h4 style='font-weight:700; margin-bottom:1rem; color:#1b5e20;'>Direktori Medis Real-Time &amp; Khasiat Obat</h4>", unsafe_allow_html=True)
        
        tab_sub_modules = st.tabs(["🔍 Pencarian Responsif Penyakit", "📖 Istilah &amp; Glosarium Farmasi"])
        
        with tab_sub_modules[0]:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # INPUT BAR PENCARIAN UTAMA RESPONSIF
            live_search_box = st.text_input("🔍 Ketik nama keluhan, tanda fisik, atau kata kunci penyakit (cth: flu, lambung, demam):", "").lower()
            
            search_grid_cols = st.columns(2)
            matched_items_count = 0
            
            for disease_key, disease_info in DISEASES.items():
                if live_search_box in disease_info["nama"].lower() or live_search_box in disease_info["kategori"].lower():
                    with search_grid_cols[matched_items_count % 2]:
                        st.markdown(
                            f"""
                            <div class="hd-info-card">
                                <span class="hd-tag-badge">{disease_info['kategori'].upper()}</span>
                                <h5 style="margin: 0.25rem 0 0.4rem 0; font-weight: 700; color: #1b5e20;">{disease_info['nama']}</h5>
                                <p style="margin: 0; font-size: 0.88rem; opacity: 0.82; line-height: 1.55;">
                                    Data referensi kesehatan terstruktur. Untuk menelaah indikasi obat ringan serta mendapatkan rangkuman anjuran perawatan secara lengkap, silakan manfaatkan fitur <b>Chat Apoteker</b>.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    matched_items_count += 1
                    
            if matched_items_count == 0:
                st.caption("Kata kunci tidak ditemukan dalam repositori. Silakan gunakan istilah klinis lainnya.")
                
        with tab_sub_modules[1]:
            st.markdown("<br>", unsafe_allow_html=True)
            dropdown_selected_term = st.selectbox("Pilih nama zat atau istilah farmasi untuk membedah fungsi:", list(DEFINITIONS.keys()))
            if dropdown_selected_term:
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e0e0e0; border-left: 4.5px solid #2e7d32; padding: 1.5rem; border-radius: 0 12px 12px 0; margin-top: 0.5rem; box-shadow:0 3px 6px rgba(0,0,0,0.01);">
                        <h5 style="margin: 0 0 0.5rem 0; font-weight: 700; color: #2e7d32; font-size:1.1rem;">{dropdown_selected_term}</h5>
                        <p style="margin: 0; font-size: 0.95rem; line-height: 1.6; opacity: 0.88;">{DEFINITIONS[dropdown_selected_term]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # =========================================================================
    # 4. PANDUAN P3K
    # =========================================================================
    elif current_active_tab == "PANDUAN_P3K":
        st.markdown("<h4 style='font-weight:700; margin-bottom:1rem; color:#1b5e20;'>Prosedur Standar Pertolongan Pertama Gawat Darurat (P3K)</h4>", unsafe_allow_html=True)
        
        p3k_split_layout = st.columns([2, 1], gap="large")
        
        with p3k_split_layout[0]:
            for aid_title, aid_instruction in FIRST_AID.items():
                st.markdown(
                    f"""
                    <div class="hd-info-card">
                        <h5 style="margin: 0 0 0.5rem 0; font-weight: 700; color: #2e7d32;">🩹 Penanganan Utama: {aid_title.title()}</h5>
                        <p style="margin: 0; font-size: 0.92rem; line-height: 1.6; opacity: 0.9;">{aid_instruction}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with p3k_split_layout[1]:
            st.markdown(
                """
                <div style="background-color: #ffebee; border: 1px solid #ffcdd2; padding: 1.25rem; border-radius: 12px; box-shadow:0 3px 8px rgba(198,40,40,0.03);">
                    <h5 style="margin: 0 0 0.75rem 0; color: #c62828; font-weight: 700;">🚨 Kontak Penyelamatan Darurat</h5>
                """,
                unsafe_allow_html=True
            )
            for emergency_agency, phone_number in EMERGENCY_NUMBERS.items():
                st.markdown(f"<div style='font-size: 0.85rem; margin-bottom: 6px;'><b>{emergency_agency.replace('_', ' ').title()}</b>: <code style='color: #c62828; font-weight:700;'>{phone_number}</code></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Memasang Komponen Batas Bawah / Kaki (Footer Lengkap)
    render_halodoc_footer()


if __name__ == "__main__":
    main()