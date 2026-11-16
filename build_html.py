# -*- coding: utf-8 -*-
"""Сборка экранных HTML-буклетов: self-contained (шрифты, стили, скрипты внутри файла)."""
import base64, pathlib
from content import SKILLS, SHARED, SERIES, SERIES_SUB

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"
FONTS = [
    ("PT Sans", "PTSans-Regular", 400, "normal"),
    ("PT Sans", "PTSans-Bold", 700, "normal"),
    ("PT Sans", "PTSans-Italic", 400, "italic"),
    ("PT Serif", "PTSerif-Regular", 400, "normal"),
    ("PT Serif", "PTSerif-Bold", 700, "normal"),
]

ARROW = '<svg viewBox="0 0 16 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 5h13"/><path d="M10.6 1.6 14 5l-3.4 3.4"/></svg>'
ICO_DOWN = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M8 2.5v9"/><path d="M4.4 8.2 8 11.8l3.6-3.6"/><path d="M2.8 13.5h10.4"/></svg>'
ICO_PRINT = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4.5 6V2.5h7V6"/><rect x="2.5" y="6" width="11" height="5" rx="1.4"/><path d="M4.5 9.5h7v4h-7z"/></svg>'

EMBLEM = {
    "trud": '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 6c9 12 16 20 16 28a16 16 0 0 1-32 0c0-8 7-16 16-28z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M20 38c4-3 8 3 12 0s8 3 12 0" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M22 46c4-3 8 3 12 0" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "stop": '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M22 6h20l16 16v20L42 58H22L6 42V22z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M22 32h20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><circle cx="32" cy="22" r="2.6" fill="currentColor"/><circle cx="32" cy="42" r="2.6" fill="currentColor"/></svg>',
    "pros_cons": '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 10v44M18 54h28M12 22h40" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><path d="M12 22l-6 14h12l-6-14zm40 0l-6 14h12l-6-14z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/></svg>',

}

TOOL_KIND = {
    "trud": ["cold", "relax", "move", "breath"],
    "stop": ["freeze", "pause", "observe", "wise"],
    "pros_cons": ["pc1", "pc2", "pc3", "pc4"],
}
AUTOSTART = {"cold", "relax", "move", "breath", "freeze", "pause"}


