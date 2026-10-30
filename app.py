"""Web arayüzü: röntgeni yükle, çürük ve kanal tedavileri işaretlenmiş olarak gelsin.

Kullanım:
    python app.py                  -> tarayıcıda http://127.0.0.1:7860 açılır
    ("Diş Röntgeni Analizi.bat" dosyasına çift tıklamak da aynı işi yapar)
"""

import json
import os
import sys

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")  # görüntüler/kullanım bilgisi dışarı gitmesin

import gradio as gr

import config
from detector import DentalDetector, crop_finding, draw_findings, load_image, select, summarize

detector = DentalDetector()

# Önce çürük ve kanal, sonra klinik olarak en ilgili olanlar
ORDER = ["CAR", "END", "API", "OBT", "PRR", "IMP", "IMT", "BON", "ROT", "FUR", "APS", "ROR", "ORD", "SRD"]
CHOICES = [(config.tr_name(c), c) for c in ORDER if c in detector.code_to_id]
SHAPES = [("Elips (yuvarlak)", "ellipse"), ("Kutu", "box")]
PRESETS = {
    "Tarama · hiçbirini kaçırma": 0.10,
    "Dengeli": 0.25,
    "Kesin · yalnızca netler": 0.40,
    "Kendim ayarlarım": None,
}


def analyze(image):
    """Modeli tek sefer, düşük eşikle ve tüm sınıflar için çalıştırır; süzmeyi render yapar."""
    if image is None:
        return None, []
    img = load_image(image)
    return img, detector.detect(img, conf=0.05, codes=None)


def bar(conf: float) -> str:
    dolu = round(conf * 10)
    return f"%{conf * 100:.0f}  " + "█" * dolu + "░" * (10 - dolu)


def render(img, all_findings, conf, codes, shape):
    if img is None:
        return None, "", [], []
    codes = codes or []
    findings = select(all_findings, conf, codes)
    out = draw_findings(img, findings, shape=shape)
    rows = [[f.no, f.name, bar(f.confidence)] for f in findings]
    galeri = [(crop_finding(img, f), f"{f.no}. {f.name} · %{f.confidence * 100:.0f}") for f in findings[:12]]

    if findings:
        ozet = f"### {summarize(findings)}"
    else:
        ozet = "### Seçili bulgulardan hiçbiri tespit edilmedi"
    daha = len([f for f in all_findings if f.code in codes and f.confidence < conf])
    if daha:
        ozet += f"\n\nEşiğin altında {daha} şüpheli bölge daha var — kaydırıcıyı sola çekerek görebilirsin."
    return out, ozet, rows, galeri


def esik_sec(secim, mevcut):
    deger = PRESETS.get(secim)
    return gr.update(value=deger if deger is not None else mevcut)


def guvenilirlik_markdown() -> str:
    """Dış doğrulama setinden (başka kliniklerin cihazları) gerçekçi beklenti tablosu."""
    yol = config.WEIGHTS_DIR / "guvenilirlik.json"
    if not yol.exists():
        return ""
    veri = json.loads(yol.read_text(encoding="utf-8")).get("external")
    if not veri:
        return ""
    n_img = veri["resim"]
    satirlar = ["", f"**Başka bir klinikten gelen röntgende ne bekleyebilirsin?** "
                    f"({n_img} röntgenlik bağımsız test, model bu cihazları hiç görmedi)", "",
                "| Bulgu | Eşik | Gerçeklerin kaçını buluyor | İşaretlediğinin kaçı doğru | Röntgen başına yanlış |",
                "|---|---|---|---|---|"]
    for code in config.TARGET_CODES:
        s = veri["siniflar"][code]
        gercek = s["gercek"]
        for esik in (0.10, 0.25, 0.40):
            secilen = [t for t in s["tahminler"] if t[0] >= esik]
            tp = sum(1 for t in secilen if t[1])
            fp = len(secilen) - tp
            kesinlik = tp / len(secilen) if secilen else 0
            satirlar.append(f"| {config.tr_name(code)} | {esik:.2f} | %{tp / gercek * 100:.0f} "
                            f"| %{kesinlik * 100:.0f} | {fp / n_img:.2f} |")
    return "\n".join(satirlar)


