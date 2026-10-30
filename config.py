"""Projenin ortak ayarları: yollar, sınıf isimleri, renkler."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATASET_DIR = DATA_DIR / "dental_xray"          # zip buraya açılır
DATA_YAML = DATA_DIR / "dental.yaml"            # train / val / test
EXTERNAL_YAML = DATA_DIR / "dental_external.yaml"  # başka kliniklerden gelen dış doğrulama seti
WEIGHTS_DIR = ROOT / "weights"
BEST_WEIGHTS = WEIGHTS_DIR / "best.pt"          # 14 sınıflı ana model
METRICS_FILE = WEIGHTS_DIR / "metrics.json"     # test sonuçları (uygulamada gösterilir)

# Çürük ve periapikal lezyon için ayrı, daha iyi model: önce 5.059 dış kaynaklı röntgenle
# ön eğitildi, sonra kendi verimizle ince ayar yapıldı. Dış doğrulamada çürük mAP50'si
# 0,320'den 0,395'e çıktı. Yoksa bu sınıflar da ana modelden okunur.
CURUK_WEIGHTS = WEIGHTS_DIR / "curuk2.pt"
CURUK_METRICS = WEIGHTS_DIR / "curuk2_metrics.json"
CURUK_CODES = ["CAR", "API"]                    # bu bulgular çürük modelinden alınır
EXAMPLES_DIR = ROOT / "ornekler"
# Colab'da Google Drive'a yönlendirilir; bağlantı koparsa eğitim kaldığı yerden devam eder
RUNS_DIR = Path(os.environ.get("DENTAL_RUNS_DIR", ROOT / "runs"))

# Veri seti: "Dataset for Automating Dental Condition Detection on Panoramic Radiographs"
# Mureșanu, Hedeșiu, Iacob (2025) - Zenodo, CC-BY-4.0 - https://doi.org/10.5281/zenodo.15487430
DATASET_URL = (
    "https://zenodo.org/api/records/15487430/files/"
    "panoramic_radiography_yolo_dataset_14_classes.zip/content"
)
DATASET_ZIP = DATA_DIR / "panoramic_radiography_yolo_dataset_14_classes.zip"
DATASET_MD5 = "18d5acaea021f4f3b05b76e9a27fbd42"
DATASET_SIZE = 1_397_393_531

# YOLO etiketlerindeki sınıf sırası (satırdaki ilk sayı = bu listedeki indeks)
CLASS_CODES = ["IMP", "PRR", "OBT", "END", "CAR", "BON", "IMT",
               "API", "ROT", "FUR", "APS", "ROR", "ORD", "SRD"]

TR_NAMES = {
    "IMP": "İmplant",
    "PRR": "Kron / Köprü",
    "OBT": "Dolgu",
    "END": "Kanal Tedavisi",
    "CAR": "Çürük",
    "BON": "Kemik Kaybı",
    "IMT": "Gömülü Diş",
    "API": "Periapikal Lezyon",
    "ROT": "Kök Artığı",
    "FUR": "Furkasyon Lezyonu",
    "APS": "Apikal Rezeksiyon",
    "ROR": "Kök Rezorpsiyonu",
    "ORD": "Ortodontik Aparey",
    "SRD": "Cerrahi Materyal",
}

# Varsayılan olarak ekranda gösterilen bulgular
TARGET_CODES = ["CAR", "END"]

# Çizim renkleri (RGB). Gri röntgen üzerinde kolay seçilsin diye doygun renkler.
COLORS = {
    "CAR": (255, 59, 48),     # kırmızı
    "END": (0, 190, 255),     # mavi
    "API": (255, 204, 0),     # sarı
    "OBT": (52, 199, 89),     # yeşil
    "PRR": (175, 82, 222),    # mor
    "IMP": (255, 149, 0),     # turuncu
    "IMT": (255, 45, 145),    # pembe
    "BON": (90, 200, 250),
    "ROT": (255, 214, 10),
    "FUR": (191, 90, 242),
    "APS": (100, 210, 255),
    "ROR": (255, 105, 97),
    "ORD": (48, 209, 88),
    "SRD": (152, 152, 157),
}

# Eğitim varsayılanları (6 GB ekran kartı için ayarlandı)
DEFAULT_MODEL = "yolo26s.pt"
IMGSZ = 1024

# Aynı veri setiyle yayımlanan makalenin (YOLOv8, Diagnostics 2024, doi:10.3390/diagnostics14202336)
# iç test setindeki sonuçları - kendi modelimizi kıyaslamak için
PAPER_BASELINE = {
    "test": {"CAR": {"precision": 0.626, "recall": 0.511},
             "END": {"precision": 0.879, "recall": 0.899}},
    "external": {"CAR": {"precision": 0.466, "recall": 0.439},
                 "END": {"precision": 0.734, "recall": 0.777}},
}


def tr_name(code: str) -> str:
    return TR_NAMES.get(code, code)