def font_css():
    out = []
    for fam, fn, weight, style in FONTS:
        b64 = base64.b64encode((ASSETS / (fn + ".woff2")).read_bytes()).decode()
        out.append("@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (fam, style, weight, b64))
    return "\n".join(out)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dash_list(items):
    return '<ul class="dash">' + "".join("<li>%s</li>" % esc(i) for i in items) + "</ul>"


def how_list(items):
    return '<ol class="how">' + "".join("<li>%s</li>" % esc(i) for i in items) + "</ol>"


def block(title, inner):
    return '<div class="block"><h3>%s</h3>%s</div>' % (esc(title), inner)


def pnum(n, label):
    return '<p class="pnum">%s · %s</p>' % (n, esc(label))


def pfoot(sk, n):
    return ('<div class="pfoot printonly"><span>%s · %s</span><span>%d / 8</span></div>'
            % (sk["acronym"], SERIES_SUB, n))


def sections(sk):
    other = SKILLS[sk["other"]]
    P = []

    # ---------------------------------------------------------------- обложка
    rows = "".join(
        '<button class="arow" type="button" data-jump="step-%d"><span class="bl">%s</span>'
        '<span class="nm">%s</span><span class="hint">%s</span></button>' % (i, l, esc(n), esc(h))
        for i, (l, n, h) in enumerate(sk["letters"], 1)
    )
    P.append(f"""<section class="page cover reveal" id="cover">
  <div class="cover-top">
    <div><div class="eyebrow">{SERIES}</div><div class="eyebrow q" style="margin-top:5px">{SERIES_SUB}</div></div>
    <div class="seal">{EMBLEM[sk['id']]}</div>
  </div>
  <h1>{sk['title']}</h1>
  <div class="latin">навык {sk['latin']}</div>
  <p class="tagline">{esc(sk['tagline'])}</p>
  <p class="cover-note">{esc(sk['cover_note'])}</p>
  <div class="acronym">{rows}</div>
  <p class="lead" style="margin-top:18px">{esc(sk['lead'])}</p>
  <div class="box tip"><span class="lbl">Как открывать буклет</span>{esc(sk['cover_callout'])}</div>
  <div class="cover-cta noprint">
    <button class="btn" type="button" id="cover-sos">Накрывает прямо сейчас</button>
    <button class="btn ghost" type="button" data-jump="step-1">К шагам навыка</button>
    <a class="btn ghost" href="{sk['id']}.pdf" download>{ICO_DOWN}<span>PDF A5</span></a>
  </div>
  <div class="cover-foot">Карманная памятка для клиента · 8 страниц · по навыкам М. Линехан</div>
  {pfoot(sk, 1)}
</section>""")

    # ------------------------------------------------------- 01 когда применять
    P.append(f"""<section class="page reveal" id="when">
  {pnum('01', 'Когда применять')}
  <h2>Сначала проверьте: это кризис?</h2>
  {block(SHARED['crisis']['title'], dash_list(SHARED['crisis']['items']))}
  {block(SHARED['use_when']['title'], dash_list(SHARED['use_when']['items']))}
  {block(sk['situations']['title'], dash_list(sk['situations']['items']))}
  <div class="box tip"><span class="lbl">Цель навыка</span>Пережить кризис, не сделав хуже. Не решить проблему и не стать спокойным навсегда — только не ухудшить.</div>
  {pfoot(sk, 2)}
</section>""")

    # --------------------------------------------------------- 02 границы навыка
    zones = "".join(
        '<div class="zone"><div class="rng">%s</div><div class="zt">%s</div><div class="zd">%s</div></div>'
        % (r, esc(t), esc(d)) for r, t, d in SHARED["scale"]["zones"]
    )
    chain = []
    for i, s in enumerate(SHARED["chain"]["steps"]):
        chain.append('<span class="pill%s">%s</span>' % (" on" if s == sk["acronym"] else "", esc(s)))
        if i < len(SHARED["chain"]["steps"]) - 1:
            chain.append('<span class="arrow">%s</span>' % ARROW)
    P.append(f"""<section class="page reveal" id="limits">
  {pnum('02', 'Границы навыка')}
  <h2>Что навык делает и чего не делает</h2>
  {block(sk['limits']['title'], dash_list(sk['limits']['items']) + '<p class="note">%s</p>' % esc(sk['limits']['note']))}
  {block(SHARED['dont_use']['title'], dash_list(SHARED['dont_use']['items']) + '<p class="note">%s</p>' % esc(SHARED['dont_use']['note']))}
  {block(SHARED['scale']['title'], '<div class="scale">%s</div><p class="note">%s</p>' % (zones, esc(SHARED['scale']['note'])))}
  <div class="tool noprint" id="scale-live">
    <div class="tool-head"><span class="tool-title">Проверьте свой накал</span><span class="tool-sub">шкала 0–10</span></div>
    <div class="ctrls" style="gap:14px">
      <span class="rv" id="scale-value" style="font-size:34px;min-width:38px">5</span>
      <input id="scale-range" type="range" min="0" max="10" step="1" value="5" style="flex:1;min-width:170px" aria-label="Накал эмоции от 0 до 10">
      <button class="btn ghost sm" type="button" id="scale-save"><span>Отметить</span></button>
    </div>
    <p class="phase" id="scale-rec" style="margin:12px 0 0"></p>
  </div>
  {block(SHARED['chain']['title'], '<div class="chain">%s</div><p class="note">%s</p>' % ("".join(chain), esc(SHARED['chain']['note'])))}
  {pfoot(sk, 3)}
</section>""")

    # ------------------------------------------------------------------- шаги
    for i, st in enumerate(sk["steps"], start=1):
        extra = ""
        if st.get("safety"):
            extra += '<div class="box warn"><span class="lbl">Безопасность · обязательно</span>%s</div>' % esc(st["safety"])
        if st.get("safety_short"):
            extra += '<div class="box warn"><span class="lbl">Безопасность</span>%s</div>' % esc(st["safety_short"])
        if st.get("tip"):
            extra += '<div class="box tip"><span class="lbl">Подсказка</span>%s</div>' % esc(st["tip"])
        chips = "".join('<span class="chip">%s</span>' % esc(c) for c in st["chips"])
        kind = TOOL_KIND[sk["id"]][i - 1]
        auto = ' data-autostart="1"' if kind in AUTOSTART else ""
        P.append(f"""<section class="page reveal" id="step-{i}">
  {pnum('0%d' % (i + 2), 'Шаг %d из 4' % i)}
  <div class="step-head">
    <div class="bl">{st['letter']}</div>
    <div><div class="step-name">{esc(st['name'])}</div><div class="step-tag">{esc(st['tag'])}</div></div>
  </div>
  <div class="why"><b>Почему это работает.</b> {esc(st['why'])}</div>
  <h3>Как делать</h3>
  {how_list(st['how'])}
  <div class="chips">{chips}</div>
  <div class="box mistake"><span class="lbl">Частая ошибка</span>{esc(st['mistake'])}</div>
  {extra}
  <div class="tool noprint" data-tool="{kind}"{auto}></div>
  {pfoot(sk, i + 3)}
</section>""")

    # ------------------------------------------------- 07 тренировка и карточка
    fields = "".join(
        '<div class="fill"><div class="fl">%s</div>'
        '<textarea data-f="f%d" rows="2" aria-label="%s"></textarea></div>' % (esc(f), i, esc(f))
        for i, f in enumerate(SHARED["card"]["fields"], 1)
    )
    P.append(f"""<section class="page reveal" id="practice">
  {pnum('07', 'Тренировка и карточка')}
  <h2>Навык появляется до кризиса, а не в нём</h2>
  {block(SHARED['practice']['title'], dash_list(SHARED['practice']['items']) + '<p class="note">%s</p>' % esc(sk['practice_extra']))}
  <div class="block">
    <h3>{esc(SHARED['card']['title'])}<span class="saved" id="card-saved">сохранено</span></h3>
    <p class="note" style="margin:0 0 12px">{esc(SHARED['card']['note'])}</p>
    {fields}
    <div class="ctrls noprint" style="margin-top:4px">
      <button class="btn ghost sm" type="button" id="card-copy"><span>Скопировать карточку</span></button>
      <span class="tool-sub" style="margin:0">Записи хранятся только в этом браузере</span>
    </div>
  </div>
  <div class="log noprint">
    <div class="tool-head" style="margin-bottom:4px"><span class="tool-title">Дневник практики</span>
      <span class="tool-sub">накал до и после</span></div>
    <div id="log-list"></div>
    <div class="ctrls" style="margin-top:10px">
      <button class="btn ghost sm" type="button" id="log-copy"><span>Скопировать для терапевта</span></button>
      <button class="btn ghost sm" type="button" id="log-clear"><span>Очистить</span></button>
    </div>
  </div>
  <div class="safety"><b>Важно.</b> {esc(SHARED['safety'])}</div>
  <a class="xlink" href="{other['id']}.html">Следующий буклет серии: {other['acronym']} — {esc(other['tagline'])} {ARROW}</a>
  <div class="sources">{esc(SHARED['sources'][sk['id']])}</div>
  {pfoot(sk, 8)}
</section>""")
    return "\n".join(P)


def sos_panel(sk):
    steps = "".join(
        '<button class="sos-step" type="button" data-target="step-%d"><span class="bl">%s</span>'
        '<span><span class="nm">%s</span><br><span class="ds">%s</span></span></button>'
        % (i, st["letter"], esc(st["name"]), esc(st["tag"]))
        for i, st in enumerate(sk["steps"], 1)
    )
    return f"""<button class="btn sos-btn noprint" type="button" id="sos-open">Накрывает сейчас</button>
<div class="sos noprint" id="sos" role="dialog" aria-modal="true" aria-label="Быстрый доступ к шагам навыка">
  <div class="sos-wrap"><div class="sos-card">
    <button class="btn ghost sm sos-close" type="button" id="sos-close"><span>Закрыть</span></button>
    <div class="eyebrow">{sk['acronym']} · быстрый доступ</div>
    <h2 style="margin-top:8px">Откройте нужный шаг</h2>
    <p class="note" style="margin:0">Не обязательно проходить всё. Начните с того, что доступно сейчас.</p>
    <div class="sos-steps">{steps}</div>
    <div class="safety" style="margin-top:16px"><b>Если есть риск для жизни</b> — сразу звоните терапевту, в кризисную службу или 112.</div>
  </div></div>
</div>"""


PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" sizes="512x512" href="icon.png">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#F7F5F0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16191D" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">

<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}} — навык ДБТ · буклет</title>
<meta name="description" content="{{DESC}}">

