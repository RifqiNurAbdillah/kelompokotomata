from pathlib import Path


BASE = [
    ("nyeri kaki", "muskuloskeletal", "Nyeri Kaki", "Rasa sakit pada tungkai, betis, lutut, tumit, atau telapak kaki akibat cedera ringan, kelelahan, saraf, sendi, atau aliran darah.", ["kaki sakit", "nyeri kaki", "betis sakit", "telapak kaki sakit", "tumit sakit"], ["bengkak kaki", "kaki pegal", "sulit berjalan", "kram betis"]),
    ("nyeri tangan", "muskuloskeletal", "Nyeri Tangan dan Pergelangan", "Nyeri pada tangan, jari, atau pergelangan akibat penggunaan berulang, cedera, saraf terjepit, atau radang sendi.", ["tangan sakit", "nyeri tangan", "pergelangan sakit", "jari sakit"], ["kesemutan tangan", "tangan kaku", "sulit menggenggam", "bengkak jari"]),
    ("nyeri leher", "muskuloskeletal", "Nyeri Leher", "Nyeri atau kaku pada leher akibat postur buruk, tegang otot, cedera, atau masalah saraf.", ["leher sakit", "nyeri leher", "leher kaku", "tengkuk sakit"], ["sakit kepala", "bahu tegang", "sulit menoleh", "kesemutan lengan"]),
    ("kesemutan", "neurologis", "Kesemutan / Parestesia", "Sensasi kebas, baal, atau seperti ditusuk jarum akibat tekanan saraf, aliran darah, diabetes, vitamin, atau gangguan saraf.", ["kesemutan", "kebas", "baal", "mati rasa", "seperti ditusuk jarum"], ["lemah otot", "tangan dingin", "kaki kebas", "sering kambuh"]),
    ("penyakit jantung koroner", "kardiovaskular", "Penyakit Jantung Koroner", "Gangguan aliran darah ke otot jantung akibat penyempitan pembuluh koroner.", ["nyeri dada saat aktivitas", "dada tertekan", "jantung koroner", "angina"], ["sesak", "keringat dingin", "nyeri menjalar ke lengan", "mudah lelah"]),
    ("rokok", "gaya_hidup", "Dampak Rokok", "Paparan zat kimia rokok meningkatkan risiko kanker, jantung, stroke, PPOK, gangguan kesuburan, dan penyakit pembuluh darah.", ["merokok", "rokok", "perokok", "asap rokok", "vape"], ["batuk kronis", "sesak", "mudah lelah", "dada tidak nyaman"]),
    ("cacingan", "infeksi_parasit", "Cacingan", "Infeksi parasit cacing di saluran cerna yang dapat menyebabkan gangguan gizi, anemia, dan keluhan perut.", ["cacingan", "cacing di feses", "perut buncit", "anus gatal"], ["berat badan turun", "lemas", "mual", "diare ringan", "nafsu makan berubah"]),
    ("infeksi parasit", "infeksi_parasit", "Infeksi Parasit Umum", "Infeksi oleh organisme parasit seperti protozoa atau cacing yang dapat menyerang pencernaan, darah, kulit, atau organ lain.", ["parasit", "infeksi parasit", "gatal setelah air kotor", "diare lama"], ["berat badan turun", "demam hilang timbul", "lemas", "nyeri perut"]),
    ("ebola", "infeksi_virus", "Ebola", "Penyakit virus berat dengan demam, kelemahan, nyeri otot, muntah atau diare, dan risiko perdarahan; terutama terkait wilayah wabah tertentu.", ["ebola", "demam ebola", "perdarahan ebola"], ["demam tinggi", "lemas berat", "muntah", "diare", "perdarahan"]),
    ("flu burung", "infeksi_virus", "Flu Burung / Avian Influenza", "Infeksi virus influenza dari unggas yang dapat menyebabkan gangguan pernapasan berat pada manusia.", ["flu burung", "kontak unggas sakit", "ayam mati mendadak", "avian influenza"], ["demam tinggi", "batuk", "sesak", "nyeri otot", "sakit tenggorokan"]),
    ("covid panjang", "pernapasan", "Long COVID", "Keluhan yang menetap atau muncul setelah infeksi COVID-19, seperti lelah, sesak, brain fog, dan nyeri tubuh.", ["long covid", "covid panjang", "lelah setelah covid", "sesak setelah covid"], ["brain fog", "mudah capek", "jantung berdebar", "batuk lama"]),
    ("jerawat batu", "kulit", "Jerawat Batu / Acne Nodulokistik", "Jerawat dalam, nyeri, meradang, dan berisiko meninggalkan bekas jaringan parut.", ["jerawat batu", "jerawat besar", "jerawat nyeri", "jerawat meradang"], ["kulit berminyak", "benjolan merah", "bekas jerawat", "komedo"]),
    ("ppok", "pernapasan", "PPOK / Penyakit Paru Obstruktif Kronis", "Penyakit paru kronis yang sering terkait rokok, ditandai batuk lama, dahak, dan sesak progresif.", ["ppok", "batuk kronis", "sesak kronis", "dahak menahun"], ["mengi", "mudah lelah", "dada berat", "sering infeksi paru"]),
    ("hipoglikemia", "metabolik", "Hipoglikemia / Gula Darah Rendah", "Kadar gula darah terlalu rendah yang dapat menyebabkan gemetar, keringat dingin, lapar, bingung, hingga pingsan.", ["gula darah rendah", "hipoglikemia", "keringat dingin lapar", "gemetar lapar"], ["lemas", "bingung", "jantung berdebar", "pusing", "pingsan"]),
    ("dehidrasi berat", "umum", "Dehidrasi Berat", "Kekurangan cairan berat akibat diare, muntah, panas, atau kurang minum yang dapat mengganggu organ.", ["dehidrasi berat", "tidak kencing", "mulut sangat kering", "mata cekung"], ["lemas berat", "pusing berdiri", "haus berat", "urin gelap"]),
]