def metrics_markdown() -> str:
    if not config.METRICS_FILE.exists():
        return "Henüz ölçüm yok. `python evaluate.py` çalıştırın."
    m = json.loads(config.METRICS_FILE.read_text(encoding="utf-8"))
    # Çürük ve periapikal lezyon ikinci modelden geliyorsa skorları da oradan oku
    m_curuk = (json.loads(config.CURUK_METRICS.read_text(encoding="utf-8"))
               if detector.curuk_codes and config.CURUK_METRICS.exists() else None)
    set_names = {"test": "İç test (aynı klinik)", "external": "Dış test (başka klinikler)"}
    lines = ["| Bulgu | Test seti | Kesinlik | Duyarlılık | mAP50 |", "|---|---|---|---|---|"]
    for code in config.TARGET_CODES:
        kaynak = m_curuk if (m_curuk and code in detector.curuk_codes) else m
        for key, res in kaynak["splits"].items():
            c = res["classes"].get(code)
            if c:
                lines.append(f"| {config.tr_name(code)} | {set_names.get(key, key)} | %{c['precision'] * 100:.0f} "
                             f"| %{c['recall'] * 100:.0f} | %{c['map50'] * 100:.0f} |")
    lines += [
        "",
        "- **Kesinlik:** Model \"çürük\" dediğinde ne sıklıkla haklı çıkıyor.",
        "- **Duyarlılık:** Gerçekte var olan çürüklerin yüzde kaçını yakalıyor.",
        "- Görüntüdeki **%** değeri, modelin o işaretten ne kadar emin olduğudur (güven skoru); "
        "tek başına \"doğru olma ihtimali\" anlamına gelmez.",
        guvenilirlik_markdown(),
    ]
    return "\n".join(lines)


with gr.Blocks(title="Diş Röntgeni Analizi") as demo:
    gr.Markdown(
        "# Diş Röntgeni Analizi\n"
        "Panoramik röntgeni yükleyin: model **çürükleri** ve **kanal tedavili dişleri** yuvarlak içine alır "
        "ve her birinin yanına güven skorunu yazar."
    )
    st_img = gr.State(None)
    st_findings = gr.State([])

    with gr.Row():
        with gr.Column(scale=2):
            inp = gr.Image(label="Röntgen", type="pil", image_mode=None, sources=["upload", "clipboard"])
            preset = gr.Radio(list(PRESETS), value="Dengeli", label="Hassasiyet")
            conf = gr.Slider(0.05, 0.95, value=0.25, step=0.05, label="Güven eşiği",
                             info="Düşürürsen daha çok (ama daha şüpheli) işaret çıkar.")
            with gr.Accordion("Diğer ayarlar", open=False):
                codes = gr.CheckboxGroup(CHOICES, value=config.TARGET_CODES, label="Gösterilecek bulgular")
                shape = gr.Radio(SHAPES, value="ellipse", label="İşaret şekli")
            examples = sorted(p for p in config.EXAMPLES_DIR.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
            if examples:
                gr.Examples([[str(p)] for p in examples], inputs=inp, label="Örnek röntgenler")
        with gr.Column(scale=3):
            out = gr.Image(label="Sonuç", type="pil", format="jpeg", interactive=False)
            summary = gr.Markdown()
            with gr.Tab("Bulgu listesi"):
                table = gr.Dataframe(headers=["No", "Bulgu", "Güven"], datatype=["number", "str", "str"],
                                     interactive=False, label=None)
            with gr.Tab("Yakın görüntüler"):
                gallery = gr.Gallery(label=None, columns=3, height=420, object_fit="contain",
                                     show_label=False)

    with gr.Accordion("Model ne kadar doğru?", open=False):
        gr.Markdown(metrics_markdown())

    gr.Markdown(
        "> ⚠️ Bu araç tanı koymaz; yalnızca karar desteği amaçlıdır. "
        "Sonuçlar mutlaka diş hekimi tarafından değerlendirilmelidir."
    )

    view_inputs = [st_img, st_findings, conf, codes, shape]
    view_outputs = [out, summary, table, gallery]
    inp.change(analyze, inp, [st_img, st_findings]).then(render, view_inputs, view_outputs)
    preset.change(esik_sec, [preset, conf], conf)
    for ctrl in (conf, codes, shape):
        ctrl.change(render, view_inputs, view_outputs)


def konsolu_hazirla():
    """Çift tıkla açılan pencerede düzgün Türkçe ve anlaşılır bir karşılama."""
    import ctypes

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if os.name == "nt":
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("Diş Röntgeni Analizi")
        except Exception:
            pass
    print("\n  ┌──────────────────────────────────────────────┐")
    print("  │            DİŞ RÖNTGENİ ANALİZİ              │")
    print("  └──────────────────────────────────────────────┘\n")
    print("  Tarayıcı birazdan kendiliğinden açılacak.")
    print("  Röntgeni sürükleyip bırakman yeterli.\n")
    print("  KAPATMAK İÇİN: bu siyah pencereyi kapat.\n")


if __name__ == "__main__":
    konsolu_hazirla()
    demo.launch(inbrowser=True, quiet=True, prevent_thread_lock=True)
    print(f"  Hazır: {demo.local_url}   (kapatmak için bu pencereyi kapat)\n")
    demo.block_thread()
