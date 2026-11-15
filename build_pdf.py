# -*- coding: utf-8 -*-
"""Сборка PDF-буклетов A5 (8 страниц) в том же дизайне, что и HTML."""
import pathlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from content import SKILLS, SHARED, SERIES, SERIES_SUB

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"

for name, fn in [
    ("PTSans", "PTSans-Regular"), ("PTSans-Bold", "PTSans-Bold"),
    ("PTSans-Italic", "PTSans-Italic"), ("PTSerif", "PTSerif-Regular"),
    ("PTSerif-Bold", "PTSerif-Bold"),
]:
    pdfmetrics.registerFont(TTFont(name, str(ASSETS / (fn + ".ttf"))))
pdfmetrics.registerFontFamily("PTSans", normal="PTSans", bold="PTSans-Bold",
                              italic="PTSans-Italic", boldItalic="PTSans-Bold")
pdfmetrics.registerFontFamily("PTSerif", normal="PTSerif", bold="PTSerif-Bold",
                              italic="PTSerif", boldItalic="PTSerif-Bold")

PW, PH = A5
ML, MR, MT, MB = 12 * mm, 12 * mm, 11 * mm, 11 * mm
CW = PW - ML - MR            # ширина контентной полосы
TOP = PH - MT
BOTTOM = MB + 16             # нижняя граница (место для колонтитула)

INK = HexColor("#23282D")
MUTED = HexColor("#6C7580")
LINE = HexColor("#E8E2D8")
NEUTRAL = HexColor("#F7F4EF")
NEUTRAL_EDGE = HexColor("#D9D2C6")
NEUTRAL_LBL = HexColor("#8A8375")
DOT = HexColor("#C9C2B6")
WHITE = HexColor("#FFFFFF")


