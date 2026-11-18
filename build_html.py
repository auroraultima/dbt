# -*- coding: utf-8 -*-
"""Сборка экранных HTML-буклетов: self-contained (шрифты, стили, скрипты внутри файла)."""
import base64, hashlib, pathlib, re
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
    "problem_solving": '<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="22" fill="none" stroke="currentColor" stroke-width="2.4"/><polygon points="41,23 36,36 23,41 28,28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><circle cx="32" cy="32" r="2.2" fill="currentColor"/></svg>',
}

TOOL_KIND = {
    "trud": ["cold", "relax", "move", "breath"],
    "stop": ["freeze", "pause", "observe", "wise"],
    "pros_cons": ["pc1", "pc2", "pc3", "pc4"],
    "problem_solving": ["ps1", "ps2", "ps3", "ps4", "ps5", "ps6", "ps7"],
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
    total = len(sk["steps"]) + 4
    sub = sk.get("series_sub", SERIES_SUB)
    return ('<div class="pfoot printonly"><span>%s · %s</span><span>%d / %d</span></div>'
            % (sk["acronym"], sub, n, total))


def sections(sk):
    other = SKILLS[sk["other"]]
    P = []

    # ---------------------------------------------------------------- обложка
    total_pages = len(sk["steps"]) + 4
    series_main = sk.get("series", SERIES)
    series_sub = sk.get("series_sub", SERIES_SUB)
    is_ps = sk["id"] == "problem_solving"
    sos_cta = "" if is_ps else '<button class="btn" type="button" id="cover-sos">Накрывает прямо сейчас</button>'
    step_btn_cls = "btn" if is_ps else "btn ghost"

    rows = "".join(
        '<button class="arow" type="button" data-jump="step-%d"><span class="bl">%s</span>'
        '<span class="nm">%s</span><span class="hint">%s</span></button>' % (i, l, esc(n), esc(h))
        for i, (l, n, h) in enumerate(sk["letters"], 1)
    )
    P.append(f"""<section class="page cover reveal" id="cover">
  <div class="cover-top">
    <div><div class="eyebrow">{series_main}</div><div class="eyebrow q" style="margin-top:5px">{series_sub}</div></div>
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
    {sos_cta}
    <button class="{step_btn_cls}" type="button" data-jump="step-1">К шагам навыка</button>
    <a class="btn ghost" href="{sk['id']}.pdf" download>{ICO_DOWN}<span>Скачать PDF A5</span></a>
  </div>
  <div class="cover-foot">Карманная памятка для клиента · {total_pages} страниц · по навыкам М. Линехан</div>
  {pfoot(sk, 1)}
</section>""")


    # ------------------------------------------------------- 01 когда применять
    if is_ps:
        when_body = "".join(block(b["title"], dash_list(b["items"])) for b in sk["when_blocks"])
        goal_txt = sk["goal_text"]
    else:
        when_body = (
            block(SHARED["crisis"]["title"], dash_list(SHARED["crisis"]["items"]))
            + block(SHARED["use_when"]["title"], dash_list(SHARED["use_when"]["items"]))
        )
        goal_txt = "Пережить кризис, не сделав хуже. Не решить проблему и не стать спокойным навсегда — только не ухудшить."

    P.append(f"""<section class="page reveal" id="when">
  {pnum('01', 'Когда применять')}
  <h2>{esc(sk.get('when_h2', 'Сначала проверьте: это кризис?'))}</h2>
  {when_body}
  {block(sk['situations']['title'], dash_list(sk['situations']['items']))}
  <div class="box tip"><span class="lbl">Цель навыка</span>{esc(goal_txt)}</div>
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
    steps_total = len(sk["steps"])
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
  {pnum('%02d' % (i + 2), 'Шаг %d из %d' % (i, steps_total))}
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

    # ------------------------------------------------- тренировка и карточка
    last_sec_num = '%02d' % (len(sk["steps"]) + 3)
    last_page_num = len(sk["steps"]) + 4
    fields = "".join(
        '<div class="fill"><label class="fl" for="card-%s-f%d">%s</label>'
        '<textarea id="card-%s-f%d" name="f%d" data-f="f%d" rows="2"></textarea></div>'
        % (sk["id"], i, esc(f), sk["id"], i, i, i)
        for i, f in enumerate(SHARED["card"]["fields"], 1)
    )
    P.append(f"""<section class="page reveal" id="practice">
  {pnum(last_sec_num, 'Тренировка и карточка')}
  <h2>Навык появляется до кризиса, а не в нём</h2>
  {block(SHARED['practice']['title'], dash_list(SHARED['practice']['items']) + '<p class="note">%s</p>' % esc(sk['practice_extra']))}
  <div class="block">
    <h3>{esc(SHARED['card']['title'])}<span class="saved" id="card-saved">сохранено</span></h3>
    <p class="note" style="margin:0 0 12px">{esc(SHARED['card']['note'])}</p>
    {fields}
    <div class="ctrls noprint" style="margin-top:4px">
      <button class="btn ghost sm" type="button" id="card-copy"><span>Скопировать карточку</span></button>
      <button class="btn ghost sm" type="button" id="card-clear"><span>Очистить</span></button>
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
  <div class="ctrls noprint" style="margin-top:14px">
    <a class="btn ghost sm" href="{sk['id']}.pdf" download>{ICO_DOWN}<span>Скачать PDF A5</span></a>
    <button class="btn ghost sm" type="button" onclick="window.print()">{ICO_PRINT}<span>Печать</span></button>
  </div>
  <a class="xlink" href="{other['id']}.html">Следующий буклет серии: {other['acronym']} — {esc(other['tagline'])} {ARROW}</a>
  <div class="sources">{esc(SHARED['sources'][sk['id']])}</div>
  {pfoot(sk, last_page_num)}
</section>""")
    return "\n".join(P)


def sos_panel(sk):
    is_ps = sk["id"] == "problem_solving"
    btn_label = "Шаги разбора" if is_ps else "Накрывает сейчас"
    sub_note = (
        "Если накал выше 5 баллов — сначала откройте СТОП или ТРУД. Если вы спокойны — выберите нужный шаг:"
        if is_ps else
        "Не обязательно проходить всё. Начните с того, что доступно сейчас."
    )
    steps = "".join(
        '<button class="sos-step" type="button" data-target="step-%d"><span class="bl">%s</span>'
        '<span><span class="nm">%s</span><br><span class="ds">%s</span></span></button>'
        % (i, st["letter"], esc(st["name"]), esc(st["tag"]))
        for i, st in enumerate(sk["steps"], 1)
    )
    return f"""<button class="btn sos-btn noprint" type="button" id="sos-open">{btn_label}</button>
<div class="sos noprint" id="sos" role="dialog" aria-modal="true" aria-label="Быстрый доступ к шагам навыка">
  <div class="sos-wrap"><div class="sos-card">
    <button class="btn ghost sm sos-close" type="button" id="sos-close"><span>Закрыть</span></button>
    <div class="eyebrow">{sk['acronym']} · быстрый доступ</div>
    <h2 style="margin-top:8px">Откройте нужный шаг</h2>
    <p class="note" style="margin:0">{sub_note}</p>
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
  <a class="tab {{ON_PS}}" href="problem_solving.html">РЕШЕНИЕ</a>
  <a class="tab" href="diary.html">ДНЕВНИК</a>
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
<script>if('serviceWorker' in navigator && /^https?:/.test(location.protocol)){navigator.serviceWorker.register('./sw.js');}</script>
<script data-goatcounter="https://drwg.goatcounter.com/count" async src="https://zgo.at"></script>
</body>
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
        "{{SERIES_SUB}}": sk.get("series_sub", SERIES_SUB),
        "{{ON_TRUD}}": "on" if sk["id"] == "trud" else "",
        "{{ON_STOP}}": "on" if sk["id"] == "stop" else "",
        "{{ON_PC}}": "on" if sk["id"] == "pros_cons" else "",
        "{{ON_PS}}": "on" if sk["id"] == "problem_solving" else "",
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
<title>Навыки ДБТ · Самопомощь в кризисе и разбор ситуаций</title>
<style>{{FONTS}}
{{CSS}}
.hub-title{font-family:'PT Serif',Georgia,serif;font-weight:700;font-size:clamp(30px,4.8vw,42px);line-height:1.14;margin:12px 0 0;color:var(--a-deep)}
.hub-title em{font-style:normal;color:#2E7E8B}
.hub-title b{font-weight:700;color:#B85838}
.hub-title span{color:#46648C}
@media (prefers-color-scheme: dark){
  .hub-title em{color:#62B6C8}
  .hub-title b{color:#DF8E6B}
  .hub-title span{color:#89B0E0}
}
.hub-lead{font-size:16px;color:var(--muted);margin:14px 0 0;line-height:1.55}
.skill-list{display:grid;grid-auto-rows:1fr;gap:12px;margin:22px 0 0}
.scard{display:grid;grid-template-columns:56px 1fr auto;align-items:center;gap:16px;padding:18px 20px;height:100%;
  border-radius:16px;background:var(--c-tint);border:1px solid var(--c-mid);
  text-decoration:none;color:inherit;transition:.2s var(--ease)}
.scard:hover{transform:translateY(-2px);background:var(--c-soft);border-color:var(--c-main);box-shadow:0 8px 22px rgba(27,31,34,.06)}
.scard.trud{--c-main:#2E7E8B;--c-deep:#1F5C66;--c-mid:#B8D7DC;--c-soft:#E7F2F4;--c-tint:#F4FAFB}
.scard.stop{--c-main:#B85838;--c-deep:#8A3E24;--c-mid:#E4C0B2;--c-soft:#F7EAE4;--c-tint:#FCF7F4}
.scard.pc{--c-main:#4E7C59;--c-deep:#36593F;--c-mid:#C3DAC8;--c-soft:#EBF3ED;--c-tint:#F5F9F6}
.scard.ps{--c-main:#46648C;--c-deep:#2F4666;--c-mid:#C2D1E5;--c-soft:#EBF1F8;--c-tint:#F5F8FC}
@media (prefers-color-scheme: dark){
  .scard.trud{--c-main:#56ADC0;--c-deep:#A7DCE7;--c-mid:#2E4F58;--c-soft:#1F343A;--c-tint:#1A292E}
  .scard.stop{--c-main:#D98662;--c-deep:#F2C0AA;--c-mid:#5A382A;--c-soft:#3A241C;--c-tint:#2C1D17}
  .scard.pc{--c-main:#76AA83;--c-deep:#B8DBC0;--c-mid:#314B38;--c-soft:#223427;--c-tint:#1C2920}
  .scard.ps{--c-main:#799ECE;--c-deep:#B8D1F0;--c-mid:#31435C;--c-soft:#212E40;--c-tint:#1A2432}
}
.scard .em{width:52px;height:52px;color:var(--c-main);display:flex;align-items:center;justify-content:center}
.scard .em svg{width:46px;height:46px}
.scard-body h2{font-family:'PT Serif',Georgia,serif;font-size:23px;margin:0;color:var(--c-deep);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.scard-body .lt{font-family:'PT Sans',sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}
.scard-body .tg{font-size:15px;color:var(--ink);margin:4px 0 0}
.scard .go{font-size:13.5px;font-weight:700;color:var(--c-deep);display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.scard .go svg{width:15px;height:10px}
@media (max-width:600px){
  .scard{grid-template-columns:44px 1fr;padding:16px}
  .scard .go{grid-column:2;margin-top:4px}
}
.route-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 0}
.route-grid .box{margin:0;background:var(--surface);border:1px solid var(--line)}
.route-grid .badge-lvl{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  padding:3px 9px;border-radius:999px;background:var(--a-soft);color:var(--a-deep);margin-bottom:8px}
.route-grid h3{font-family:'PT Serif',Georgia,serif;font-size:17px;letter-spacing:0;text-transform:none;color:var(--ink);margin:0 0 6px}
.route-grid p{font-size:14px;color:var(--ink-2);margin:0}
@media (max-width:680px){.route-grid{grid-template-columns:1fr}}
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
.guide-body li{margin-bottom:6px}
.src-list{margin:8px 0 0;padding-left:18px}
.src-list li{margin-bottom:4px}
</style>
</head>
<body>
<nav class="nav noprint"><div class="nav-in">
  <a class="nav-brand" href="index.html">Навыки ДБТ · Самопомощь<span>Стрессоустойчивость и регуляция</span></a>
  <a class="tab" href="trud.html">ТРУД</a>
  <a class="tab" href="stop.html">СТОП</a>
  <a class="tab" href="pros_cons.html">ЗА/ПРОТИВ</a>
  <a class="tab" href="problem_solving.html">РЕШЕНИЕ</a>
  <a class="tab" href="diary.html">ДНЕВНИК</a>
  <button class="tab icon" type="button" id="print-btn">{{ICO_PRINT}}Печать</button>
</div></nav>
<div class="wrap">
<section class="page cover">
  <div class="cover-top">
    <div>
      <div class="eyebrow">ДБТ · Практикум самопомощи</div>
      <div class="eyebrow q" style="margin-top:5px">Стрессоустойчивость и эмоциональная регуляция</div>
    </div>
    <div class="seal" aria-hidden="true">
        <svg viewBox="0 0 64 64"><circle cx="32" cy="24" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="24" cy="38" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="40" cy="38" r="13" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>
    </div>
  </div>
  <h1 class="hub-title">Четыре навыка: от <em>острого кризиса</em> и <b>импульса</b> до <span>решения проблемы</span></h1>
  <p class="hub-lead" style="max-width:none">Интерактивные буклеты по диалектической поведенческой терапии (ДБТ) Марши Линехан. Единая цепочка шагов: сначала снизить накал через тело и удержаться от срыва, а когда вернётся мудрый разум — спокойно изменить саму ситуацию. Внутри есть таймеры, рабочие матрицы, единый локальный дневник с поиском и версии для печати A5.</p>
    <div class="skill-list">
      <a class="scard trud" href="trud.html">
        <div class="em">{{EM_TRUD}}</div>
        <div class="scard-body">
          <h2>ТРУД <span class="lt">навык TIPP · 8 стр.</span></h2>
          <div class="tg">Быстро снизить накал эмоции через тело (когда накал 8–10 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>
      <a class="scard stop" href="stop.html">
        <div class="em">{{EM_STOP}}</div>
        <div class="scard-body">
          <h2>СТОП <span class="lt">навык STOP · 8 стр.</span></h2>
          <div class="tg">Пауза между импульсом и действием (когда накал 5–7 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>
      <a class="scard pc" href="pros_cons.html">
        <div class="em">{{EM_PC}}</div>
        <div class="scard-body">
          <h2>ЗА / ПРОТИВ <span class="lt">навык PROS &amp; CONS · 8 стр.</span></h2>
          <div class="tg">Взвесить цену импульса и сдержанности (когда накал 5–7 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>
      <a class="scard ps" href="problem_solving.html">
        <div class="em">{{EM_PS}}</div>
        <div class="scard-body">
          <h2>РЕШЕНИЕ ПРОБЛЕМЫ <span class="lt">навык PROBLEM SOLVING · 11 стр.</span></h2>
          <div class="tg">7 шагов по М. Линехан: изменить ситуацию, когда кризис позади (0–4 из 10)</div>
        </div>
        <span class="go">Открыть {{ARROW}}</span>
      </a>
    </div>
  </section>

  <section class="page">
    <p class="pnum">01 · Навигация по накалу</p>
    <h2>С чего начать прямо сейчас</h2>
    <div class="route-grid">
      <div class="box">
        <span class="badge-lvl">Накал 8–10</span>
        <h3>Сначала тело</h3>
        <p>Откройте <b>ТРУД</b>: 30 секунд холодной воды на лицо, нагрузка или длинный выдох сбивают физиологический шторм быстрее любых слов.</p>
      </div>
      <div class="box">
        <span class="badge-lvl">Накал 5–7</span>
        <h3>Пауза и выбор</h3>
        <p>Откройте <b>СТОП</b>, чтобы не написать и не сделать лишнего, а затем заполните матрицу <b>«За / против»</b>, чтобы увидеть цену срыва.</p>
      </div>
      <div class="box">
        <span class="badge-lvl">Накал 0–4</span>
        <h3>Разбор ситуации</h3>
        <p>Когда вы вернулись в мудрый разум, откройте <b>«Решение проблемы»</b> и пройдите 7 шагов от проверки фактов до первого действия.</p>
      </div>
    </div>
    <details class="guide-box">
      <summary>Как пользоваться приложением, дневником и PDF-буклетами</summary>
      <div class="guide-body">
        <h4>1. Офлайн-доступ на телефоне (работает без интернета)</h4>
        <ul>
          <li><b>Android (Chrome):</b> нажмите три точки в правом верхнем углу → <b>«Установить приложение»</b>.</li>
          <li><b>iPhone (Safari):</b> нажмите кнопку <b>«Поделиться»</b> внизу → <b>«На экран „Домой“»</b>.</li>
          <li>После первого открытия все страницы, тренажёры, дневник и PDF-файлы сохраняются в память телефона.</li>
        </ul>
        <h4>2. Интерактивные инструменты внутри буклетов</h4>
        <ul>
          <li><b>ТРУД и СТОП:</b> встроенные таймеры со <b>звуковым сопровождением</b> для холодной воды (30 сек), дыхания, мышечной релаксации и паузы, а также тренажёр «Факт или мысль». Чтобы запустить или поставить таймер на паузу, достаточно нажать прямо на большой круг циферблата.</li>
          <li><b>«За / против»:</b> интерактивная матрица из 4 квадратов с кнопкой <b>«Сохранить в дневник»</b> (после сохранения поля автоматически очищаются).</li>
          <li><b>«Решение проблемы»:</b> пошаговый конструктор из 7 шагов Линехан (проверка фактов, цель, мозговой штурм, план действий, возврат к шагу 5 при неудаче и сохранение разбора в дневник).</li>
          <li><b>Персональная карточка:</b> в конце каждого буклета есть <b>«Моя карточка на кризис»</b>, которая остаётся под рукой и копируется одной кнопкой.</li>
        </ul>
        <h4>3. Единая вкладка «Дневник» и резервные копии</h4>
        <ul>
          <li>Во вкладке <b>«Дневник»</b> в верхнем меню собираются все ваши тренировки, отметки накала и полные разборы, сгруппированные по дням.</li>
          <li>В дневнике работает <b>поиск по тексту</b>, выбор конкретной <b>даты</b>, <b>фильтры по навыкам</b> и выбор отдельных записей галочками.</li>
          <li>Все данные хранятся <b>только локально на вашем устройстве</b>. Вы можете скопировать выбранные записи, скачать отчёт для терапевта (<b>.txt</b>) или полную резервную копию базы (<b>.json</b>).</li>
        </ul>
        <h4>4. Печать и карманные буклеты A5</h4>
        <ul>
          <li>В шапке каждого навыка есть кнопка <b>«PDF»</b> (готовый макет формата A5 на 8 или 11 страниц) и кнопка <b>«Печать»</b>.</li>
        </ul>
      </div>
    </details>

    <div class="safety" style="margin-top:18px">
      <b>Важно.</b> {{SAFETY}}
    </div>
    <div class="sources">
      <b>Источники · M. M. Linehan. DBT Skills Training Handouts and Worksheets, 2nd ed. (2015):</b>
      <ul class="src-list">
        <li><b>ТРУД (TIPP):</b> Distress Tolerance Handouts 3, 6, 6b — изменение химии тела через температуру, релаксацию, нагрузку и дыхание.</li>
        <li><b>СТОП (STOP):</b> Distress Tolerance Handouts 3, 4, 5 — остановка импульсивного действия и возвращение в мудрый разум.</li>
        <li><b>«За / против» (Pros &amp; Cons):</b> Distress Tolerance Handouts 3, 5 — взвешивание краткосрочных и долгосрочных последствий.</li>
        <li><b>Решение проблемы (Problem Solving):</b> Emotion Regulation Handout 12 — 7 шагов изменения ситуации, когда эмоция оправдана фактами.</li>
      </ul>
    </div>
  </section>
</div>
<script>if('serviceWorker' in navigator && /^https?:/.test(location.protocol)){navigator.serviceWorker.register('./sw.js');}</script>
<script data-goatcounter="https://drwg.goatcounter.com/count" async src="https://zgo.at"></script>
</body>
<script>if('serviceWorker' in navigator && /^https?:/.test(location.protocol)){navigator.serviceWorker.register('./sw.js');}</script>
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
        "{{FONTS}}": font_css(),
        "{{CSS}}": css,
        "{{EM_TRUD}}": EMBLEM["trud"],
        "{{EM_STOP}}": EMBLEM["stop"],
        "{{EM_PC}}": EMBLEM["pros_cons"],
        "{{EM_PS}}": EMBLEM["problem_solving"],
        "{{ARROW}}": ARROW,
        "{{ICO_PRINT}}": ICO_PRINT,
        "{{SAFETY}}": esc(SHARED["safety"]),
    }.items():
        html = html.replace(a, b)
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    return out, len(html)


DIARY = r"""<!doctype html>
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
<title>Дневник практики — Навыки ДБТ</title>
<style>{{FONTS}}
{{CSS}}
</style>
</head>
<body>
<nav class="nav noprint"><div class="nav-in">
  <a class="nav-brand" href="index.html">Навыки ДБТ · Самопомощь<span>Дневник практики и база записей</span></a>
  <a class="tab" href="trud.html">ТРУД</a>
  <a class="tab" href="stop.html">СТОП</a>
  <a class="tab" href="pros_cons.html">ЗА/ПРОТИВ</a>
  <a class="tab" href="problem_solving.html">РЕШЕНИЕ</a>
  <a class="tab on" href="diary.html">ДНЕВНИК</a>
  <button class="tab icon" type="button" id="print-btn">{{ICO_PRINT}}Печать</button>
</div></nav>

<div class="wrap" id="diary-app">
  <section class="page cover">
    <div class="cover-top">
      <div>
        <div class="eyebrow">ДБТ · Локальная база практики</div>
        <div class="eyebrow q" style="margin-top:5px">Хранится только на вашем устройстве</div>
      </div>
    </div>
    <h1 style="font-size:clamp(32px,6vw,46px)">ДНЕВНИК ПРАКТИКИ</h1>
    <p class="lead" style="margin-top:12px">Единая хронология всех ваших тренировок, отметок накала, матриц «За / против» и разборов проблем по дням.</p>

    <div class="db-stats">
      <div class="db-stat"><div class="num" id="db-stat-total">0</div><div class="lbl">Всего записей в базе</div></div>
      <div class="db-stat"><div class="num" id="db-stat-week">0</div><div class="lbl">За последние 7 дней</div></div>
      <div class="db-stat"><div class="num" id="db-stat-drop">—</div><div class="lbl">Среднее снижение накала</div></div>
    </div>

    <div class="ctrls noprint" style="margin-top:18px">
      <button class="btn sm" type="button" id="db-exp-txt">{{ICO_DOWN}}<span>Скачать отчёт (.txt)</span></button>
      <button class="btn ghost sm" type="button" id="db-exp-json">{{ICO_DOWN}}<span>Резервная копия (.json)</span></button>
      <button class="btn ghost sm" type="button" id="db-imp-json"><span>Загрузить из .json</span></button>
      <input type="file" id="db-imp-file" accept=".json,application/json" style="display:none">
    </div>
  </section>

  <section class="page">
    <p class="pnum">01 · Поиск и фильтры</p>
    <div class="db-bar noprint">
      <input type="search" class="db-search" id="db-q" placeholder="Поиск по тексту записей, целям, мыслям..." aria-label="Поиск по тексту">
      <input type="date" class="db-date" id="db-date" aria-label="Фильтр по дате">
      <button class="btn ghost sm" type="button" id="db-date-clear"><span>Сбросить дату</span></button>
    </div>
    <div class="db-chips noprint">
      <button type="button" class="db-chip on" data-skill="all">Все навыки</button>
      <button type="button" class="db-chip" data-skill="trud">ТРУД</button>
      <button type="button" class="db-chip" data-skill="stop">СТОП</button>
      <button type="button" class="db-chip" data-skill="pros_cons">ЗА / ПРОТИВ</button>
      <button type="button" class="db-chip" data-skill="problem_solving">РЕШЕНИЕ ПРОБЛЕМЫ</button>
    </div>

        <div class="db-sel-bar noprint" id="db-sel-bar">
      <span class="db-sel-cnt" id="db-sel-cnt">Выбрано: 0</span>
      <button class="btn sm" type="button" id="db-sel-copy"><span>Скопировать выбранные</span></button>
      <button class="btn ghost sm" type="button" id="db-sel-txt">{{ICO_DOWN}}<span>Скачать (.txt)</span></button>
      <button class="btn ghost sm" type="button" id="db-sel-all"><span>Выбрать все</span></button>
      <button class="btn ghost sm" type="button" id="db-sel-none"><span>Снять</span></button>
    </div>

    <div id="db-list"></div>


    <div class="safety" style="margin-top:20px">
      <b>Приватность.</b> Все записи хранятся исключительно в локальной памяти вашего браузера и никуда не отправляются. Рекомендуем периодически скачивать резервную копию (<b>.json</b>).
    </div>
  </section>
</div>

<script>window.DBT_CONFIG={skill:"diary",acronym:"Дневник",latin:"DIARY"};</script>
<script>
{{JS}}
</script>
<script>if('serviceWorker' in navigator && /^https?:/.test(location.protocol)){navigator.serviceWorker.register('./sw.js');}</script>
<script data-goatcounter="https://drwg.goatcounter.com/count" async src="https://zgo.at"></script>
</body>
</body>
</html>
"""


def build_diary():
    css = (ASSETS / "app.css").read_text(encoding="utf-8")
    for k, v in {"main": "#8FA1AC", "deep": "#CBD5DC", "mid": "#343D44", "soft": "#262D33", "tint": "#1E2429"}.items():
        css = css.replace("DARK_ACCENT_" + k.upper(), v)
    for k, v in {"main": "#5A6B75", "deep": "#3E4C55", "mid": "#DCE2E5", "soft": "#EEF2F4", "tint": "#F6F8F9"}.items():
        css = css.replace("ACCENT_" + k.upper(), v)

    html = DIARY
    for a, b in {
        "{{FONTS}}": font_css(),
        "{{CSS}}": css,
        "{{JS}}": (ASSETS / "app.js").read_text(encoding="utf-8"),
        "{{ICO_PRINT}}": ICO_PRINT,
        "{{ICO_DOWN}}": ICO_DOWN,
    }.items():
        html = html.replace(a, b)
    out = HERE / "diary.html"
    out.write_text(html, encoding="utf-8")
    return out, len(html)


def bump_sw():
    sw_path = HERE / "sw.js"
    if not sw_path.exists():
        return
    h = hashlib.md5()
    for fn in ("index.html", "diary.html", "trud.html", "stop.html", "pros_cons.html", "problem_solving.html",
               "trud.pdf", "stop.pdf", "pros_cons.pdf", "problem_solving.pdf", "manifest.json", "icon.png", "favicon.png"):
        fp = HERE / fn
        if fp.exists():
            h.update(fp.read_bytes())
    ver = "dbt-offline-" + h.hexdigest()[:8]
    txt = sw_path.read_text(encoding="utf-8")
    new_txt = re.sub(r"const CACHE = '[^']+';", f"const CACHE = '{ver}';", txt, count=1)
    if new_txt != txt:
        sw_path.write_text(new_txt, encoding="utf-8")
        print("updated sw.js ->", ver)


if __name__ == "__main__":
    for sid in ("trud", "stop", "pros_cons", "problem_solving"):
        p, n = build(SKILLS[sid])
        print("built", p.name, round(n / 1024), "KB")
    p, n = build_index()
    print("built", p.name, round(n / 1024), "KB")
    p, n = build_diary()
    print("built", p.name, round(n / 1024), "KB")
    bump_sw()
