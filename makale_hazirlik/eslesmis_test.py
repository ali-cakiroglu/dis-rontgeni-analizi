"""İddia 2: yöntemin (curuk2) baseline'a (tek modelli ilk sürüm) üstünlüğü rastlantı mı?

Üç model AYNI röntgenlerde çalıştırılır; çürük (CAR) AP50 farkı için EŞLEŞTİRİLMİŞ önyükleme yapılır:
her yinelemede aynı röntgen örneklemi iki modele birden uygulanır, fark o örneklemde hesaplanır.

  baseline : weights/best_yolo26s.pt  (14 sınıflı YOLO26s, yalnız kendi verisi; eğitim zincirinin başı)
  karisik  : weights/curuk.pt         (baseline'dan devam, kendi verisi + 5.059 dış röntgen birlikte, 15 epok)
  yontem   : yedek_calisan_surum/curuk2.pt (karisik'tan devam, yalnız kendi verisi, 20 epok)

Kullanım (proje kökünden):  .venv\\Scripts\\python.exe makale_hazirlik\\eslesmis_test.py
Çıktı: makale_hazirlik/eslesmis_test.json
"""

import json
import sys
from pathlib import Path

import numpy as np

BURASI = Path(__file__).resolve().parent
KOK = BURASI.parent
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(BURASI))

import config  # noqa: E402
from guvenilirlik import topla  # noqa: E402
from bagimsiz_test import ap50, kayitlar, BOLUMLER  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOHUM = 2242
B = 2000
KOD = "CAR"
W = config.WEIGHTS_DIR
MODELLER = {
    "baseline": (W / "best_yolo26s.pt", None),
    "karisik": (W / "best_yolo26s.pt", W / "curuk.pt"),
    "yontem": (W / "yolo26m.pt", KOK / "yedek_calisan_surum" / "curuk2.pt"),
}
KARSILASTIRMALAR = [("yontem", "baseline"), ("yontem", "karisik")]


def main():
    from detector import DentalDetector

    veri = {}
    for ad, (ana, curuk) in MODELLER.items():
        det = DentalDetector(ana, curuk_weights=curuk)
        kaynak = "curuk modeli" if det.curuk_model and KOD in det.curuk_codes else "ana model"
        print(f"\n{ad}: {ana.name} + {curuk.name if curuk else '-'}  (çürük {kaynak}den)", flush=True)
        veri[ad] = {}
        for bolum in ("test", "external"):
            print(f"  {bolum}...", flush=True)
            veri[ad][bolum] = topla(det, BOLUMLER[bolum], [KOD])

    sonuc = {"modeller": {k: [str(a.relative_to(KOK)), str(c.relative_to(KOK)) if c else None]
                          for k, (a, c) in MODELLER.items()},
             "B": B, "tohum": TOHUM, "bolumler": {}}
    for bolum in ("test", "external"):
        n = veri["baseline"][bolum]["resim_sayisi"]
        assert all(veri[m][bolum]["resim_sayisi"] == n for m in MODELLER)
        ap = {m: ap50(*kayitlar(veri[m][bolum], KOD)) for m in MODELLER}
        rng = np.random.default_rng(TOHUM)
        orneklem = [rng.integers(0, n, n) for _ in range(B)]
        boot = {m: np.array([ap50(*kayitlar(veri[m][bolum], KOD, o)) for o in orneklem]) for m in MODELLER}
        b = {"roentgen": n, "AP50": ap, "karsilastirma": {}}
        print(f"\n=== {bolum} (n={n} röntgen) — AP50: "
              + ", ".join(f"{m} {v:.3f}" for m, v in ap.items()))
        for a, c in KARSILASTIRMALAR:
            d = boot[a] - boot[c]
            d = d[~np.isnan(d)]
            alt, ust = np.percentile(d, [2.5, 97.5])
            p_tek = float(np.mean(d <= 0))
            p_cift = min(1.0, 2 * min(np.mean(d <= 0), np.mean(d >= 0)))
            b["karsilastirma"][f"{a}-{c}"] = {
                "fark": ap[a] - ap[c], "GA95": [float(alt), float(ust)],
                "p_tek_yonlu": p_tek, "p_cift_yonlu": float(p_cift), "gecerli_yineleme": int(d.size)}
            print(f"  {a} − {c}: fark {ap[a] - ap[c]:+.3f}  [%95 GA {alt:+.3f} – {ust:+.3f}]  "
                  f"önyükleme p (çift yönlü) {p_cift:.3f}")
        sonuc["bolumler"][bolum] = b

    yol = BURASI / "eslesmis_test.json"
    yol.write_text(json.dumps(sonuc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKaydedildi: {yol}")


if __name__ == "__main__":
    main()
