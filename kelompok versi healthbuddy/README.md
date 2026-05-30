# HealthBuddy

> Asisten edukasi kesehatan berbasis Finite State Machine. Disusun untuk Tugas Akhir mata kuliah Teori Bahasa & Otomata.

HealthBuddy adalah chatbot kesehatan yang tidak berusaha menjadi pengganti dokter. Tugasnya sederhana: mendengarkan keluhan ringan, mengenali gejala yang disampaikan pengguna, lalu menyajikan saran perawatan mandiri yang sumbernya dapat ditelusuri. Seluruh proses berjalan di atas Finite State Machine klasik tanpa memanggil API model bahasa eksternal.

## Latar Belakang

Tugas mata kuliah ini mensyaratkan pembuatan chatbot tanpa pemanfaatan API kecerdasan buatan eksternal seperti ChatGPT atau layanan serupa. Atas dasar tersebut, seluruh logika percakapan disusun dari aturan yang ditulis secara manual: indeks kata kunci, mesin state, dan pencocokan teks berbasis pola. Domain yang dipilih adalah kesehatan dengan pertimbangan dampak edukatif, karena cukup banyak situasi sehari-hari yang sebenarnya hanya membutuhkan informasi awal sebelum memutuskan langkah berikutnya.

Aplikasi ini bukan alat diagnosis. Saran yang diberikan dibatasi pada tindakan rumahan yang aman dilakukan tanpa pengawasan medis, seperti kompres, hidrasi, istirahat, dan pengaturan pola makan. Tidak ada rekomendasi obat, dosis, maupun diagnosis klinis.

## Teknologi

- **Python 3.11**
- **Streamlit** untuk antarmuka pengguna
- **Sastrawi** untuk *stemming* Bahasa Indonesia agar variasi imbuhan seperti "menyakitkan", "disakiti", dan "sakit-sakit" dikenali sebagai satu akar kata
- **RapidFuzz** untuk toleransi kesalahan ketik, sehingga kata seperti "batok" tetap dikenali sebagai "batuk"

Tidak ada model *machine learning* yang dimuat dan tidak ada panggilan keluar ke API mana pun selama aplikasi berjalan.

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser akan otomatis terbuka pada alamat `http://localhost:8501`. Apabila tidak, alamat tersebut dapat diakses secara manual dari tautan yang muncul di terminal.

Untuk menguji FSM tanpa antarmuka:

```bash
python smoke_test.py
```

Skrip ini menyimulasikan delapan skenario percakapan: salam pembuka, *triage* multi-turn, pencarian definisi, panduan pertolongan pertama, deteksi gejala kritis, toleransi kesalahan ketik, alur reset, dan pencarian FAQ. Skrip dapat dijadikan referensi pada saat menjelaskan transisi antar-state kepada dosen pembimbing.

## Cakupan Pertanyaan

- Konsultasi gejala, sebagai contoh: *"saya batuk berdahak dan demam ringan sudah dua hari"*
- Pencarian definisi istilah medis, sebagai contoh: *"apa itu kolesterol"*
- Panduan pertolongan pertama, sebagai contoh: *"cara mengatasi mimisan"*
- Tips gaya hidup sehat, sebagai contoh: *"berapa lama tidur ideal"*
- Nomor darurat kesehatan, sebagai contoh: *"nomor ambulans"*

Sistem akan otomatis berpindah ke mode darurat apabila pengguna menyebutkan gejala kritis seperti nyeri dada, kejang, atau stroke. Pada mode tersebut, sistem akan terkunci sampai pengguna mengetik perintah "mulai ulang". Mekanisme ini disengaja untuk mencegah pemberian saran perawatan mandiri pada kondisi yang seharusnya langsung dirujuk ke instalasi gawat darurat.

## Struktur Proyek

```
kelompok versi healthbuddy/
├── app.py              Halaman Streamlit utama
├── requirements.txt
├── smoke_test.py       Pengujian percakapan tanpa antarmuka
├── assets/
│   └── styles.css      Custom CSS bertema editorial magazine
├── core/
│   ├── fsm.py          Finite State Machine dan dialog manager
│   └── nlp.py          Stemming, scoring gejala, deteksi intent
└── data/
    ├── diseases.py     30 kondisi medis dengan saran lengkap
    ├── red_flags.py    20 gejala kritis
    ├── first_aid.py    10 panduan pertolongan pertama
    ├── definitions.py  70+ istilah medis
    └── faq.py          18 pertanyaan umum dan tips wellness
```

