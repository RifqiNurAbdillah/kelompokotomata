"""Daftar gejala bahaya (red flags) yang wajib dirujuk ke fasilitas medis darurat."""

RED_FLAGS = {
    "nyeri dada": {
        "kategori": "Jantung",
        "alasan": "Nyeri dada hebat dapat menandakan serangan jantung atau emboli paru.",
        "tindakan": "Segera ke IGD. Posisi setengah duduk, longgarkan pakaian, hindari aktivitas.",
    },
    "sesak napas berat": {
        "kategori": "Pernapasan",
        "alasan": "Sesak napas berat dapat mengindikasikan gagal napas, serangan asma berat, atau emboli.",
        "tindakan": "Posisi duduk tegak, hubungi 119, gunakan inhaler jika tersedia.",
    },
    "kejang": {
        "kategori": "Neurologis",
        "alasan": "Kejang dapat menandakan epilepsi, infeksi otak, atau gangguan elektrolit serius.",
        "tindakan": "Miringkan tubuh, jauhkan dari benda keras, jangan masukkan apapun ke mulut. Hubungi 119.",
    },
    "muntah darah": {
        "kategori": "Pencernaan",
        "alasan": "Muntah darah menandakan pendarahan saluran cerna atas yang berbahaya.",
        "tindakan": "Segera ke IGD. Posisi miring, jangan berikan makanan atau minuman.",
    },
    "BAB berdarah hitam": {
        "kategori": "Pencernaan",
        "alasan": "Tinja hitam (melena) menunjukkan pendarahan saluran cerna atas.",
        "tindakan": "Segera ke IGD untuk evaluasi pendarahan internal.",
    },
    "stroke": {
        "kategori": "Neurologis",
        "alasan": "Stroke adalah kerusakan otak akibat gangguan aliran darah yang butuh penanganan cepat.",
        "tindakan": "FAST: Face droop, Arm weak, Speech slurred, Time to call 119. Jangan beri makan/minum.",
    },
    "pelo": {
        "kategori": "Neurologis",
        "alasan": "Bicara pelo mendadak adalah tanda stroke akut.",
        "tindakan": "Segera hubungi 119, catat waktu mulai gejala, jangan tunda.",
    },
    "wajah perot": {
        "kategori": "Neurologis",
        "alasan": "Wajah tidak simetris mendadak adalah tanda klasik stroke.",
        "tindakan": "Segera ke IGD, golden period stroke hanya 4.5 jam.",
    },
    "lemas separuh tubuh": {
        "kategori": "Neurologis",
        "alasan": "Kelemahan satu sisi tubuh tiba-tiba menandakan stroke.",
        "tindakan": "Segera hubungi 119, jangan berikan apapun lewat mulut.",
    },
    "pingsan": {
        "kategori": "Umum",
        "alasan": "Pingsan dapat akibat aritmia jantung, hipoglikemia, atau perdarahan.",
        "tindakan": "- Baringkan korban telentang di tempat datar dan aman.\n- Angkat kedua kaki sekitar 30 cm untuk mengalirkan darah ke otak.\n- Longgarkan pakaian di leher, dada, dan pinggang.\n- Pastikan jalan napas terbuka, periksa pernapasan.\n- Jangan berikan makanan atau minuman saat belum sadar penuh.\n- Saat sadar, bantu duduk perlahan, beri minum manis hangat."
    },
    "tidak sadar": {
        "kategori": "Umum",
        "alasan": "Penurunan kesadaran adalah kondisi gawat darurat dengan banyak penyebab kritis.",
        "tindakan": "Cek napas dan nadi, posisi pemulihan, hubungi 119 segera.",
    },
    "perut kanan bawah hebat": {
        "kategori": "Bedah",
        "alasan": "Nyeri kanan bawah hebat dapat menandakan radang usus buntu yang butuh operasi.",
        "tindakan": "Segera ke IGD. Jangan beri makan/minum, jangan kompres hangat.",
    },
    "bibir membiru": {
        "kategori": "Pernapasan",
        "alasan": "Sianosis menandakan kekurangan oksigen berat.",
        "tindakan": "Segera ke IGD, posisi duduk, beri ventilasi udara segar.",
    },
    "demam tinggi anak": {
        "kategori": "Pediatri",
        "alasan": "Demam di atas 40 derajat pada anak berisiko menyebabkan kejang demam.",
        "tindakan": "Kompres hangat, longgarkan pakaian, segera ke IGD jika kejang.",
    },
    "sakit kepala hebat mendadak": {
        "kategori": "Neurologis",
        "alasan": "Sakit kepala hebat mendadak (thunderclap) dapat menandakan pendarahan otak.",
        "tindakan": "Segera ke IGD, jangan tunggu, jangan beri obat sembarangan.",
    },
    "anafilaksis": {
        "kategori": "Alergi",
        "alasan": "Reaksi alergi berat dengan sesak, bengkak wajah, dan tekanan darah turun.",
        "tindakan": "Hubungi 119 segera, posisi telentang dengan kaki terangkat.",
    },
    "luka bakar luas": {
        "kategori": "Trauma",
        "alasan": "Luka bakar lebih dari 10 persen tubuh berisiko syok dan infeksi serius.",
        "tindakan": "Aliri air mengalir 20 menit, tutup kasa bersih, segera ke IGD.",
    },
    "patah tulang terbuka": {
        "kategori": "Trauma",
        "alasan": "Patah tulang dengan luka terbuka berisiko infeksi dan pendarahan.",
        "tindakan": "Imobilisasi, tutup luka, jangan dorong tulang masuk, segera ke IGD.",
    },
    "perdarahan tidak berhenti": {
        "kategori": "Trauma",
        "alasan": "Pendarahan deras yang tidak berhenti mengancam nyawa.",
        "tindakan": "Tekan langsung dengan kain bersih, angkat bagian tubuh yang terluka, hubungi 119.",
    },
    "muncul ruam ungu": {
        "kategori": "Infeksi",
        "alasan": "Ruam ungu yang tidak hilang saat ditekan dapat menandakan meningitis.",
        "tindakan": "Segera ke IGD, terutama jika disertai demam dan kaku leher.",
    },
}

EMERGENCY_NUMBERS = {
    "Ambulans": "119",
    "Polisi": "110",
    "Damkar": "113",
    "BPJS Kesehatan": "165",
    "Kementerian Kesehatan": "1500-567",
    "SAPA 129 (kekerasan)": "129",
}
