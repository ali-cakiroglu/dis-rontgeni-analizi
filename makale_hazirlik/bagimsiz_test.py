"""Makaleye hazırlık: bağımsız test, eşiğin yalnız doğrulama setinde seçilmesi ve alt küme tekrarı.

1) Kopya/sızıntı kontrolü: Veri setinde hasta kimliği yok. Bu yüzden test ve dış doğrulama
   röntgenlerinin, modelin gördüğü herhangi bir röntgenle (eğitim, doğrulama, 5.059'luk ön eğitim
   seti) birebir ya da neredeyse aynı olup olmadığına görüntü özetiyle (16x16 fark özeti, 256 bit)
   bakılır. Aynı hastanın aynı röntgeni farklı bölümlere düşmüşse burada yakalanır.
2) Eşik yalnız doğrulama setinde (valid, 153 röntgen) F1'i en yüksek yapan değer olarak seçilir.
3) Bu eşikle iç testte (100) ve dış doğrulamada (180, başka klinikler) BİR KEZ ölçülür.
4) Test ve dış doğrulama sabit tohumla 4 alt kümeye bölünür; AP50 ve F1 ortalama ± sapma verilir.
   Ayrıca röntgenler üzerinde 1000 kez önyükleme (bootstrap) ile AP50 için %95 güven aralığı.

Kullanım (proje kökünden):  .venv\\Scripts\\python.exe makale_hazirlik\\bagimsiz_test.py
"""

import json
import random
import statistics
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BURASI = Path(__file__).resolve().parent
KOK = BURASI.parent
sys.path.insert(0, str(KOK))

import config  # noqa: E402
from guvenilirlik import topla  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOHUM = 2242
ALT_KUME = 4
UZAKLIK_ESIGI = 10          # 256 bitten en çok 10'u farklıysa "neredeyse aynı" kabul edilir
D = config.DATASET_DIR
BOLUMLER = {
    "valid": D / "valid" / "images",
    "test": D / "test" / "images",
    "external": D / "test_alte_cabinete" / "Ext-validation" / "images",
}
UZANTI = {".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------------- 1) kopya kontrolü
def ozet(yol: Path) -> np.ndarray:
    g = Image.open(yol).convert("L").resize((17, 16), Image.BILINEAR)
    a = np.asarray(g, dtype=np.int16)
    return (a[:, 1:] > a[:, :-1]).flatten()


def ozetler(klasor: Path) -> tuple[list[str], np.ndarray]:
    yollar = sorted(p for p in klasor.rglob("*") if p.suffix.lower() in UZANTI)
    return [p.name for p in yollar], np.array([ozet(p) for p in yollar])


def kopya_kontrolu() -> dict:
    print("1) Kopya kontrolü: görüntü özetleri hesaplanıyor...", flush=True)
    havuz = {
        "egitim": D / "train" / "images",
        "dogrulama": D / "valid" / "images",
        "on_egitim_5059": config.DATA_DIR / "ek_veri" / "images",
    }
    havuz_oz = {k: ozetler(v) for k, v in havuz.items()}
    sonuc = {}
    for bolum in ("test", "external"):
        adlar, oz = ozetler(BOLUMLER[bolum])
        sonuc[bolum] = {"roentgen": len(adlar)}
        for hk, (h_ad, h_oz) in havuz_oz.items():
            uz = (oz[:, None, :] != h_oz[None, :, :]).sum(axis=2)      # Hamming uzaklığı
            en_yakin = uz.min(axis=1)
            supheli = [(adlar[i], h_ad[int(uz[i].argmin())], int(en_yakin[i]))
                       for i in np.where(en_yakin <= UZAKLIK_ESIGI)[0]]
            sonuc[bolum][hk] = {"havuz": len(h_ad), "en_kucuk_uzaklik": int(en_yakin.min()),
                                "ortanca_en_yakin": float(np.median(en_yakin)),
                                "neredeyse_ayni": len(supheli), "ornekler": supheli[:10]}
            print(f"   {bolum:<9} vs {hk:<15} ({len(h_ad):>5}): en küçük uzaklık {int(en_yakin.min()):>3}, "
                  f"ortanca {np.median(en_yakin):>5.1f}, neredeyse aynı (≤{UZAKLIK_ESIGI}): {len(supheli)}")
    return sonuc


# ---------------------------------------------------------------- 2-4) ölçüm
def kayitlar(veri: dict, code: str, idx=None):
    """Seçilen röntgenlerin (gerçek sayısı, [(güven, doğru)]) kayıtlarını birleştirir."""
    gb = veri["goruntu_basi"][code]
    secim = range(len(gb)) if idx is None else idx
    gercek, tahmin = 0, []
    for i in secim:
        g, k = gb[i]
        gercek += g
        tahmin += [(c, t) for c, t, _ in k]
    return gercek, tahmin


def ap50(gercek: int, tahmin) -> float:
    """101 noktalı enterpolasyonla AP (IoU 0,5 eşleştirmesi topla() içinde yapıldı)."""
    if gercek == 0:
        return float("nan")
    t = sorted(tahmin, key=lambda x: -x[0])
    tp = np.cumsum([1 if d else 0 for _, d in t])
    fp = np.cumsum([0 if d else 1 for _, d in t])
    if len(t) == 0:
        return 0.0
    recall = tp / gercek
    precision = tp / np.maximum(tp + fp, 1)
    mrec = np.concatenate(([0.0], recall, [1.0]))
    mpre = np.concatenate(([1.0], precision, [0.0]))
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))
    x = np.linspace(0, 1, 101)
    alan = getattr(np, "trapezoid", None) or np.trapz
    return float(alan(np.interp(x, mrec, mpre), x))