<style>
{{FONTS}}
{{CSS}}
</style>
</head>
<body>
<nav class="nav noprint"><div class="nav-in">
<a class="nav-brand" href="index.html">Навыки ДБТ · Самопомощь<span>{{SERIES_SUB}}</span></a>
  <a class="tab {{ON_TRUD}}" href="trud.html">ТРУД</a>
  <a class="tab {{ON_STOP}}" href="stop.html">СТОП</a>
  <a class="tab {{ON_PC}}" href="pros_cons.html">ЗА/ПРОТИВ</a>
  <a class="tab icon" href="{{PDF}}" download>{{ICO_DOWN}}PDF</a>
  <button class="tab icon" type="button" id="print-btn">{{ICO_PRINT}}Печать</button>
</div><div class="progress"><i id="progress-bar"></i></div></nav>
<div class="wrap">
{{PAGES}}
</div>
{{SOS}}
<script>window.DBT_CONFIG={skill:"{{ID}}",acronym:"{{ACRONYM}}",latin:"{{LATIN}}"};</script>
<script>
{{JS}}
</script>
<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('./sw.js');}</script>
</body>
</html>
"""


def build(sk):
    css = (ASSETS / "app.css").read_text(encoding="utf-8")
    for k, v in sk["accent_dark"].items():
        css = css.replace("DARK_ACCENT_" + k.upper(), v)
    for k, v in sk["accent"].items():
        css = css.replace("ACCENT_" + k.upper(), v)

    html = PAGE
    repl = {
        "{{ON_PC}}": "on" if sk["id"] == "pros_cons" else "",
        "{{FONTS}}": font_css(),
        "{{CSS}}": css,
        "{{JS}}": (ASSETS / "app.js").read_text(encoding="utf-8"),
        "{{TITLE}}": sk["acronym"] + " (" + sk["latin"] + ")",
        "{{DESC}}": sk["tagline"] + ". Навык ДБТ, модуль «Стрессоустойчивость»: ситуации, шаги, практика.",
        "{{SERIES_SUB}}": SERIES_SUB,
        "{{ON_TRUD}}": "on" if sk["id"] == "trud" else "",
        "{{ON_STOP}}": "on" if sk["id"] == "stop" else "",
        "{{ON_PC}}": "on" if sk["id"] == "pros_cons" else "",
        "{{PDF}}": sk["id"] + ".pdf",
        "{{ICO_DOWN}}": ICO_DOWN,
        "{{ICO_PRINT}}": ICO_PRINT,
        "{{PAGES}}": sections(sk),
        "{{SOS}}": sos_panel(sk),
        "{{ID}}": sk["id"],
        "{{ACRONYM}}": sk["acronym"],
        "{{LATIN}}": sk["latin"],
    }
    for a, b in repl.items():
        html = html.replace(a, b)
    out = HERE / (sk["id"] + ".html")
    out.write_text(html, encoding="utf-8")
    return out, len(html)


# ------------------------------------------------------------------ индекс серии
INDEX = r"""<!doctype html>
<html lang="ru">
<head>
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" sizes="512x512" href="icon.png">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#F7F5F0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16191D" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{SERIES}} — Навыки выживания в кризисе</title>
<style>{{FONTS}}
{{CSS}}