BODY_PARTS = ["bahu", "punggung", "pinggang", "lutut", "tumit", "telapak kaki", "pergelangan kaki", "pergelangan tangan", "siku", "jari", "rahang", "dada", "perut bawah", "paha", "betis", "lengan", "telapak tangan", "tulang kering", "pangkal paha", "bokong"]
VIRUSES = ["campak", "rubella", "gondongan", "hepatitis a", "hepatitis b", "hepatitis c", "herpes", "cacar air", "chikungunya", "zika", "rabies", "polio"]
SKIN = ["eksim", "kurap", "panu", "kudis", "bisul", "impetigo", "luka bernanah", "kulit kering", "dermatitis kontak", "sunburn"]
LIFESTYLE = ["kurang olahraga", "kurang tidur", "terlalu banyak gula", "kebanyakan garam", "kurang minum", "duduk terlalu lama", "stres kerja", "begadang", "makan tidak teratur", "obesitas"]
COMMON_TOPICS = [
    "mata kering", "mata lelah", "hidung berdarah", "sinusitis", "bau mulut", "bibir pecah", "lidah putih", "telinga gatal", "telinga nyeri", "leher tegang",
    "bahu kaku", "punggung bawah sakit", "saraf kejepit", "sciatica", "carpal tunnel", "varises", "kaki bengkak", "telapak kaki panas", "asam lambung naik", "gerd",
    "muntah", "mual terus", "susah bab", "bab berdarah", "perut melilit", "keracunan makanan", "intoleransi laktosa", "alergi makanan", "biduran dingin", "kaligata",
    "rambut rontok", "ketombe", "kutu rambut", "jamur kuku", "cantengan", "luka diabetes", "luka sulit sembuh", "memar", "lebam", "mimisan sering",
    "jantung berdebar", "denyut tidak teratur", "tekanan darah rendah", "kolesterol tinggi", "trigliserida tinggi", "gula darah tinggi", "prediabetes", "obesitas sentral", "asam urat tinggi", "batu ginjal",
    "infeksi saluran kemih", "anyang anyangan", "nyeri pinggang ginjal", "keputihan", "nyeri haid berat", "haid tidak teratur", "pms", "menopause", "anemia remaja", "kurang zat besi",
    "vitamin d rendah", "kurang vitamin b12", "kurang kalsium", "dehidrasi ringan", "heat exhaustion", "hipotermia", "gigitan nyamuk", "gigitan hewan", "rabies risiko", "tetanus risiko",
    "demam tifoid", "malaria", "leptospirosis", "dengue warning sign", "tbc paru", "pneumonia ringan", "bronkitis", "sinus mampet", "radang telinga", "radang amandel",
    "cemas", "panic attack", "burnout", "kelelahan kronis", "kurang fokus", "brain fog", "overthinking", "nyeri dada cemas", "sesak karena panik", "gangguan tidur",
]

SUGGESTIONS = ["Istirahat cukup dan kurangi aktivitas yang memperberat keluhan.", "Cukupi cairan dan makan bergizi seimbang.", "Pantau durasi, intensitas, dan pemicu keluhan.", "Periksa ke fasilitas kesehatan bila memburuk atau tidak membaik."]

conditions = {}
for key, cat, name, definition, utama, pendukung in BASE:
    conditions[key] = (cat, name, definition, utama, pendukung, SUGGESTIONS)