def xesc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Book:
    def __init__(self, sk, path):
        self.sk = sk
        a = sk["accent"]
        self.main = HexColor(a["main"])
        self.deep = HexColor(a["deep"])
        self.mid = HexColor(a["mid"])
        self.soft = HexColor(a["soft"])
        self.tint = HexColor(a["tint"])
        self.c = canvas.Canvas(str(path), pagesize=A5)
        self.c.setTitle("%s (%s) — навык ДБТ" % (sk["acronym"], sk["latin"]))
        self.c.setAuthor("Буклет серии «Навыки ДБТ при ПРЛ»")
        self.c.setSubject("Стрессоустойчивость: навыки выживания в кризисе. По М. Линехан.")
        self.page = 0
        self.warn = []
        self.y = TOP

    # ------------------------------------------------------------ утилиты
    def new_page(self):
        if self.page:
            self.footer()
            self.c.showPage()
        self.page += 1
        self.y = TOP

    def footer(self):
        c = self.c
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(ML, MB + 9, PW - MR, MB + 9)
        c.setFont("PTSans", 6.8)
        c.setFillColor(MUTED)
        c.drawString(ML, MB, "%s · %s" % (self.sk["acronym"], SERIES_SUB))
        c.drawRightString(PW - MR, MB, "%d / 8" % self.page)

    def check(self, need, tag):
        if self.y - need < BOTTOM:
            self.warn.append("стр.%d %s: не хватает %.1f pt" % (self.page, tag, BOTTOM - (self.y - need)))

    def style(self, size, leading, font="PTSans", color=INK, align=0, space=0):
        return ParagraphStyle("s", fontName=font, fontSize=size, leading=leading,
                              textColor=color, alignment=align, spaceAfter=space,
                              allowWidows=0, allowOrphans=0)

    def flow(self, text, st, x=None, w=None, gap=0):
        x = ML if x is None else x
        w = CW if w is None else w
        p = Paragraph(text, st)
        _, h = p.wrapOn(self.c, w, 10000)
        self.check(h, "текст")
        p.drawOn(self.c, x, self.y - h)
        self.y -= h + gap
        return h

    def label(self, text, color=None, size=8, gap=5, x=None, w=None, rule=False):
        """Мелкий разряженный заголовок (аналог h3 / .pnum)."""
        x = ML if x is None else x
        color = self.deep if color is None else color
        c = self.c
        c.saveState()
        t = c.beginText(x, self.y - size)
        t.setFont("PTSans-Bold", size)
        t.setFillColor(color)
        t.setCharSpace(0.75)
        t.textOut(text.upper())
        c.drawText(t)
        c.restoreState()
        if rule:
            tw = pdfmetrics.stringWidth(text.upper(), "PTSans-Bold", size) + 0.75 * len(text)
            c.setStrokeColor(LINE)
            c.setLineWidth(0.5)
            c.line(x + tw + 7, self.y - size * 0.42, ML + CW, self.y - size * 0.42)
        self.y -= size + gap

    def h2(self, text, gap=8):
        self.flow(xesc(text), self.style(15.5, 18.5, "PTSerif-Bold"), gap=gap)

    def note(self, text, gap=0, x=None, w=None):
        self.flow(xesc(text), self.style(8.7, 11.6, "PTSans-Italic", MUTED), x=x, w=w, gap=gap)

    def dash_list(self, items, gap=7, size=9.6, leading=13.4):
        st = self.style(size, leading)
        for it in items:
            p = Paragraph(xesc(it), st)
            _, h = p.wrapOn(self.c, CW - 13, 10000)
            self.check(h, "список")
            self.c.setStrokeColor(self.mid)
            self.c.setLineWidth(1.6)
            self.c.setLineCap(1)
            self.c.line(ML + 1.5, self.y - leading * 0.52, ML + 8, self.y - leading * 0.52)
            p.drawOn(self.c, ML + 13, self.y - h)
            self.y -= h + 3.2
        self.y += 3.2
        self.y -= gap

    def how_list(self, items, gap=6, size=9.6, leading=13.4):
        st = self.style(size, leading)
        d = 14.5
        for i, it in enumerate(items, 1):
            p = Paragraph(xesc(it), st)
            _, h = p.wrapOn(self.c, CW - 22, 10000)
            self.check(h, "шаги")
            self.c.setFillColor(self.soft)
            self.c.setStrokeColor(self.mid)
            self.c.setLineWidth(0.6)
            self.c.circle(ML + d / 2, self.y - d / 2 - 0.5, d / 2, stroke=1, fill=1)
            self.c.setFillColor(self.deep)
            self.c.setFont("PTSans-Bold", 7.8)
            self.c.drawCentredString(ML + d / 2, self.y - d / 2 - 3.1, str(i))
            p.drawOn(self.c, ML + 22, self.y - h)
            self.y -= max(h, d) + 5
        self.y += 5
        self.y -= gap

    def box(self, label, text, kind="mistake", gap=8):
        if kind == "mistake":
            bg, edge, lbl = NEUTRAL, NEUTRAL_EDGE, NEUTRAL_LBL
        elif kind == "warn":
            bg, edge, lbl = self.soft, self.main, self.deep
        else:
            bg, edge, lbl = WHITE, self.mid, self.main
        padx, pady = 10, 8.5
        w = CW - 2 * padx - (3 if kind != "tip" else 0)
        st = self.style(9, 12.3)
        p = Paragraph(xesc(text), st)
        _, h = p.wrapOn(self.c, w, 10000)
        lblh = 11
        total = h + lblh + 2 * pady
        self.check(total, "бокс " + kind)
        y0 = self.y - total
        c = self.c
        if kind == "tip":
            c.setFillColor(WHITE)
            c.setStrokeColor(edge)
            c.setLineWidth(0.7)
            c.setDash(2.2, 2.2)
            c.roundRect(ML, y0, CW, total, 8, stroke=1, fill=1)
            c.setDash()
            tx = ML + padx
        else:
            c.setFillColor(bg)
            c.setStrokeColor(bg)
            c.setLineWidth(0.5)
            c.roundRect(ML, y0, CW, total, 8, stroke=1, fill=1)
            c.setFillColor(edge)
            c.rect(ML, y0 + 3, 2.6, total - 6, stroke=0, fill=1)
            tx = ML + padx + 3
        c.saveState()
        t = c.beginText(tx, self.y - pady - 7.6)
        t.setFont("PTSans-Bold", 7.4)
        t.setFillColor(lbl)
        t.setCharSpace(0.8)
        t.textOut(label.upper())
        c.drawText(t)
        c.restoreState()
        p.drawOn(self.c, tx, y0 + pady)
        self.y = y0 - gap

    def arrow(self, x, y, w=11, color=None, lw=1.2):
        """Векторная стрелка (в PT Sans нет глифа U+2192)."""
        c = self.c
        c.saveState()
        c.setStrokeColor(self.mid if color is None else color)
        c.setLineWidth(lw)
        c.setLineCap(1)
        c.setLineJoin(1)
        c.line(x, y, x + w, y)
        p = c.beginPath()
        p.moveTo(x + w - 3.2, y + 2.6)
        p.lineTo(x + w, y)
        p.lineTo(x + w - 3.2, y - 2.6)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()

    def chips(self, items, gap=8):
        c = self.c
        x = ML
        h = 17
        self.check(h, "чипсы")
        for it in items:
            tw = pdfmetrics.stringWidth(it, "PTSans-Bold", 8.5)
            w = tw + 20
            c.setFillColor(self.tint)
            c.setStrokeColor(self.mid)
            c.setLineWidth(0.6)
            c.roundRect(x, self.y - h, w, h, h / 2, stroke=1, fill=1)
            c.setFillColor(self.deep)
            c.setFont("PTSans-Bold", 8.5)
            c.drawString(x + 10, self.y - h + 5.4, it)
            x += w + 6
        self.y -= h + gap

    def badge(self, letter, size, x, y_top, fs):
        c = self.c
        c.setFillColor(self.soft)
        c.setStrokeColor(self.mid)
        c.setLineWidth(0.7)
        c.roundRect(x, y_top - size, size, size, size * 0.28, stroke=1, fill=1)
        c.setFillColor(self.deep)
        c.setFont("PTSerif-Bold", fs)
        c.drawCentredString(x + size / 2, y_top - size / 2 - fs * 0.35, letter)

    def emblem(self, x, y_top, s):
        """Эмблема обложки: капля (ТРУД) / восьмиугольник (СТОП)."""
        c = self.c
        c.saveState()
        c.translate(x, y_top - s)
        k = s / 64.0
        c.scale(k, k)
        c.setStrokeColor(self.main)
        c.setFillColor(self.main)
        c.setLineWidth(2.4)
        c.setLineJoin(1)
        c.setLineCap(1)
        if self.sk["id"] == "trud":
            p = c.beginPath()
            p.moveTo(32, 58)
            p.curveTo(41, 46, 48, 38, 48, 30)
            p.curveTo(48, 21.2, 40.8, 14, 32, 14)
            p.curveTo(23.2, 14, 16, 21.2, 16, 30)
            p.curveTo(16, 38, 23, 46, 32, 58)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            c.setLineWidth(2.2)
            p = c.beginPath()
            p.moveTo(20, 26)
            p.curveTo(24, 29, 28, 23, 32, 26)
            p.curveTo(36, 29, 40, 23, 44, 26)
            c.drawPath(p, stroke=1, fill=0)
            p = c.beginPath()
            p.moveTo(22, 18)
            p.curveTo(26, 21, 30, 15, 34, 18)
            c.drawPath(p, stroke=1, fill=0)
        elif self.sk["id"] == "pros_cons":
            c.line(32, 54, 32, 10)
            c.line(18, 10, 46, 10)
            c.line(12, 42, 52, 42)
            c.line(12, 42, 6, 28)
            c.line(12, 42, 18, 28)
            c.line(6, 28, 18, 28)
            c.line(52, 42, 46, 28)
            c.line(52, 42, 58, 28)
            c.line(46, 28, 58, 28)

        else:
            p = c.beginPath()
            pts = [(22, 58), (42, 58), (58, 42), (58, 22), (42, 6), (22, 6), (6, 22), (6, 42)]
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            c.setLineWidth(2.6)
            c.line(22, 32, 42, 32)
            c.circle(32, 42, 2.6, stroke=0, fill=1)
            c.circle(32, 22, 2.6, stroke=0, fill=1)
        c.restoreState()

    # ------------------------------------------------------------ страницы
    def cover(self):
        sk = self.sk
        self.new_page()
        c = self.c
        self.label(SERIES, self.main, size=7.6, gap=3)
        self.label(SERIES_SUB, MUTED, size=7.6, gap=0)
        self.emblem(PW - MR - 44, TOP + 2, 44)
        self.y -= 22
        self.flow(xesc(sk["title"]), self.style(46, 46, "PTSerif-Bold", self.deep), gap=6)
        self.label("навык " + sk["latin"], MUTED, size=8.4, gap=14)
        self.flow(xesc(sk["tagline"]), self.style(13, 16.5, "PTSerif"), gap=5)
        self.flow(xesc(sk["cover_note"]), self.style(9.5, 12.6, "PTSans-Italic", MUTED), gap=14)

        # таблица расшифровки
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(ML, self.y, PW - MR, self.y)
        self.y -= 0
        for letter, name, hint in sk["letters"]:
            rowh = 40
            self.check(rowh, "акроним")
            self.badge(letter, 28, ML, self.y - 6, 15.5)
            c.setFillColor(INK)
            c.setFont("PTSans-Bold", 11.5)
            c.drawString(ML + 40, self.y - 22, name)
            c.setFillColor(MUTED)
            c.setFont("PTSans", 9)
            c.drawRightString(PW - MR, self.y - 22, hint)
            self.y -= rowh
            c.setStrokeColor(LINE)
            c.line(ML, self.y, PW - MR, self.y)
        self.y -= 14
        self.flow(xesc(sk["lead"]), self.style(10.5, 14.6, color=HexColor("#3A4249")), gap=12)
        self.box("Как открывать буклет", sk["cover_callout"], kind="tip", gap=10)
        self.flow("Карманная памятка для клиента · 8 страниц · по навыкам М. Линехан",
                  self.style(8, 11, color=MUTED), gap=0)

    def when(self):
        self.new_page()
        self.label("01 · Когда применять", self.main, size=7.5, gap=8, rule=True)
        self.h2("Сначала проверьте: это кризис?", gap=10)
        for key in ("crisis", "use_when"):
            self.label(SHARED[key]["title"], size=8, gap=5)
            self.dash_list(SHARED[key]["items"], gap=10)
        self.label(self.sk["situations"]["title"], size=8, gap=5)
        self.dash_list(self.sk["situations"]["items"], gap=8)
        self.box("Цель навыка",
                 "Пережить кризис, не сделав хуже. Не решить проблему и не стать спокойным навсегда — только не ухудшить.",
                 kind="tip", gap=0)

    def limits(self):
        sk = self.sk
        self.new_page()
        self.label("02 · Границы навыка", self.main, size=7.5, gap=8, rule=True)
        self.h2("Что навык делает и чего не делает", gap=10)
        self.label(sk["limits"]["title"], size=8, gap=5)
        self.dash_list(sk["limits"]["items"], gap=4)
        self.note(sk["limits"]["note"], gap=11)
        self.label(SHARED["dont_use"]["title"], size=8, gap=5)
        self.dash_list(SHARED["dont_use"]["items"], gap=4)
        self.note(SHARED["dont_use"]["note"], gap=12)

        # шкала
        self.label(SHARED["scale"]["title"], size=8, gap=6)
        gap = 6
        zw = (CW - 2 * gap) / 3
        pads = 9
        inner = zw - 2 * pads
        cells = []
        for rng, zt, zd in SHARED["scale"]["zones"]:
            pr = Paragraph(xesc(zd), self.style(8.5, 11.2, color=MUTED))
            _, hh = pr.wrapOn(self.c, inner, 10000)
            cells.append((rng, zt, pr, hh))
        zh = max(14 + 4 + 11 + 3 + c[3] for c in cells) + 2 * pads
        self.check(zh, "шкала")
        bgs = [WHITE, self.tint, self.soft]
        for i, (rng, zt, pr, hh) in enumerate(cells):
            x = ML + i * (zw + gap)
            y0 = self.y - zh
            self.c.setFillColor(bgs[i])
            self.c.setStrokeColor(self.mid)
            self.c.setLineWidth(0.6)
            self.c.roundRect(x, y0, zw, zh, 8, stroke=1, fill=1)
            self.c.setFillColor(self.deep)
            self.c.setFont("PTSerif-Bold", 14)
            self.c.drawString(x + pads, self.y - pads - 12, rng)
            self.c.setFillColor(INK)
            self.c.setFont("PTSans-Bold", 8.5)
            self.c.drawString(x + pads, self.y - pads - 26, zt)
            pr.drawOn(self.c, x + pads, y0 + pads)
        self.y -= zh + 6
        self.note(SHARED["scale"]["note"], gap=12)

        # цепочка
        self.label(SHARED["chain"]["title"], size=8, gap=7)
        x = ML
        h = 18
        self.check(h, "цепочка")
        steps = SHARED["chain"]["steps"]
        for i, s in enumerate(steps):
            tw = pdfmetrics.stringWidth(s, "PTSans-Bold", 8.5)
            w = tw + 20
            if x + w > ML + CW:
                x = ML
                self.y -= h + 5
            on = s == sk["acronym"]
            self.c.setFillColor(self.main if on else WHITE)
            self.c.setStrokeColor(self.main if on else LINE)
            self.c.setLineWidth(0.6)
            self.c.roundRect(x, self.y - h, w, h, h / 2, stroke=1, fill=1)
            self.c.setFillColor(WHITE if on else MUTED)
            self.c.setFont("PTSans-Bold", 8.5)
            self.c.drawString(x + 10, self.y - h + 5.6, s)
            x += w
            if i < len(steps) - 1:
                self.arrow(x + 5, self.y - h / 2, w=10)
                x += 20
        self.y -= h + 6
        self.note(SHARED["chain"]["note"], gap=0)

    def step(self, i, st):
        self.new_page()
        self.label("0%d · Шаг %d из 4" % (i + 2, i), self.main, size=7.5, gap=10, rule=True)
        head_h = 42
        self.check(head_h, "заголовок шага")
        self.badge(st["letter"], 40, ML, self.y, 22)
        x = ML + 54
        w = CW - 54
        self.y -= 2
        self.flow(xesc(st["name"]), self.style(18, 20, "PTSerif-Bold"), x=x, w=w, gap=3)
        self.flow(xesc(st["tag"]), self.style(9.5, 12.4, "PTSans-Italic", MUTED), x=x, w=w, gap=0)
        self.y = min(self.y, TOP - 10 - head_h - 12)
        self.y -= 12

        p = Paragraph("<b>Почему это работает.</b> " + xesc(st["why"]), self.style(9.3, 12.8))
        padx, pady = 10, 8.5
        _, h = p.wrapOn(self.c, CW - 2 * padx, 10000)
        total = h + 2 * pady
        self.check(total, "зачем")
        self.c.setFillColor(self.tint)
        self.c.setStrokeColor(self.mid)
        self.c.setLineWidth(0.6)
        self.c.roundRect(ML, self.y - total, CW, total, 8, stroke=1, fill=1)
        p.drawOn(self.c, ML + padx, self.y - total + pady)
        self.y -= total + 11

        self.label("Как делать", size=8, gap=6)
        self.how_list(st["how"], gap=8)
        self.chips(st["chips"], gap=9)
        self.box("Частая ошибка", st["mistake"], kind="mistake", gap=8)
        if st.get("safety"):
            self.box("Безопасность · обязательно", st["safety"], kind="warn", gap=8)
        if st.get("safety_short"):
            self.box("Безопасность", st["safety_short"], kind="warn", gap=8)
        if st.get("tip"):
            self.box("Подсказка", st["tip"], kind="tip", gap=0)

    def practice(self):
        sk = self.sk
        self.new_page()
        self.label("07 · Тренировка и карточка", self.main, size=7.5, gap=8, rule=True)
        self.h2("Навык появляется до кризиса, а не в нём", gap=8)
        self.label(SHARED["practice"]["title"], size=8, gap=5)
        self.dash_list(SHARED["practice"]["items"], gap=3, leading=13.0)
        self.note(sk["practice_extra"], gap=10)

        self.label(SHARED["card"]["title"], size=8, gap=5)
        self.note(SHARED["card"]["note"], gap=8)
        for f in SHARED["card"]["fields"]:
            self.check(36, "карточка")
            self.c.setFillColor(self.deep)
            self.c.setFont("PTSans-Bold", 8.7)
            self.c.drawString(ML, self.y - 8.7, f)
            self.y -= 13.5
            self.c.setStrokeColor(DOT)
            self.c.setLineWidth(0.6)
            self.c.setDash(1, 2)
        for _ in range(2):
            self.c.line(ML, self.y, PW - MR, self.y)
            self.y -= 10
            self.c.setDash()
            self.y -= 2.5
        self.y -= 4
        self.box("Важно", SHARED["safety"], kind="warn", gap=9)
        other = SKILLS[sk["other"]]
        txt = "Следующий буклет серии: <b>%s</b> — %s" % (other["acronym"], xesc(other["tagline"]))
        plain = "Следующий буклет серии: %s — %s" % (other["acronym"], other["tagline"])
        self.flow(txt, self.style(9.2, 12.4, color=self.deep), gap=8)
        tw = pdfmetrics.stringWidth(plain, "PTSans", 9.2)
        self.arrow(ML + tw + 7, self.y + 12.4 + 3.2, w=10, color=self.deep)
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.5)
        self.c.line(ML, self.y, PW - MR, self.y)
        self.y -= 8
        self.flow(xesc(SHARED["sources"][sk["id"]]), self.style(7.6, 9.6, color=MUTED), gap=0)

    def build(self):
        self.cover()
        self.when()
        self.limits()
        for i, st in enumerate(self.sk["steps"], 1):
            self.step(i, st)
        self.practice()
        self.footer()
        self.c.save()
        return self.warn


if __name__ == "__main__":
    for sid in ("trud", "stop", "pros_cons"):
        b = Book(SKILLS[sid], HERE / (sid + ".pdf"))
        w = b.build()
        print(sid + ".pdf:", b.page, "страниц", "| предупреждения:", w if w else "нет")