## Diagram FSM

```
IDLE -> GREETING -> MAIN_MENU
                       |
       +---------------+---------------+
       |               |               |
    TRIAGE       DEFINITION /     EMERGENCY_INFO
       |         FIRST_AID /
       |         FAQ
    ADVICE  <-->  CLARIFY

Dari state apa pun:
  - Deteksi gejala kritis -> EMERGENCY (terkunci)
  - Intent reset           -> IDLE
```

Setiap perpindahan state direkam pada `bot.transition_log` dan ditampilkan secara real-time di panel samping antarmuka. Hal ini memudahkan demonstrasi langsung kepada penguji, karena perubahan state dapat diamati seiring pengguna mengetik input.

## Cara Kerja NLP

Alur pemrosesan setiap masukan pengguna sebagai berikut:

1. Input mentah dibersihkan, diubah menjadi huruf kecil, dan tanda baca dihilangkan.
2. Setiap kata di-*stem* menggunakan Sastrawi. Misalnya, "menyakitkan" menjadi "sakit", dan "kedinginan" menjadi "dingin".
3. Hasil stemming dicocokkan dengan indeks kata kunci yang telah dibangun sebelumnya dari `data/diseases.py`. Apabila terdapat kecocokan tepat, skor langsung diberikan. Jika tidak, RapidFuzz mencoba *partial ratio match* dengan ambang batas 88 persen.
4. Skor diakumulasi antar-turn percakapan. Sebagai ilustrasi, apabila pengguna menyebut "perut perih" pada turn pertama dan "kembung" pada turn berikutnya, sistem menggabungkan keduanya menjadi skor Maag yang lebih tinggi.
5. Ketika skor melampaui ambang batas (`CONFIDENCE_THRESHOLD = 4.0`), sistem berpindah ke state ADVICE dan menyajikan saran perawatan.

Tidak ada proses pelatihan, *vector embedding*, maupun pemanggilan model pada arsitektur ini. Seluruh kecerdasan sistem bersumber dari indeks string yang dibangun pada saat aplikasi pertama kali dimuat.

## Sumber Knowledge Base

Knowledge base disusun secara manual dari sumber publik yang diperbolehkan untuk penggunaan edukasi:

- Kementerian Kesehatan Republik Indonesia: Pedoman Pengendalian Penyakit dan Pedoman Gizi Seimbang
- World Health Organization: Fact Sheets (public domain)
- Standar Pertolongan Pertama Pada Kecelakaan, Palang Merah Indonesia
- Pedoman Imunisasi Kementerian Kesehatan

Apabila terdapat kebutuhan untuk menambah penyakit baru, format entri sudah konsisten dan didokumentasikan pada `data/diseases.py`. Pengguna dapat menyalin satu entri yang sudah ada, mengubah isinya, lalu memuat ulang aplikasi. NLP engine akan otomatis melakukan *re-indexing*.

## Catatan Penting

Aplikasi ini merupakan alat edukasi, bukan pengganti tenaga medis profesional. Untuk diagnosis dan pengobatan, konsultasi tetap harus dilakukan dengan dokter atau fasilitas kesehatan resmi. Pada situasi yang mengancam jiwa, hubungi nomor darurat **119**.

Saran perawatan yang diberikan dirancang secara konservatif dan hanya mencakup tindakan rumahan yang aman dilakukan tanpa pengawasan medis. Setiap keluhan yang berpotensi serius akan diarahkan untuk segera mendapatkan penanganan di fasilitas kesehatan.

## Anggota Kelompok

Daftar kontributor dapat dilihat pada tab GitHub repository ini. Pembagian peran utama meliputi:

- *Knowledge engineering* dan desain FSM
- Pengembangan NLP engine dan modul stemming
- Pengembangan UI/UX Streamlit
- Penyusunan dokumentasi dan pengujian

## Lisensi

Repositori ini disusun untuk keperluan akademik dan dapat digunakan secara bebas untuk tugas atau pembelajaran lebih lanjut.
