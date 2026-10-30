"""Modeli test setinde ve başka kliniklerden gelen dış doğrulama setinde ölçer.

Sonuçlar weights/metrics.json dosyasına yazılır ve arayüzde gösterilir.

Kullanım:
    python evaluate.py
    python evaluate.py --weights runs/yolo26s/weights/best.pt
"""

import argparse
import json
import sys
from pathlib import Path

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def evaluate(weights=config.BEST_WEIGHTS, imgsz: int = config.IMGSZ, batch: int = 8,
             data_yaml=None, external_yaml=None, metrics_file=None) -> dict:
    from ultralytics import YOLO

    model = YOLO(str(weights))
    out = {"weights": Path(weights).name, "imgsz": imgsz, "splits": {}}
    sets = [("test", Path(data_yaml or config.DATA_YAML), "test"),
            ("external", Path(external_yaml or config.EXTERNAL_YAML), "val")]
    for key, yaml_path, split in sets:
        if not yaml_path.exists():
            continue
        m = model.val(data=str(yaml_path), split=split, imgsz=imgsz, batch=batch, plots=False,
                      verbose=False, project=str(config.RUNS_DIR), name=f"val_{key}", exist_ok=True)
        classes = {}
        for i, c in enumerate(m.box.ap_class_index):
            p, r, ap50, ap = (float(v) for v in m.box.class_result(i))
            classes[model.names[int(c)]] = {
                "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0,
                "map50": ap50, "map50_95": ap, "instances": int(m.nt_per_class[int(c)]),
            }
        out["splits"][key] = {
            "overall": {"precision": float(m.box.mp), "recall": float(m.box.mr),
                        "map50": float(m.box.map50), "map50_95": float(m.box.map)},
            "classes": classes,
        }

    config.WEIGHTS_DIR.mkdir(exist_ok=True)
    hedef = Path(metrics_file or config.METRICS_FILE)
    hedef.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print_report(out, hedef)
    return out


def print_report(metrics: dict, dosya=None):
    titles = {"test": "İÇ TEST SETİ (aynı klinik, eğitimde hiç görülmedi)",
              "external": "DIŞ DOĞRULAMA (başka klinikler, farklı cihazlar)"}
    for key, res in metrics["splits"].items():
        print(f"\n=== {titles.get(key, key)} ===")
        print(f"{'Bulgu':<18}{'Kesinlik':>10}{'Duyarlılık':>12}{'F1':>7}{'mAP50':>8}{'Adet':>7}   Makale (P / R)")
        kodlar = [k for k in config.TARGET_CODES if k in res["classes"]]
        kodlar += [k for k in res["classes"] if k not in kodlar]
        for code in kodlar:
            c = res["classes"][code]
            base = config.PAPER_BASELINE.get(key, {}).get(code)
            ref = f"{base['precision']:.2f} / {base['recall']:.2f}" if base else "-"
            print(f"{config.tr_name(code):<18}{c['precision']:>10.3f}{c['recall']:>12.3f}{c['f1']:>7.3f}"
                  f"{c['map50']:>8.3f}{c['instances']:>7}   {ref}")
        o = res["overall"]
        etiket = f"({len(res['classes'])} sınıf ort.)"
        print(f"{etiket:<18}{o['precision']:>10.3f}{o['recall']:>12.3f}{'':>7}{o['map50']:>8.3f}")
    print(f"\nKaydedildi: {dosya or config.METRICS_FILE}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default=str(config.BEST_WEIGHTS))
    ap.add_argument("--imgsz", type=int, default=config.IMGSZ)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--data", default=None)
    ap.add_argument("--external", default=None)
    ap.add_argument("--out", default=None, help="metrics json çıktısı")
    a = ap.parse_args()
    evaluate(a.weights, a.imgsz, a.batch, a.data, a.external, a.out)
