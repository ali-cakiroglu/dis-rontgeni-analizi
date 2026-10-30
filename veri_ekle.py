"""Dışarıdan bulduğun etiketli röntgenleri mevcut eğitim setine ekler.

Beklenen klasör yapısı (YOLO formatı):
    klasor/images/*.jpg   +   klasor/labels/*.txt        (ya da resim ve txt'ler yan yana)

Etiket satırı: <sınıf no> <merkez x> <merkez y> <genişlik> <yükseklik>   (hepsi 0-1 arası)

Kullanım:
    python veri_ekle.py C:\\indirilen\\dataset --map 0=CAR,1=END --dene
    python veri_ekle.py C:\\indirilen\\dataset --map 0=CAR,1=END
    python veri_ekle.py C:\\kendi_rontgenlerim --map 0=CAR --split val

--map: onlardaki sınıf numarası = bizim sınıf kodumuz. Haritada olmayan sınıflar atılır.
Bizim kodlar: IMP PRR OBT END CAR BON IMT API ROT FUR APS ROR ORD SRD
(END = kanal tedavisi, CAR = çürük)
"""

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def harita_coz(metin: str) -> dict[int, int]:
    harita = {}
    for parca in metin.split(","):
        sol, sag = parca.split("=")
        kod = sag.strip().upper()
        if kod not in config.CLASS_CODES:
            sys.exit(f"Bilinmeyen sınıf kodu: {kod}. Geçerliler: {' '.join(config.CLASS_CODES)}")
        harita[int(sol)] = config.CLASS_CODES.index(kod)
    return harita


def etiket_dosyasi(img: Path) -> Path | None:
    for aday in (img.parent.parent / "labels" / f"{img.stem}.txt", img.with_suffix(".txt")):
        if aday.exists():
            return aday
    return None


def main():
    ap = argparse.ArgumentParser(description="Eğitim setine dışarıdan veri ekle")
    ap.add_argument("klasor", help="eklenecek veri setinin klasörü")
    ap.add_argument("--map", required=True, help="ör. 0=CAR,1=END  (onların sınıf no = bizim kod)")
    ap.add_argument("--split", choices=["train", "valid"], default="train")
    ap.add_argument("--onek", default=None, help="dosya adı öneki (varsayılan: klasör adı)")
    ap.add_argument("--dene", action="store_true", help="hiçbir şey kopyalama, sadece ne olacağını göster")
    args = ap.parse_args()

    kaynak = Path(args.klasor)
    if not kaynak.is_dir():
        sys.exit(f"Klasör bulunamadı: {kaynak}")
    harita = harita_coz(args.map)
    onek = (args.onek or kaynak.name).replace(" ", "_")

    hedef_img = config.DATASET_DIR / args.split / "images"
    hedef_lbl = config.DATASET_DIR / args.split / "labels"
    if not hedef_img.exists():
        sys.exit(f"Önce veri setini hazırla: python prepare_data.py  ({hedef_img} yok)")

    resimler = sorted(p for p in kaynak.rglob("*") if p.suffix.lower() in IMG_EXT)
    print(f"{len(resimler)} görüntü bulundu: {kaynak}")
    eklenen, etiketsiz, bos = 0, 0, 0
    sayac = Counter()

    for img in resimler:
        lbl = etiket_dosyasi(img)
        if lbl is None:
            etiketsiz += 1
            continue
        satirlar = []
        for satir in lbl.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not satir.strip():
                continue
            parcalar = satir.split()
            eski = int(float(parcalar[0]))
            if eski in harita:
                yeni = harita[eski]
                satirlar.append(" ".join([str(yeni), *parcalar[1:5]]))
                sayac[config.CLASS_CODES[yeni]] += 1
        if not satirlar:
            bos += 1
            continue  # hiç işimize yarayan kutu yoksa alma
        if not args.dene:
            shutil.copy2(img, hedef_img / f"{onek}_{img.stem}{img.suffix.lower()}")
            (hedef_lbl / f"{onek}_{img.stem}.txt").write_text("\n".join(satirlar) + "\n", encoding="utf-8")
        eklenen += 1

    print(f"\n{'[DENEME] ' if args.dene else ''}Eklenen görüntü: {eklenen}")
    print(f"  etiket dosyası bulunamayan: {etiketsiz}")
    print(f"  haritadaki sınıflardan hiç kutu içermeyen (atlandı): {bos}")
    for kod, adet in sayac.most_common():
        print(f"  {config.tr_name(kod):<18}{adet:>7} kutu")
    if args.dene:
        print("\nGerçekten eklemek için --dene olmadan tekrar çalıştır.")
    else:
        print(f"\nHedef: {hedef_img}")
        print("Sonra: python train.py --nazik   (sıfırdan eğitir)")
        print("veya:  python train.py --nazik --model weights/best.pt --epochs 40   (mevcut modelin üstüne)")


if __name__ == "__main__":
    main()
