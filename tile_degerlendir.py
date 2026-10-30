"""Parçalı (tiling) tahmini tam röntgen üzerinde ölçer.

Her röntgen 6 parçaya bölünür, her parça ayrı ayrı modele verilir, kutular tam görüntü
koordinatlarına taşınır ve üst üste binen kutular NMS ile temizlenir. Sonuç, normal
(tek geçişli) ölçümle birebir karşılaştırılabilsin diye Ultralytics'in kendi
ap_per_class fonksiyonuyla değerlendirilir.

Kullanım:
    python tile_degerlendir.py --weights weights/tile.pt
    python tile_degerlendir.py --weights weights/curuk2.pt --tek-gecis   # kıyas için
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision.ops import batched_nms
from ultralytics.utils.metrics import ap_per_class

import config
from curuk_veri import HEDEF as CURUK_DIR
from tile_veri import parcalar

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

IMG_EXT = {".jpg", ".jpeg", ".png"}
IOU_NMS = 0.60      # parçalar arası tekrarları temizlemek için
IOU_ESIK = 0.50     # doğru tespit sayılma eşiği


def tahmin_parcali(model, img: Image.Image, imgsz: int, conf: float):
    W, H = img.size
    kutular, skorlar, siniflar = [], [], []
    for x0, y0, x1, y1 in parcalar(W, H):
        r = model.predict(img.crop((x0, y0, x1, y1)), conf=conf, imgsz=imgsz,
                          max_det=300, verbose=False)[0]
        if len(r.boxes) == 0:
            continue
        b = r.boxes.xyxy.cpu().clone()
        b[:, [0, 2]] += x0
        b[:, [1, 3]] += y0
        kutular.append(b)
        skorlar.append(r.boxes.conf.cpu())
        siniflar.append(r.boxes.cls.cpu())
    if not kutular:
        return torch.zeros((0, 4)), torch.zeros(0), torch.zeros(0)
    kutular, skorlar, siniflar = torch.cat(kutular), torch.cat(skorlar), torch.cat(siniflar)
    tut = batched_nms(kutular, skorlar, siniflar.int(), IOU_NMS)
    return kutular[tut], skorlar[tut], siniflar[tut]


def tahmin_tek(model, img: Image.Image, imgsz: int, conf: float):
    r = model.predict(img, conf=conf, imgsz=imgsz, max_det=1000, verbose=False)[0]
    return r.boxes.xyxy.cpu(), r.boxes.conf.cpu(), r.boxes.cls.cpu()


def gercek_kutular(etiket: Path, W: int, H: int):
    kutular, siniflar = [], []
    for satir in etiket.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            c, cx, cy, bw, bh = satir.split()[:5]
            cx, cy, bw, bh = float(cx) * W, float(cy) * H, float(bw) * W, float(bh) * H
            kutular.append([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2])
            siniflar.append(int(c))
    return torch.tensor(kutular).reshape(-1, 4), torch.tensor(siniflar, dtype=torch.int64)


def iou_matris(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    alan_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    alan_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    lt = torch.max(a[:, None, :2], b[None, :, :2])
    rb = torch.min(a[:, None, 2:], b[None, :, 2:])
    wh = (rb - lt).clamp(min=0)
    kesisim = wh[..., 0] * wh[..., 1]
    return kesisim / (alan_a[:, None] + alan_b[None, :] - kesisim + 1e-9)


def olc(model, bolum_dizin: Path, imgsz: int, parcali: bool, conf: float = 0.01) -> dict:
    tp_hepsi, conf_hepsi, pred_cls_hepsi, hedef_cls_hepsi = [], [], [], []
    resimler = sorted(p for p in (bolum_dizin / "images").iterdir() if p.suffix.lower() in IMG_EXT)
    for i, yol in enumerate(resimler, 1):
        if i % 40 == 0:
            print(f"    {i}/{len(resimler)}", flush=True)
        img = Image.open(yol).convert("RGB")
        gt_kutu, gt_cls = gercek_kutular(bolum_dizin / "labels" / f"{yol.stem}.txt", *img.size)
        hedef_cls_hepsi.append(gt_cls.numpy())

        p_kutu, p_conf, p_cls = (tahmin_parcali if parcali else tahmin_tek)(model, img, imgsz, conf)
        if len(p_kutu) == 0:
            continue
        sira = p_conf.argsort(descending=True)
        p_kutu, p_conf, p_cls = p_kutu[sira], p_conf[sira], p_cls[sira]

        tp = np.zeros(len(p_kutu), dtype=bool)
        if len(gt_kutu):
            iou = iou_matris(p_kutu, gt_kutu)
            kullanildi = torch.zeros(len(gt_kutu), dtype=torch.bool)
            for j in range(len(p_kutu)):
                uygun = (gt_cls == p_cls[j]) & ~kullanildi & (iou[j] >= IOU_ESIK)
                if uygun.any():
                    en_iyi = torch.where(uygun, iou[j], torch.tensor(-1.0)).argmax()
                    kullanildi[en_iyi] = True
                    tp[j] = True
        tp_hepsi.append(tp)
        conf_hepsi.append(p_conf.numpy())
        pred_cls_hepsi.append(p_cls.numpy())

    tp = np.concatenate(tp_hepsi).reshape(-1, 1) if tp_hepsi else np.zeros((0, 1), dtype=bool)
    sonuc = ap_per_class(tp, np.concatenate(conf_hepsi), np.concatenate(pred_cls_hepsi),
                         np.concatenate(hedef_cls_hepsi))
    _, _, p, r, f1, ap, siniflar = sonuc[:7]
    return {model.names[int(c)]: {"precision": float(p[i]), "recall": float(r[i]),
                                  "f1": float(f1[i]), "map50": float(ap[i, 0])}
            for i, c in enumerate(siniflar)}


def main():
    ap_ = argparse.ArgumentParser(description="Parçalı tahmin değerlendirmesi")
    ap_.add_argument("--weights", default="weights/tile.pt")
    ap_.add_argument("--imgsz", type=int, default=config.IMGSZ)
    ap_.add_argument("--tek-gecis", action="store_true", help="parçalamadan, normal tahminle ölç")
    ap_.add_argument("--kaynak", choices=["curuk", "ana"], default="curuk",
                     help="hangi veri setinin test bölümleri kullanılsın")
    ap_.add_argument("--out", default=None)
    a = ap_.parse_args()

    from ultralytics import YOLO
    model = YOLO(a.weights)
    parcali = not a.tek_gecis
    print(f"Model: {Path(a.weights).name} | {'PARÇALI (6 parça)' if parcali else 'tek geçiş'} | {a.imgsz} piksel")

    cikti = {}
    for ad, baslik in (("test", "İÇ TEST SETİ"), ("external", "DIŞ DOĞRULAMA")):
        print(f"\n=== {baslik}")
        cikti[ad] = olc(model, CURUK_DIR / ad, a.imgsz, parcali)
        print(f"{'Bulgu':<20}{'Kesinlik':>10}{'Duyarlılık':>12}{'F1':>8}{'mAP50':>8}")
        for kod, d in cikti[ad].items():
            print(f"{config.tr_name(kod):<20}{d['precision']:>10.3f}{d['recall']:>12.3f}"
                  f"{d['f1']:>8.3f}{d['map50']:>8.3f}")

    yol = Path(a.out) if a.out else config.WEIGHTS_DIR / (Path(a.weights).stem + "_tile_metrics.json")
    yol.write_text(json.dumps(cikti, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKaydedildi: {yol}")


if __name__ == "__main__":
    main()