.hub-title{font-family:'PT Serif',Georgia,serif;font-weight:700;font-size:clamp(32px,5vw,44px);line-height:1.12;margin:12px 0 0;color:var(--a-deep)}
.hub-title em{font-style:normal;color:#2E7E8B}
.hub-title b{font-weight:700;color:#B85838}
@media (prefers-color-scheme: dark){
  .hub-title em{color:#62B6C8}
  .hub-title b{color:#DF8E6B}
}
.hub-lead{font-size:16.5px;color:var(--muted);margin:16px 0 0;line-height:1.55}
.skill-list{display:flex;flex-direction:column;gap:12px;margin:24px 0 0}
.scard{display:grid;grid-template-columns:56px 1fr auto;align-items:center;gap:16px;padding:18px 20px;
  border-radius:16px;background:var(--c-tint);border:1px solid var(--c-mid);
  text-decoration:none;color:inherit;transition:.2s var(--ease)}
.scard:hover{transform:translateY(-2px);background:var(--c-soft);border-color:var(--c-main);box-shadow:0 8px 22px rgba(27,31,34,.06)}
.scard.trud{--c-main:#2E7E8B;--c-deep:#1F5C66;--c-mid:#B8D7DC;--c-soft:#E7F2F4;--c-tint:#F4FAFB}
.scard.stop{--c-main:#B85838;--c-deep:#8A3E24;--c-mid:#E4C0B2;--c-soft:#F7EAE4;--c-tint:#FCF7F4}
.scard.pc{--c-main:#4E7C59;--c-deep:#36593F;--c-mid:#C3DAC8;--c-soft:#EBF3ED;--c-tint:#F5F9F6}
@media (prefers-color-scheme: dark){
  .scard.trud{--c-main:#56ADC0;--c-deep:#A7DCE7;--c-mid:#2E4F58;--c-soft:#1F343A;--c-tint:#1A292E}
  .scard.stop{--c-main:#D98662;--c-deep:#F2C0AA;--c-mid:#5A382A;--c-soft:#3A241C;--c-tint:#2C1D17}
  .scard.pc{--c-main:#76AA83;--c-deep:#B8DBC0;--c-mid:#314B38;--c-soft:#223427;--c-tint:#1C2920}
}
.scard .em{width:52px;height:52px;color:var(--c-main);display:flex;align-items:center;justify-content:center}
.scard .em svg{width:46px;height:46px}
.scard-body h2{font-family:'PT Serif',Georgia,serif;font-size:24px;margin:0;color:var(--c-deep);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.scard-body .lt{font-family:'PT Sans',sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}
.scard-body .tg{font-size:15px;color:var(--ink);margin:4px 0 0}
.scard .go{font-size:13.5px;font-weight:700;color:var(--c-deep);display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.scard .go svg{width:15px;height:10px}
@media (max-width:600px){
  .scard{grid-template-columns:44px 1fr;padding:16px}
  .scard .go{grid-column:2;margin-top:4px}
}

.guide-box{margin:18px 0 0;border:1px solid var(--a-mid);border-radius:14px;background:var(--a-tint);overflow:hidden}
.guide-box summary{padding:14px 18px;font-weight:700;font-size:15px;color:var(--a-deep);cursor:pointer;list-style:none;
  display:flex;align-items:center;justify-content:space-between;user-select:none;transition:.18s var(--ease)}
.guide-box summary::-webkit-details-marker{display:none}
.guide-box summary:hover{background:var(--a-soft)}
.guide-box summary::after{content:"+";font-size:20px;font-weight:400;line-height:1;color:var(--a-main);transition:.2s var(--ease)}
.guide-box[open] summary{border-bottom:1px solid var(--a-mid);background:var(--a-soft)}
.guide-box[open] summary::after{transform:rotate(45deg)}
.guide-body{padding:16px 18px;font-size:14.5px;line-height:1.55;color:var(--ink)}
.guide-body h4{font-family:'PT Serif',Georgia,serif;font-size:16.5px;margin:14px 0 6px;color:var(--a-deep)}
.guide-body h4:first-child{margin-top:0}
.guide-body ul{margin:0;padding-left:18px}
.guide-body li{margin-bottom:5px}
</style>
</head>
<body>
<nav class="nav noprint"><div class="nav-in">
  <a class="nav-brand" href="index.html">Навыки ДБТ · Самопомощь<span>{{SERIES_SUB}}</span></a>
  <a class="tab" href="trud.html">ТРУД</a>
  <a class="tab" href="stop.html">СТОП</a>
  <a class="tab" href="pros_cons.html">ЗА/ПРОТИВ</a>
  <button class="tab icon" type="button" id="print-btn">{{ICO_PRINT}}Печать</button>
</div></nav>

<div class="wrap">
<section class="page cover">
  <div class="cover-top">
    <div>
      <div class="eyebrow">ДБТ · стрессоустойчивость</div>
      <div class="eyebrow q" style="margin-top:5px">{{SERIES_SUB}}</div>
    </div>
    <div class="seal" aria-hidden="true">
        <svg viewBox="0 0 64 64"><circle cx="32" cy="24" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="24" cy="38" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="40" cy="38" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>
    </div>
  </div>

  <h1 class="hub-title">Три навыка на случай, когда <em>накрывает</em> или когда <b>тянет действовать</b></h1>
  <p class="hub-lead" style="max-width:none">Буклеты по диалектической поведенческой терапии (ДБТ) Марши Линехан — для тех, кто сталкивается с сильными эмоциями и импульсами. Одинаковый дизайн, восемь страниц: ситуации, шаги, типичные ошибки и тренировка. Здесь также есть таймеры и карточка на кризис.</p>

    <div class="skill-list">
      <a class="scard trud" href="trud.html">
        <div class="em">{{EM_TRUD}}</div>
        <div class="scard-body">
          <h2>ТРУД <span class="lt">навык TIPP</span></h2>
          <div class="tg">Быстро снизить накал эмоции через тело (когда накал 8–10 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>

      <a class="scard stop" href="stop.html">
        <div class="em">{{EM_STOP}}</div>
        <div class="scard-body">
          <h2>СТОП <span class="lt">навык STOP</span></h2>
          <div class="tg">Пауза между импульсом и действием (когда накал 5–7 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>

      <a class="scard pc" href="pros_cons.html">
        <div class="em">{{EM_PC}}</div>
        <div class="scard-body">
          <h2>ЗА / ПРОТИВ <span class="lt">навык PROS &amp; CONS</span></h2>
          <div class="tg">Взвесить цену импульса, прежде чем действовать</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>
    </div>
  </section>

  <section class="page">
    <div class="sec-head"><span class="sec-num">01 · НАВИГАЦИЯ</span><h2>С чего начать прямо сейчас</h2></div>
    <div class="grid2">
      <div class="box">
        <h3>Когда накал 8–10 и думать нечем</h3>
        <p>Откройте <b>ТРУД</b>: 30 секунд холодной воды на лицо или интенсивное движение сбивают адреналин быстрее любых рассуждений. Только потом переходите к паузе.</p>
      </div>
      <div class="box">
        <h3>Когда есть секунда до срыва</h3>
        <p>Откройте <b>СТОП</b>, чтобы не написать и не сделать лишнего, а затем взвесьте последствия в <b>«За / против»</b>. Если уже трясёт — нажмите кнопку «Накрывает сейчас» внизу.</p>
      </div>
    </div>
    
    <details class="guide-box">
      <summary>Как пользоваться приложением и установить на телефон</summary>
      <div class="guide-body">
        <h4>1. Установка на главный экран (работает без интернета)</h4>
        <ul>
          <li><b>Android (Chrome):</b> нажмите три точки в правом верхнем углу → <b>«Установить приложение»</b>.</li>
          <li><b>iPhone (Safari):</b> нажмите кнопку <b>«Поделиться»</b> внизу → <b>«На экран „Домой“»</b>.</li>
          <li>После первого открытия все страницы, таймеры и PDF сохраняются в память телефона и работают в авиарежиме.</li>
        </ul>

        <h4>2. Подготовка в спокойный день</h4>
        <ul>
          <li>Внизу любой страницы навыка (раздел <b>07</b>) заполните <b>«Мою карточку на кризис»</b>: ваши сигналы, контакты поддержки и способы заземления.</li>
          <li>В буклете <b>«За / против»</b> заранее впишите аргументы для 1–2 частых импульсов — в стрессе останется только прочитать готовое.</li>
          <li>Все записи хранятся <b>только в памяти вашего телефона</b> и никуда не отправляются.</li>
        </ul>

        <h4>3. Когда накрывает прямо сейчас</h4>
        <ul>
          <li><b>Накал 8–10 (трясёт, трудно думать):</b> нажмите кнопку <b>«Накрывает сейчас»</b> внизу или откройте <b>ТРУД</b> — начните с холодной воды (таймер 30 сек) или нагрузки.</li>
          <li><b>Накал 5–7 (сильный импульс сорваться):</b> откройте <b>СТОП</b>, сделайте паузу и взвесьте последствия в <b>«За / против»</b>.</li>
          <li>После шага можно отметить накал в <b>«Дневнике практики»</b> или скопировать записи одной кнопкой для терапевта.</li>
        </ul>
      </div>
    </details>

    <div class="callout" style="margin-top:18px">
      <b>Важно.</b> {{SAFETY}}
    </div>
    <p style="font-size:12.5px;color:var(--muted);margin:16px 0 0;line-height:1.5">
      {{SRC_TRUD}}<br><br>{{SRC_STOP}}<br><br>{{SRC_PC}}
    </p>
  </section>
</div>

<script>document.getElementById("print-btn").addEventListener("click",function(){window.print();});</script>
<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('./sw.js');}</script>
</body>
</html>
"""




def build_index():
    css = (ASSETS / "app.css").read_text(encoding="utf-8")
    for k, v in {"main": "#8FA1AC", "deep": "#CBD5DC", "mid": "#343D44", "soft": "#262D33", "tint": "#1E2429"}.items():
        css = css.replace("DARK_ACCENT_" + k.upper(), v)
    for k, v in {"main": "#5A6B75", "deep": "#3E4C55", "mid": "#DCE2E5", "soft": "#EEF2F4", "tint": "#F6F8F9"}.items():
        css = css.replace("ACCENT_" + k.upper(), v)

    html = INDEX
    for a, b in {
        "{{FONTS}}": font_css(), "{{CSS}}": css, "{{SERIES}}": SERIES, "{{SERIES_SUB}}": SERIES_SUB,
        "{{EM_TRUD}}": EMBLEM["trud"], "{{EM_STOP}}": EMBLEM["stop"], "{{ARROW}}": ARROW,
        "{{EM_PC}}": EMBLEM["pros_cons"], "{{SRC_PC}}": esc(SHARED["sources"]["pros_cons"]),
        "{{ICO_PRINT}}": ICO_PRINT,
        "{{SAFETY}}": esc(SHARED["safety"]),
        "{{SRC_TRUD}}": esc(SHARED["sources"]["trud"]), "{{SRC_STOP}}": esc(SHARED["sources"]["stop"]),
    }.items():
        html = html.replace(a, b)
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    return out, len(html)



if __name__ == "__main__":
    for sid in ("trud", "stop", "pros_cons"):
        p, n = build(SKILLS[sid])
        print("built", p.name, round(n / 1024), "KB")
    p, n = build_index()
    print("built", p.name, round(n / 1024), "KB")