for part in BODY_PARTS:
    conditions[f"nyeri {part}"] = ("muskuloskeletal", f"Nyeri {part.title()}", f"Nyeri pada area {part} yang dapat terkait cedera, postur, tegang otot, saraf, atau sendi.", [f"{part} sakit", f"nyeri {part}", f"{part} pegal"], [f"{part} kaku", f"{part} bengkak", "sulit bergerak"], SUGGESTIONS)

for virus in VIRUSES:
    conditions[virus] = ("infeksi_virus", virus.title(), f"Infeksi virus {virus} dapat menimbulkan keluhan sistemik seperti demam, lemas, nyeri tubuh, atau gejala khas sesuai organ yang terkena.", [virus, f"gejala {virus}", f"terkena {virus}"], ["demam", "lemas", "nyeri tubuh", "tidak enak badan"], SUGGESTIONS)

for skin in SKIN:
    conditions[skin] = ("kulit", skin.title(), f"Keluhan {skin} merupakan masalah kulit yang dapat dipicu infeksi, iritasi, alergi, kebersihan, atau kondisi kulit tertentu.", [skin, f"kulit {skin}", f"gejala {skin}"], ["gatal", "kemerahan", "perih", "ruam"], SUGGESTIONS)

for item in LIFESTYLE:
    conditions[item] = ("gaya_hidup", item.title(), f"Kebiasaan {item} dapat memengaruhi kesehatan secara bertahap dan meningkatkan risiko keluhan fisik maupun metabolik.", [item, f"akibat {item}", f"dampak {item}"], ["mudah lelah", "kurang fokus", "berat badan berubah", "keluhan berulang"], SUGGESTIONS)

for topic in COMMON_TOPICS:
    cat = "umum"
    if any(x in topic for x in ["mata", "hidung", "telinga", "amandel", "sinus"]):
        cat = "tht_mata"
    elif any(x in topic for x in ["kulit", "rambut", "kuku", "jamur", "biduran", "luka", "memar", "lebam"]):
        cat = "kulit"
    elif any(x in topic for x in ["jantung", "darah", "kolesterol", "trigliserida"]):
        cat = "kardiovaskular"
    elif any(x in topic for x in ["gula", "diabetes", "obesitas", "asam urat", "vitamin", "kalsium"]):
        cat = "metabolik"
    elif any(x in topic for x in ["bab", "perut", "mual", "muntah", "lambung", "gerd", "makanan"]):
        cat = "pencernaan"
    elif any(x in topic for x in ["cemas", "panic", "burnout", "overthinking", "tidur", "brain fog"]):
        cat = "mental"
    elif any(x in topic for x in ["malaria", "tbc", "pneumonia", "bronkitis", "dengue", "tifoid", "leptospirosis"]):
        cat = "infeksi_umum"
    conditions[topic] = (cat, topic.title(), f"Topik {topic} mencakup keluhan yang perlu dipahami dari durasi, tingkat keparahan, pemicu, serta tanda bahaya yang menyertai.", [topic, f"gejala {topic}", f"keluhan {topic}"], ["tidak nyaman", "mengganggu aktivitas", "keluhan berulang"], SUGGESTIONS)

def pylist(items):
    return "[" + ", ".join(repr(x) for x in items) + "]"

lines = ['"""Additional broad medical knowledge for HealthBuddy."""', '', 'MEDICAL_EXPANSION_DISEASES = {']
for key, (cat, nama, definition, utama, pendukung, saran) in sorted(conditions.items()):
    lines.extend([
        f"    {key!r}: {{",
        f"        'kategori': {cat!r},",
        f"        'nama': {nama!r},",
        f"        'definisi': {definition!r},",
        f"        'gejala_utama': {pylist(utama)},",
        f"        'gejala_pendukung': {pylist(pendukung)},",
        f"        'saran': {pylist(saran)},",
        "        'kapan_ke_dokter': 'Segera periksa bila gejala berat, berlangsung lama, memburuk, atau disertai tanda bahaya.',",
        "        'pencegahan': 'Jaga pola hidup sehat, kebersihan, nutrisi, aktivitas fisik, dan lakukan pemeriksaan bila berisiko.',",
        "    },",
    ])
lines.extend(['}', '', 'MEDICAL_EXPANSION_CATEGORIES = {', "    'infeksi_parasit': 'Infeksi Parasit',", "    'infeksi_virus': 'Infeksi Virus',", "    'gaya_hidup': 'Gaya Hidup & Risiko',", "    'umum': 'Kondisi Umum',", "    'tht_mata': 'THT & Mata',", '}'])
Path('data/medical_expansion.py').write_text('\n'.join(lines), encoding='utf-8')
print('generated', len(conditions), 'conditions', len(lines), 'lines')