def prf(gercek: int, tahmin, esik: float):
    s = [d for c, d in tahmin if c >= esik]
    tp = sum(s)
    p = tp / len(s) if s else 0.0
    r = tp / gercek if gercek else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def esik_sec(gercek, tahmin) -> float:
    adaylar = [round(x, 2) for x in np.arange(0.05, 0.61, 0.01)]
    return max(adaylar, key=lambda e: (prf(gercek, tahmin, e)[2], -e))


def main():
    sonuc = {"kopya_kontrolu": kopya_kontrolu()}

    from detector import DentalDetector
    # weights/best.pt ve weights/curuk2.pt diskte yok; aynı modeller şu dosyalarda:
    ana = config.WEIGHTS_DIR / "yolo26m.pt"                 # metrics.json == yolo26m_metrics.json
    curuk = KOK / "yedek_calisan_surum" / "curuk2.pt"
    det = DentalDetector(ana, curuk_weights=curuk)
    sonuc["agirliklar"] = {"ana": str(ana.relative_to(KOK)), "curuk": str(curuk.relative_to(KOK))}
    veriler = {}
    for bolum, klasor in BOLUMLER.items():
        print(f"\n2) {bolum}: tahminler alınıyor...", flush=True)
        veriler[bolum] = topla(det, klasor, config.TARGET_CODES)

    rng = random.Random(TOHUM)
    sonuc["siniflar"] = {}
    for code in config.TARGET_CODES:
        g, t = kayitlar(veriler["valid"], code)
        esik = esik_sec(g, t)
        p, r, f = prf(g, t, esik)
        cs = {"esik_dogrulamada_secildi": esik,
              "dogrulama": {"P": p, "R": r, "F1": f, "AP50": ap50(g, t)}}
        print(f"\n=== {config.tr_name(code)} — eşik doğrulamada seçildi: {esik:.2f} "
              f"(doğrulama F1 {f:.3f})")
        for bolum in ("test", "external"):
            v = veriler[bolum]
            n = v["resim_sayisi"]
            g, t = kayitlar(v, code)
            p, r, f = prf(g, t, esik)
            ap = ap50(g, t)
            # alt kümeler
            idx = list(range(n))
            rng.shuffle(idx)
            parcalar = [idx[i::ALT_KUME] for i in range(ALT_KUME)]
            ap_k, f_k = [], []
            for pc in parcalar:
                gg, tt = kayitlar(v, code, pc)
                ap_k.append(ap50(gg, tt))
                f_k.append(prf(gg, tt, esik)[2])
            # önyükleme
            br = np.random.default_rng(TOHUM)
            boot = []
            for _ in range(1000):
                ornek = br.integers(0, n, n)
                gg, tt = kayitlar(v, code, ornek)
                if gg:
                    boot.append(ap50(gg, tt))
            alt, ust = np.percentile(boot, [2.5, 97.5])
            cs[bolum] = {"roentgen": n, "gercek": g, "P": p, "R": r, "F1": f, "AP50": ap,
                         "AP50_guven_araligi_95": [float(alt), float(ust)],
                         "alt_kume_AP50": ap_k, "alt_kume_F1": f_k,
                         "AP50_ort": statistics.mean(ap_k), "AP50_sapma": statistics.stdev(ap_k),
                         "F1_ort": statistics.mean(f_k), "F1_sapma": statistics.stdev(f_k)}
            print(f"  {bolum:<9} n={n:<4} gerçek={g:<4} P {p:.3f}  R {r:.3f}  F1 {f:.3f}  AP50 {ap:.3f} "
                  f"[%95 GA {alt:.3f}–{ust:.3f}]")
            print(f"            {ALT_KUME} alt küme: AP50 {statistics.mean(ap_k):.3f} ± {statistics.stdev(ap_k):.3f}"
                  f"  ({', '.join(f'{x:.3f}' for x in ap_k)});  F1 {statistics.mean(f_k):.3f} ± "
                  f"{statistics.stdev(f_k):.3f}")
        sonuc["siniflar"][code] = cs

    yol = BURASI / "bagimsiz_test.json"
    yol.write_text(json.dumps(sonuc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKaydedildi: {yol}")


if __name__ == "__main__":
    main()
