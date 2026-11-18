/* ============================================================
   Интерактивная практика к буклетам ДБТ (ТРУД / СТОП)
   Vanilla JS, без зависимостей. Всё локально, ничего не уходит наружу.
   ============================================================ */
(function () {
  "use strict";
  var CFG = window.DBT_CONFIG || { skill: "trud" };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var mmss = function (s) { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ":" + pad(s % 60); };
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- безопасное хранилище (может быть недоступно в песочнице) ---------- */
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };

  /* ---------- тост ---------- */
  var toastEl, toastTimer;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; toastEl.setAttribute("role", "status"); document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add("on");
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove("on"); }, 2600);
  }

  /* ---------- звуковой движок (Web Audio API, без внешних файлов) ---------- */
  var SND = (function () {
    var ctx = null;
    var enabled = store.get("dbt-sound", true);
    function getCtx() {
      if (!enabled) return null;
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      if (!ctx) ctx = new AC();
      if (ctx.state === "suspended") ctx.resume().catch(function () {});
      return ctx;
    }
    function tone(freq, dur, vol, delay) {
      var c = getCtx(); if (!c) return;
      var t0 = c.currentTime + (delay || 0);
      var osc = c.createOscillator();
      var gain = c.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, t0);
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.exponentialRampToValueAtTime(vol || 0.14, t0 + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
      osc.connect(gain);
      gain.connect(c.destination);
      osc.start(t0);
      osc.stop(t0 + dur + 0.02);
    }
    return {
      isOn: function () { return enabled; },
      toggle: function () {
        enabled = !enabled;
        store.set("dbt-sound", enabled);
        if (enabled) tone(528, 0.35, 0.1);
        return enabled;
      },
      unlock: function () { getCtx(); },
      start: function () { tone(440, 0.3, 0.1); },
      tick: function () { tone(392, 0.18, 0.07); },
      inhale: function () { tone(396, 0.55, 0.11); },
      exhale: function () { tone(528, 0.75, 0.11); },
      done: function () { tone(528, 0.7, 0.15, 0); tone(660, 0.95, 0.14, 0.22); }
    };
  })();

  function soundToggleBtn() {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "btn ghost sm";
    b.style.marginLeft = "auto";
    function paint() {
      b.innerHTML = "<span>" + (SND.isOn() ? "Звук: вкл" : "Звук: выкл") + "</span>";
      b.style.opacity = SND.isOn() ? "1" : "0.65";
    }
    b.addEventListener("click", function () { SND.toggle(); paint(); });
    paint();
    return b;
  }

  /* ---------- иконки ---------- */
  var ICO = {
    play: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M4 2.6v10.8c0 .5.6.8 1 .5l8.2-5.4c.4-.3.4-.8 0-1L5 2.1c-.4-.3-1 0-1 .5z"/></svg>',
    pause: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><rect x="3.5" y="2.5" width="3.4" height="11" rx="1.2"/><rect x="9.1" y="2.5" width="3.4" height="11" rx="1.2"/></svg>',
    reset: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M13 8a5 5 0 1 1-1.6-3.7"/><path d="M13.2 2.2v3.1h-3.1"/></svg>',
    arrow: '<svg viewBox="0 0 16 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 5h13"/><path d="M10.6 1.6 14 5l-3.4 3.4"/></svg>',
    copy: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="9" rx="1.6"/><path d="M10.5 3.5v-.4a1.6 1.6 0 0 0-1.6-1.6H4.1A1.6 1.6 0 0 0 2.5 3.1v6.3c0 .9.7 1.6 1.6 1.6h.4"/></svg>',
    print: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4.5 6V2.5h7V6"/><rect x="2.5" y="6" width="11" height="5" rx="1.4"/><path d="M4.5 9.5h7v4h-7z"/></svg>',
    down: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M8 2.5v9"/><path d="M4.4 8.2 8 11.8l3.6-3.6"/><path d="M2.8 13.5h10.4"/></svg>'
  };
  function btn(label, cls, icon) {
    var b = document.createElement("button");
    b.type = "button"; b.className = "btn " + (cls || "");
    b.innerHTML = (icon ? ICO[icon] : "") + "<span>" + label + "</span>";
    return b;
  }

  /* ---------- единая БД дневника (dbt-journal-v1) ---------- */
  var DBKEY = "dbt-journal-v1";
  var SKILL_NAMES = { trud: "ТРУД", stop: "СТОП", pros_cons: "ЗА/ПРОТИВ", problem_solving: "РЕШЕНИЕ" };
  if (navigator.storage && navigator.storage.persist) { navigator.storage.persist().catch(function () {}); }

  function loadDB() {
    var db = store.get(DBKEY, null);
    if (!db) {
      db = [];
      ["trud", "stop", "pros_cons", "problem_solving"].forEach(function (sk) {
        var old = store.get("dbt-log-" + sk, []);
        old.forEach(function (item, idx) {
          db.push({
            id: item.ts + "-" + sk + "-" + idx,
            ts: item.ts,
            skill: sk,
            skillName: SKILL_NAMES[sk] || sk,
            label: item.label || "",
            v: typeof item.v === "number" ? item.v : null,
            prev: typeof item.prev === "number" ? item.prev : null,
            extra: item.extra || "",
            details: item.details || ""
          });
        });
      });
      db.sort(function (a, b) { return a.ts - b.ts; });
      if (db.length) store.set(DBKEY, db);
    }
    return db;
  }
  function saveDB(db) {
    if (db.length > 2000) db = db.slice(-2000);
    store.set(DBKEY, db);
  }
  function lastRating(db) {
    for (var i = db.length - 1; i >= 0; i--) {
      if (db[i].skill === CFG.skill && typeof db[i].v === "number") return db[i].v;
    }
    return null;
  }
  function addLog(label, v, extra, details) {
    var db = loadDB();
    var prev = lastRating(db);
    db.push({
      id: Date.now() + "-" + Math.random().toString(36).slice(2, 6),
      ts: Date.now(),
      skill: CFG.skill,
      skillName: SKILL_NAMES[CFG.skill] || CFG.acronym || CFG.skill,
      label: label,
      v: typeof v === "number" ? v : null,
      prev: prev,
      extra: extra || "",
      details: details || ""
    });
    saveDB(db);
    renderLog();
  }
  function renderLog() {
    var box = $("#log-list"); if (!box) return;
    box.innerHTML = "";
    var list = loadDB().filter(function (e) { return e.skill === CFG.skill; });
    if (!list.length) { box.innerHTML = '<p class="log-empty">Пока пусто. Отметьте накал или нажмите «Сохранить в дневник» — все записи появятся здесь и на вкладке «Дневник».</p>'; return; }
    list.slice(-30).reverse().forEach(function (e) {
      var li = document.createElement("li");
      var d = new Date(e.ts);
      var delta = "";
      if (typeof e.v === "number") delta = (typeof e.prev === "number" ? e.prev + " → " : "") + e.v;
      li.innerHTML = '<span class="t">' + pad(d.getHours()) + ":" + pad(d.getMinutes()) + "</span>" +
        "<span>" + e.label + (e.extra ? " · " + e.extra : "") + "</span>" +
        (delta ? '<span class="d">' + delta + "</span>" : "");
      box.appendChild(li);
    });
  }
  function logText() {
    var list = loadDB().filter(function (e) { return e.skill === CFG.skill; });
    if (!list.length) return "";
    var lines = ["Дневник практики · навык " + CFG.acronym + " (" + CFG.latin + ")"];
    list.forEach(function (e) {
      var d = new Date(e.ts);
      lines.push(pad(d.getDate()) + "." + pad(d.getMonth() + 1) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) +
        " — " + e.label + (e.extra ? " (" + e.extra + ")" : "") +
        (typeof e.v === "number" ? ", накал " + (typeof e.prev === "number" ? e.prev + "→" : "") + e.v : "") +
        (e.details ? "\n" + e.details : ""));
    });
    return lines.join("\n");
  }

  function copyText(txt) {
    if (!txt) { toast("Пока нечего копировать"); return; }
    var done = function () { toast("Скопировано — можно отправить терапевту"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(done, function () { fallbackCopy(txt, done); });
    } else fallbackCopy(txt, done);
  }
  function fallbackCopy(txt, done) {
    var ta = document.createElement("textarea");
    ta.value = txt; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    var ok = false; try { ok = document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
    if (ok) done(); else { window.prompt("Скопируйте текст вручную:", txt); }
  }

  /* ---------- строка оценки накала ---------- */
  function rateRow(label, onsave) {
    var wrap = document.createElement("div"); wrap.className = "rate";
    var l = document.createElement("span"); l.className = "rl"; l.textContent = "Накал сейчас";
    var r = document.createElement("input"); r.type = "range"; r.min = 0; r.max = 10; r.step = 1;
    r.value = 5; r.setAttribute("aria-label", "Накал эмоции от 0 до 10");
    var v = document.createElement("span"); v.className = "rv"; v.textContent = "5";
    r.addEventListener("input", function () { v.textContent = r.value; });
    var b = btn("Записать", "ghost sm");
    b.addEventListener("click", function () { onsave(parseInt(r.value, 10), label); toast("Записано в дневник практики"); });
    wrap.appendChild(l); wrap.appendChild(r); wrap.appendChild(v); wrap.appendChild(b);
    return wrap;
  }

  /* ---------- циферблат ---------- */
  function makeDial(unit) {
    var d = document.createElement("div"); d.className = "dial";
    var R = 54, C = 2 * Math.PI * R;
    d.innerHTML = '<svg viewBox="0 0 132 132" aria-hidden="true">' +
      '<circle class="trk" cx="66" cy="66" r="' + R + '"/>' +
      '<circle class="bar" cx="66" cy="66" r="' + R + '" stroke-dasharray="' + C.toFixed(1) + '" stroke-dashoffset="0"/></svg>' +
      '<div class="mid"><span class="val" role="timer" aria-live="off">0</span><span class="unit">' + unit + "</span></div>";
    var bar = $(".bar", d), val = $(".val", d);
    return {
      el: d,
      set: function (text, frac) { val.textContent = text; bar.style.strokeDashoffset = (C * (1 - clamp(frac, 0, 1))).toFixed(1); }
    };
  }

  /* ---------- степпер ---------- */
  function stepper(value, min, max, step, fmt, onchange) {
    var w = document.createElement("div"); w.className = "stepper";
    var minus = document.createElement("button"); minus.type = "button"; minus.textContent = "−"; minus.setAttribute("aria-label", "Уменьшить");
    var plus = document.createElement("button"); plus.type = "button"; plus.textContent = "+"; plus.setAttribute("aria-label", "Увеличить");
    var sv = document.createElement("span"); sv.className = "sv";
    function paint() { sv.textContent = fmt(value); minus.disabled = value <= min; plus.disabled = value >= max; }
    function set(nv) { value = clamp(nv, min, max); paint(); onchange(value); }
    minus.addEventListener("click", function () { set(value - step); });
    plus.addEventListener("click", function () { set(value + step); });
    w.appendChild(minus); w.appendChild(sv); w.appendChild(plus); paint();
    return { el: w, get: function () { return value; }, set: set };
  }

  /* ---------- обратный отсчёт ---------- */
  function Countdown(opts) {
    var self = this;
    this.total = opts.seconds; this.remain = opts.seconds; this.running = false; this.raf = null;
    this.onTick = opts.onTick; this.onDone = opts.onDone; this.onState = opts.onState || function () {};
    this._loop = function () {
      if (!self.running) return;
      var now = Date.now();
      self.remain = Math.max(0, (self.endAt - now) / 1000);
      self.onTick(self.remain, self.total);
      if (self.remain <= 0) { self.running = false; self.onState("done"); self.onDone(); return; }
      self.raf = requestAnimationFrame(self._loop);
    };
  }
  Countdown.prototype.start = function () {
    if (this.running) return;
    if (this.remain <= 0) this.remain = this.total;
    this.endAt = Date.now() + this.remain * 1000; this.running = true; this.onState("run");
    this.raf = requestAnimationFrame(this._loop);
  };
  Countdown.prototype.pause = function () {
    if (!this.running) return;
    this.running = false; cancelAnimationFrame(this.raf);
    this.remain = Math.max(0, (this.endAt - Date.now()) / 1000); this.onState("pause");
  };
  Countdown.prototype.reset = function (sec) {
    this.running = false; cancelAnimationFrame(this.raf);
    if (sec != null) this.total = sec;
    this.remain = this.total; this.onTick(this.remain, this.total); this.onState("idle");
  };

  /* ---------- каркас инструмента-таймера ---------- */
  function timerTool(host, cfg) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">' + cfg.title + '</span><span class="tool-sub">' + cfg.sub + "</span></div>" +
      '<div class="tool-body"></div>';
    $(".tool-head", host).appendChild(soundToggleBtn());
    var body = $(".tool-body", host);
    var dial = makeDial(cfg.unit || "сек");
    var side = document.createElement("div"); side.className = "tool-side";
    var phase = document.createElement("div"); phase.className = "phase q"; phase.setAttribute("aria-live", "polite");
    var hint = document.createElement("div"); hint.className = "tool-hint"; hint.textContent = cfg.hint;
    var ctrls = document.createElement("div"); ctrls.className = "ctrls";
    side.appendChild(phase); side.appendChild(hint);
    if (cfg.pick) side.appendChild(cfg.pick.el);
    side.appendChild(ctrls);
    body.appendChild(dial.el); body.appendChild(side);

    var st = stepper(cfg.seconds, cfg.min, cfg.max, cfg.step, cfg.fmt, function (v) { cd.reset(v); paintIdle(); });
    var start = btn("Старт", "", "play"), reset = btn("Сброс", "ghost", "reset");
    ctrls.appendChild(st.el); ctrls.appendChild(start); ctrls.appendChild(reset);
    if (cfg.extraCtrls) cfg.extraCtrls(ctrls);

    function paintIdle() { phase.className = "phase q"; phase.textContent = cfg.idle; dial.set(cfg.fmt(cd.total), 1); }
    var lastTick = 0;
    var cd = new Countdown({
      seconds: cfg.seconds,
      onTick: function (r, t) {
        dial.set(cfg.fmt(r), r / t);
        var ceilR = Math.ceil(r);
        if (cfg.countdownBeep && ceilR <= 3 && ceilR >= 1 && ceilR !== lastTick) {
          lastTick = ceilR;
          SND.tick();
        }
        if (cfg.onTick) cfg.onTick(r, t, phase);
      },
      onDone: function () {
        lastTick = 0;
        SND.done();
        phase.className = "phase"; phase.textContent = cfg.done;
        start.innerHTML = ICO.play + "<span>Ещё раз</span>";
        if (cfg.onDoneExtra) cfg.onDoneExtra();
        toast(cfg.toast || "Готово. Оцените накал 0–10.");
      },
      onState: function (s) {
        if (s === "run") { lastTick = 0; SND.start(); phase.className = "phase"; phase.textContent = cfg.run; start.innerHTML = ICO.pause + "<span>Пауза</span>"; }
        if (s === "pause") { start.innerHTML = ICO.play + "<span>Продолжить</span>"; }
        if (s === "idle") { start.innerHTML = ICO.play + "<span>Старт</span>"; }
      }
    });
    function toggleRun() { cd.running ? cd.pause() : cd.start(); }
    start.addEventListener("click", toggleRun);
    dial.el.setAttribute("role", "button");
    dial.el.setAttribute("tabindex", "0");
    dial.el.setAttribute("aria-label", "Запустить или поставить таймер на паузу");
    dial.el.addEventListener("click", toggleRun);
    dial.el.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggleRun(); }
    });
    reset.addEventListener("click", function () { cd.reset(st.get()); paintIdle(); if (cfg.onReset) cfg.onReset(); });
    paintIdle();
    host.appendChild(rateRow(cfg.logLabel, function (v) { addLog(cfg.logLabel, v, cfg.pick ? cfg.pick.value() : ""); }));
    return { cd: cd, start: function () { cd.start(); }, dial: dial, phase: phase };
  }

  /* ---------- Т: таймер холода ---------- */
  function toolCold(host) {
    timerTool(host, {
      title: "Практика · холод на лицо", sub: "шаг Т", unit: "сек", countdownBeep: true,
      seconds: 30, min: 10, max: 30, step: 5, fmt: function (v) { return Math.ceil(v); },
      idle: "Приготовьте воду, задержите дыхание — и старт.",
      run: "Держите лицо в воде. Дыхание задержано.",
      done: "Готово. Поднимите голову, вдохните, оцените накал.",
      hint: "Вода выше 10 °C. Нет миски — холодный пакет на глаза и скулы. Есть ограничения по здоровью — сначала врач.",
      logLabel: "ТРУД · Т (холод)", toast: "30 секунд прошли. Вдохните и оцените накал."
    });
  }

  /* ---------- У: разрядка ---------- */
  function toolMove(host) {
    var acts = ["Быстрая ходьба", "Бег", "Прыжки", "Лестница", "Приседания", "Работа с весом", "Мяч"];
    var chosen = acts[0];
    var pick = document.createElement("div"); pick.className = "pick";
    acts.forEach(function (a, i) {
      var b = document.createElement("button"); b.type = "button"; b.textContent = a;
      b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      b.addEventListener("click", function () {
        chosen = a; $$("button", pick).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      });
      pick.appendChild(b);
    });
    timerTool(host, {
      title: "Практика · разрядка", sub: "шаг У", unit: "мин:сек",
      seconds: 600, min: 60, max: 1200, step: 60, fmt: mmss,
      idle: "Выберите нагрузку и начните, когда будете готовы.",
      run: "Двигайтесь интенсивно. Цель — истратить энергию.",
      done: "Стоп. Оцените накал; остаток снимите дыханием (Д).",
      hint: "Интенсивно и недолго. Не до истощения и не через боль — нагрузка не наказание телу.",
      pick: { el: pick, value: function () { return chosen; } },
      logLabel: "ТРУД · У (нагрузка)", toast: "Нагрузка завершена. Оцените накал."
    });
  }

  /* ---------- Д: дыхательный ритм ---------- */
  function toolBreath(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · дыхательный ритм</span><span class="tool-sub">шаг Д</span></div>' +
      '<div class="tool-body"></div>';
	$(".tool-head", host).appendChild(soundToggleBtn());
    var body = $(".tool-body", host);
    var breath = document.createElement("div"); breath.className = "breath";
    breath.innerHTML = '<span class="ring"></span><span class="orb"></span><span class="cnt">5</span>';
    var orb = $(".orb", breath), cnt = $(".cnt", breath);
    var side = document.createElement("div"); side.className = "tool-side";
    var phase = document.createElement("div"); phase.className = "phase q"; phase.setAttribute("aria-live", "polite");
    phase.textContent = "Вдох носом в живот, выдох длиннее вдоха.";
    var hint = document.createElement("div"); hint.className = "tool-hint";
    hint.textContent = "Ориентир: 5–6 дыханий в минуту. Подберите свой счёт: выдох всегда длиннее вдоха.";
    var ctrls = document.createElement("div"); ctrls.className = "ctrls";
    var meta = document.createElement("div"); meta.className = "tool-hint"; meta.style.margin = "10px 0 0";
    side.appendChild(phase); side.appendChild(hint); side.appendChild(ctrls); side.appendChild(meta);
    body.appendChild(breath); body.appendChild(side);

    var inhale = 5, exhale = 7, limit = 120;
    var running = false, phaseName = "in", phaseLeft = inhale, cycles = 0, elapsed = 0, last = 0, raf = null;

    var sIn = stepper(inhale, 3, 8, 1, function (v) { return "вдох " + v; }, function (v) {
      inhale = v; if (exhale <= inhale) { exhale = inhale + 2; sEx.set(exhale); toast("Выдох должен быть длиннее вдоха"); }
      if (!running) { phaseLeft = inhale; paintIdle(); }
    });
    var sEx = stepper(exhale, 4, 10, 1, function (v) { return "выдох " + v; }, function (v) {
      exhale = v; if (exhale <= inhale) { inhale = Math.max(3, exhale - 2); sIn.set(inhale); toast("Вдох укорочен: выдох длиннее"); }
      if (!running) paintIdle();
    });
    var sMin = stepper(limit, 60, 300, 60, function (v) { return Math.round(v / 60) + " мин"; }, function (v) { limit = v; if (!running) paintMeta(); });
    var start = btn("Старт", "", "play"), reset = btn("Сброс", "ghost", "reset");
    ctrls.appendChild(sIn.el); ctrls.appendChild(sEx.el); ctrls.appendChild(sMin.el); ctrls.appendChild(start); ctrls.appendChild(reset);

    function setOrb(scale, sec) {
      orb.style.transitionDuration = (reduced ? 0.001 : sec) + "s";
      orb.style.transform = "scale(" + scale + ")";
    }
    function paintIdle() { cnt.textContent = inhale; setOrb(0.62, .4); phase.className = "phase q"; phase.textContent = "Вдох носом в живот, выдох длиннее вдоха."; paintMeta(); }
    function paintMeta() { meta.textContent = "Циклов: " + cycles + " · осталось " + mmss(Math.max(0, limit - elapsed)); }
    function enter(name) {
      phaseName = name;
      if (name === "in") { phaseLeft = inhale; phase.className = "phase"; phase.textContent = "Вдох… живот поднимается"; setOrb(1, inhale); SND.inhale(); }
      else { phaseLeft = exhale; phase.className = "phase"; phase.textContent = "Выдох… отпустите плечи"; setOrb(0.62, exhale); SND.exhale(); }
    }
    function loop(ts) {
      if (!running) return;
      if (!last) last = ts;
      var dt = Math.min(.25, (ts - last) / 1000); last = ts;
      phaseLeft -= dt; elapsed += dt;
      if (phaseLeft <= 0) { if (phaseName === "ex") { cycles++; } enter(phaseName === "in" ? "ex" : "in"); }
      cnt.textContent = Math.max(1, Math.ceil(phaseLeft));
      paintMeta();
      if (elapsed >= limit) { stop(true); return; }
      raf = requestAnimationFrame(loop);
    }
    function stop(done) {
      running = false; cancelAnimationFrame(raf); last = 0;
      start.innerHTML = ICO.play + "<span>" + (done ? "Ещё раз" : "Продолжить") + "</span>";
      if (done) { phase.className = "phase"; phase.textContent = "Готово. Оцените накал 0–10."; setOrb(.62, .6); toast("Дыхание завершено. Оцените накал."); SND.done();}
    }
    function toggleBreath() {
      if (running) { stop(false); return; }
      if (elapsed >= limit) { elapsed = 0; cycles = 0; }
      running = true; last = 0; start.innerHTML = ICO.pause + "<span>Пауза</span>";
      enter(phaseLeft > 0 && phaseName ? phaseName : "in"); raf = requestAnimationFrame(loop);
    }
    start.addEventListener("click", toggleBreath);
    breath.setAttribute("role", "button");
    breath.setAttribute("tabindex", "0");
    breath.setAttribute("aria-label", "Запустить или поставить дыхательный ритм на паузу");
    breath.addEventListener("click", toggleBreath);
    breath.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggleBreath(); }
    });
    reset.addEventListener("click", function () {
      running = false; cancelAnimationFrame(raf); last = 0; elapsed = 0; cycles = 0; phaseName = "in"; phaseLeft = inhale;
      start.innerHTML = ICO.play + "<span>Старт</span>"; paintIdle();
    });
    paintIdle();
    host.appendChild(rateRow("ТРУД · Д (дыхание)", function (v) { addLog("ТРУД · Д (дыхание)", v, cycles + " циклов"); }));
  }

  /* ---------- Р: парная мышечная релаксация ---------- */
  var GROUPS = ["Кисти", "Руки", "Плечи", "Лоб", "Глаза", "Нос и щёки", "Губы и челюсть", "Язык и рот",
    "Шея", "Грудь", "Спина", "Живот", "Ягодицы", "Бёдра", "Икры", "Стопы"];
  function toolRelax(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · напряжение и отпускание</span><span class="tool-sub">шаг Р</span></div>' +
      '<div class="tool-body"></div>';
	$(".tool-head", host).appendChild(soundToggleBtn());
    var body = $(".tool-body", host);
    var dial = makeDial("сек");
    var side = document.createElement("div"); side.className = "tool-side";
    var phase = document.createElement("div"); phase.className = "phase q"; phase.setAttribute("aria-live", "polite");
    phase.textContent = "Устройтесь удобно, ослабьте тесную одежду.";
    var hint = document.createElement("div"); hint.className = "tool-hint";
    hint.textContent = "На вдохе напрягите мышцы (не до судороги), на выдохе мысленно скажите «Расслабься» и отпустите.";
    var ctrls = document.createElement("div"); ctrls.className = "ctrls";
    var chips = document.createElement("div"); chips.className = "muscles";
    var track = document.createElement("div"); track.className = "bar-track"; track.innerHTML = "<i></i>";
    side.appendChild(phase); side.appendChild(hint); side.appendChild(ctrls); side.appendChild(track); side.appendChild(chips);
    body.appendChild(dial.el); body.appendChild(side);

    var tense = 5, release = 12, idx = 0, mode = "tense", left = tense, running = false, last = 0, raf = null;
    GROUPS.forEach(function (g) { var s = document.createElement("span"); s.textContent = g; chips.appendChild(s); });
    function paintGroups() {
      $$("span", chips).forEach(function (s, i) { s.className = i < idx ? "done" : (i === idx ? "now" : ""); });
    }
    var sT = stepper(tense, 4, 8, 1, function (v) { return "напрячь " + v; }, function (v) { tense = v; if (!running && mode === "tense") { left = v; paint(); } });
    var sR = stepper(release, 8, 20, 1, function (v) { return "отпустить " + v; }, function (v) { release = v; if (!running && mode === "release") { left = v; paint(); } });
    var start = btn("Старт", "", "play"), skip = btn("Дальше", "ghost sm"), reset = btn("Сброс", "ghost", "reset");
    ctrls.appendChild(sT.el); ctrls.appendChild(sR.el); ctrls.appendChild(start); ctrls.appendChild(skip); ctrls.appendChild(reset);

    function paint() {
      var total = mode === "tense" ? tense : release;
      dial.set(Math.max(1, Math.ceil(left)), left / total);
      $("i", track).style.width = (100 * (1 - left / total)).toFixed(1) + "%";
      paintGroups();
    }
    function enter(m) {
      mode = m; left = m === "tense" ? tense : release;
      phase.className = "phase";
      phase.textContent = m === "tense"
        ? "Вдох · напрягите: " + GROUPS[idx].toLowerCase()
        : "Выдох · «Расслабься» · отпустите";
      if (m === "tense") SND.inhale(); else SND.exhale();
      paint();
    }
    function next() {
      if (mode === "tense") { enter("release"); return; }
      idx++;
      if (idx >= GROUPS.length) { finish(); return; }
      enter("tense");
    }
    function finish() {
      running = false; cancelAnimationFrame(raf); last = 0;
      idx = GROUPS.length; paintGroups();
      phase.className = "phase"; phase.textContent = "Всё тело пройдено. Заметьте разницу и оцените накал.";
      dial.set("0", 0); start.innerHTML = ICO.play + "<span>Ещё раз</span>";
      toast("Релаксация завершена. Оцените накал.");
	  SND.done();
    }
    function loop(ts) {
      if (!running) return;
      if (!last) last = ts;
      var dt = Math.min(.25, (ts - last) / 1000); last = ts;
      left -= dt;
      if (left <= 0) next();
      if (!running) return;
      paint(); raf = requestAnimationFrame(loop);
    }
    function toggleRelax() {
      if (running) { running = false; cancelAnimationFrame(raf); last = 0; start.innerHTML = ICO.play + "<span>Продолжить</span>"; return; }
      if (idx >= GROUPS.length) { idx = 0; }
      running = true; last = 0; start.innerHTML = ICO.pause + "<span>Пауза</span>";
      enter(mode); raf = requestAnimationFrame(loop);
    }
    start.addEventListener("click", toggleRelax);
    dial.el.setAttribute("role", "button");
    dial.el.setAttribute("tabindex", "0");
    dial.el.setAttribute("aria-label", "Запустить или поставить релаксацию на паузу");
    dial.el.addEventListener("click", toggleRelax);
    dial.el.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggleRelax(); }
    });
    skip.addEventListener("click", function () { if (idx < GROUPS.length) next(); });
    reset.addEventListener("click", function () {
      running = false; cancelAnimationFrame(raf); last = 0; idx = 0; mode = "tense"; left = tense;
      start.innerHTML = ICO.play + "<span>Старт</span>";
      phase.className = "phase q"; phase.textContent = "Устройтесь удобно, ослабьте тесную одежду.";
      paint();
    });
    paint();
    host.appendChild(rateRow("ТРУД · Р (релаксация)", function (v) { addLog("ТРУД · Р (релаксация)", v, Math.min(idx, GROUPS.length) + " групп"); }));
  }

  /* ---------- С: замрите ---------- */
  function toolFreeze(host) {
    timerTool(host, {
      title: "Практика · замрите", sub: "шаг С", unit: "сек",
      seconds: 10, min: 3, max: 20, step: 1, fmt: function (v) { return Math.ceil(v); },
      idle: "Нажмите «Старт» — и не двигайтесь.",
      run: "Не двигайте ни одной мышцей. Ничего не отправляйте.",
      done: "Пауза состоялась. Переходите к шагу Т — шаг назад.",
      hint: "Руки от телефона, от двери, от предмета. Ни слова: ни последнего слова, ни оправдания.",
      logLabel: "СТОП · С (стоп)", toast: "Стоп отработано. Шаг Т — отойдите."
    });
  }

  /* ---------- Т: пауза ---------- */
  function toolPause(host) {
    var t = timerTool(host, {
      title: "Практика · пауза", sub: "шаг Т", unit: "мин:сек",
      seconds: 180, min: 60, max: 300, step: 60, fmt: mmss,
      idle: "Отойдите и поставьте таймер паузы.",
      run: "Дышите глубоко. Пауза не для прокрутки обид.",
      done: "Пауза закончилась. Осмотритесь — шаг О.",
      hint: "Уйти нельзя — отойдите мысленно: «это эмоция, а не приказ».",
      logLabel: "СТОП · Т (пауза)", toast: "Пауза завершена. Шаг О — осмотритесь."
    });
    var row = document.createElement("div"); row.className = "ctrls"; row.style.marginTop = "10px";
    var phrase = document.createElement("div"); phrase.className = "tool-hint"; phrase.style.margin = "10px 0 0";
    function paintPhrase() { phrase.textContent = "Фраза для паузы: «Мне нужно " + Math.round(t.cd.total / 60) + " минут, я вернусь к разговору»."; }
    var copy = btn("Скопировать фразу", "ghost sm", "copy");
    copy.addEventListener("click", function () { copyText("Мне нужно " + Math.round(t.cd.total / 60) + " минут, я вернусь к разговору."); });
    row.appendChild(copy); host.insertBefore(row, $(".rate", host)); host.insertBefore(phrase, $(".rate", host));
    paintPhrase();
    $$(".stepper button", host).forEach(function (b) { b.addEventListener("click", paintPhrase); });
  }

  /* ---------- О: осмотрись ---------- */
  var SORT_ITEMS = [
    { t: "«Он не ответил на сообщение 40 минут»", a: "fact", why: "Это наблюдение: время и действие можно проверить." },
    { t: "«Он меня бросает»", a: "thought", why: "Это толкование. Факт — только отсутствие ответа." },
    { t: "«Я повысила голос и перебила»", a: "fact", why: "Наблюдаемое поведение — своё тоже можно описать без оценок." },
    { t: "«Все считают меня неадекватной»", a: "thought", why: "Чтение мыслей: фактов о «всех» нет." },
    { t: "«Он отвернулся и посмотрел в телефон»", a: "fact", why: "Действие, которое видно снаружи." },
    { t: "«Ему всё равно, что со мной»", a: "thought", why: "Вывод о чужих чувствах — это мысль, а не факт." }
  ];
  function toolObserve(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · осмотритесь</span><span class="tool-sub">шаг О</span></div>' +
      '<div class="tool-hint">Сначала — что внутри и снаружи. Затем отделите факты от толкований.</div>' +
      '<div class="fields">' +
      '<div class="field"><label for="ob-in">Внутри: эмоция, тело, мысль, побуждение</label><textarea id="ob-in" rows="3" placeholder="Например: злость, жар в груди, «меня не ценят», хочу написать"></textarea></div>' +
      '<div class="field"><label for="ob-out">Снаружи: что сказано и сделано</label><textarea id="ob-out" rows="3" placeholder="Только наблюдаемое: слова, действия, время"></textarea></div>' +
      "</div>" +
      '<div class="tool-head" style="margin:16px 0 4px"><span class="tool-title">Факт или мысль?</span><span class="tool-sub" id="sort-score">0 из 6</span></div>' +
      '<div class="sorter"></div>';
    var sorter = $(".sorter", host), score = 0, answered = 0;
    SORT_ITEMS.forEach(function (it) {
      var row = document.createElement("div"); row.className = "sort-row";
      row.innerHTML = '<span class="txt">' + it.t + "</span>";
      var acts = document.createElement("div"); acts.className = "acts";
      [["fact", "Факт"], ["thought", "Мысль"]].forEach(function (p) {
        var b = document.createElement("button"); b.type = "button"; b.textContent = p[1];
        b.addEventListener("click", function () {
          if (row.dataset.done) return;
          row.dataset.done = "1"; answered++;
          var ok = p[0] === it.a;
          if (ok) score++;
          row.classList.add(ok ? "right" : "wrong");
          var fb = document.createElement("div"); fb.className = "sort-fb";
          fb.textContent = (ok ? "Верно. " : "Это " + (it.a === "fact" ? "факт. " : "мысль. ")) + it.why;
          row.appendChild(fb);
          $$("button", acts).forEach(function (x) { x.disabled = true; });
          $("#sort-score", host).textContent = score + " из " + SORT_ITEMS.length;
          if (answered === SORT_ITEMS.length) toast("Разбор пройден: " + score + " из " + SORT_ITEMS.length);
        });
        acts.appendChild(b);
      });
      row.appendChild(acts); sorter.appendChild(row);
    });
    var save = btn("Сохранить в дневник", "", "arrow");
    save.style.marginTop = "14px";
    save.addEventListener("click", function () {
      var a = $("#ob-in", host).value.trim(), b = $("#ob-out", host).value.trim();
      if (!a && !b) { toast("Сначала опишите, что внутри и снаружи"); return; }
      var det = (a ? "Внутри: " + a : "") + (a && b ? "\n" : "") + (b ? "Снаружи: " + b : "");
      addLog("СТОП · О (наблюдение)", null, (a || b).slice(0, 50), det);
      $("#ob-in", host).value = "";
      $("#ob-out", host).value = "";
      toast("Сохранено в дневник, поля очищены");
    });
    host.appendChild(save);
  }

  /* ---------- П: мудрый разум ---------- */
  function toolWise(host) {
    var actions = ["Отложить сообщение до утра", "Попросить паузу", "Применить ТРУД", "Составить «за/против»", "Лечь спать", "Позвонить по кризисному плану"];
    var chosen = actions[0];
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · мудрый разум</span><span class="tool-sub">шаг П</span></div>' +
      '<div class="tool-hint">Четыре вопроса — и одно наименьшее действие, которое не ухудшит.</div>' +
      '<div class="fields">' +
      '<div class="field"><label for="w-goal">Моя цель в этой ситуации</label><input id="w-goal" type="text" placeholder="Например: сохранить отношения и себя"></div>' +
      '<div class="field"><label for="w-better">Что сделает лучше</label><input id="w-better" type="text" placeholder="Пауза, сон, короткое честное сообщение"></div>' +
      '<div class="field"><label for="w-worse">Что сделает хуже</label><input id="w-worse" type="text" placeholder="Двадцать звонков, обвинения, самоповреждение"></div>' +
      '<div class="field"><label for="w-other">Что может чувствовать другой</label><input id="w-other" type="text" placeholder="Усталость, растерянность, злость"></div>' +
      "</div>" +
      '<div class="tool-head" style="margin:16px 0 6px"><span class="tool-title">Один шаг сейчас</span></div>' +
      '<div class="pick"></div>';
    var pick = $(".pick", host);
    actions.forEach(function (a, i) {
      var b = document.createElement("button"); b.type = "button"; b.textContent = a;
      b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      b.addEventListener("click", function () {
        chosen = a; $$("button", pick).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      });
      pick.appendChild(b);
    });
    var row = document.createElement("div"); row.className = "ctrls"; row.style.marginTop = "12px";
    var save = btn("Сохранить в дневник", "", "arrow");
    save.addEventListener("click", function () {
      var goal = $("#w-goal", host).value.trim();
      var better = $("#w-better", host).value.trim();
      var worse = $("#w-worse", host).value.trim();
      var other = $("#w-other", host).value.trim();
      var det = [
        "Выбранный шаг: " + chosen,
        goal ? "Цель: " + goal : "",
        better ? "Что сделает лучше: " + better : "",
        worse ? "Что сделает хуже: " + worse : "",
        other ? "Что может чувствовать другой: " + other : ""
      ].filter(Boolean).join("\n");
      addLog("СТОП · П (осознанный шаг)", null, chosen, det);
      $("#w-goal", host).value = "";
      $("#w-better", host).value = "";
      $("#w-worse", host).value = "";
      $("#w-other", host).value = "";
      toast("Сохранено в дневник, поля очищены");
    });
    row.appendChild(save); host.appendChild(row);
    host.appendChild(rateRow("СТОП · П (после шага)", function (v) { addLog("СТОП · П (после шага)", v, chosen); }));
  }

  /* ---------- ЗА/ПРОТИВ: интерактивные шаги матрицы ---------- */
  function getPCData() { return store.get("dbt-pc-matrix", { imp: "", p1: "", c1: "", p2: "", c2: "" }); }
  function setPCData(d) { store.set("dbt-pc-matrix", d); }

  function toolPC1(host) {
    var d = getPCData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · формулировка импульса</span><span class="tool-sub">шаг 1</span></div>' +
      '<div class="field"><label for="pc-imp">Прямо сейчас мне хочется...</label>' +
      '<input id="pc-imp" type="text" placeholder="Например: написать обвиняющее сообщение / причинить себе боль"></div>' +
      '<div class="tool-hint" style="margin:8px 0 0">Запись сохраняется автоматически для следующих шагов.</div>';
    var inp = $("#pc-imp", host);
    inp.value = d.imp || "";
    inp.addEventListener("input", function () { var cur = getPCData(); cur.imp = inp.value; setPCData(cur); });
  }

  function toolPC2(host) {
    var d = getPCData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Матрица · сторона срыва</span><span class="tool-sub">квадраты 1 и 2</span></div>' +
      '<div class="fields">' +
      '<div class="field"><label for="pc-p1">ЗА срыв (выгода в ближайшие 5 мин)</label><textarea id="pc-p1" rows="3" placeholder="Сброшу напряжение, получу реакцию сейчас..."></textarea></div>' +
      '<div class="field"><label for="pc-c1">ПРОТИВ срыва (цена завтра и через неделю)</label><textarea id="pc-c1" rows="3" placeholder="Стыд, испорченные отношения, откат..."></textarea></div>' +
      '</div>';
    var p1 = $("#pc-p1", host), c1 = $("#pc-c1", host);
    p1.value = d.p1 || ""; c1.value = d.c1 || "";
    p1.addEventListener("input", function () { var cur = getPCData(); cur.p1 = p1.value; setPCData(cur); });
    c1.addEventListener("input", function () { var cur = getPCData(); cur.c1 = c1.value; setPCData(cur); });
  }

  function toolPC3(host) {
    var d = getPCData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Матрица · сторона сдержанности</span><span class="tool-sub">квадраты 3 и 4</span></div>' +
      '<div class="fields">' +
      '<div class="field"><label for="pc-p2">ЗА удержаться (польза сейчас и в долгую)</label><textarea id="pc-p2" rows="3" placeholder="Сохраню самоуважение, завтра скажу себе спасибо..."></textarea></div>' +
      '<div class="field"><label for="pc-c2">ПРОТИВ удержаться (трудность прямо сейчас)</label><textarea id="pc-c2" rows="3" placeholder="Придётся терпеть тревогу ещё 20–30 минут..."></textarea></div>' +
      '</div>';
    var p2 = $("#pc-p2", host), c2 = $("#pc-c2", host);
    p2.value = d.p2 || ""; c2.value = d.c2 || "";
    p2.addEventListener("input", function () { var cur = getPCData(); cur.p2 = p2.value; setPCData(cur); });
    c2.addEventListener("input", function () { var cur = getPCData(); cur.c2 = c2.value; setPCData(cur); });
  }

  function toolPC4(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Сводка матрицы и решение</span><span class="tool-sub">шаг 4</span></div>' +
      '<div class="tool-hint" id="pc-summary" style="color:var(--ink);margin-bottom:12px"></div>' +
      '<div class="ctrls">' +
      '<button class="btn sm" type="button" id="pc-save-db"><span>Сохранить в дневник</span></button>' +
      '<button class="btn ghost sm" type="button" id="pc-refresh"><span>Обновить сводку</span></button>' +
      '<button class="btn ghost sm" type="button" id="pc-copy"><span>Скопировать</span></button>' +
      '</div>';
    function formatPC(d) {
      return [
        "Импульс: " + (d.imp || "—"),
        "ЗА срыв (сейчас): " + (d.p1 || "—"),
        "ПРОТИВ срыва (потом): " + (d.c1 || "—"),
        "ЗА удержаться (потом): " + (d.p2 || "—"),
        "ПРОТИВ удержаться (сейчас): " + (d.c2 || "—")
      ].join("\n");
    }
    function renderSum() {
      var d = getPCData();
      var imp = d.imp ? "Импульс: «" + d.imp + "». " : "";
      var c1 = d.c1 ? "Цена срыва: " + d.c1 + ". " : "";
      var p2 = d.p2 ? "Ради чего держусь: " + d.p2 + "." : "";
      $("#pc-summary", host).textContent = (imp + c1 + p2) || "Заполните поля в шагах 1–3, чтобы увидеть сводку здесь.";
    }
    renderSum();
    $("#pc-refresh", host).addEventListener("click", renderSum);
    $("#pc-copy", host).addEventListener("click", function () {
      copyText("Матрица «За и против»\n" + formatPC(getPCData()));
    });
    $("#pc-save-db", host).addEventListener("click", function () {
      var d = getPCData();
      if (!d.imp && !d.p1 && !d.c1 && !d.p2 && !d.c2) { toast("Сначала заполните хотя бы одно поле матрицы"); return; }
      var rInp = $(".rate input[type=range]", host);
      var rateVal = rInp ? parseInt(rInp.value, 10) : null;
      addLog("ЗА/ПРОТИВ · матрица", rateVal, d.imp ? d.imp.slice(0, 50) : "", formatPC(d));
      store.del("dbt-pc-matrix");
      ["#pc-imp", "#pc-p1", "#pc-c1", "#pc-p2", "#pc-c2"].forEach(function (sel) {
        var el = $(sel); if (el) el.value = "";
      });
      renderSum();
      toast("Матрица сохранена в дневник, поля очищены");
    });
    host.appendChild(rateRow("ЗА/ПРОТИВ · накал", function (v) {
      var d = getPCData();
      addLog("ЗА/ПРОТИВ · оценка накала", v, d.imp ? d.imp.slice(0, 50) : "");
    }));
  }

  /* ---------- РЕШЕНИЕ ПРОБЛЕМЫ: 7 отдельных шагов (М. Линехан) ---------- */
  function getPSData() {
    return store.get("dbt-ps-data", {
      event: "", facts: "", goal: "", ideas: [], step: "", planB: "", result: ""
    });
  }
  function setPSData(d) { store.set("dbt-ps-data", d); }

  function toolPS1(host) {
    var d = getPSData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · описание события</span><span class="tool-sub">шаг 1 из 7</span></div>' +
      '<div class="field"><label for="ps-event">Что произошло? (как видеокамера, без оценок и ярлыков)</label>' +
      '<textarea id="ps-event" rows="3" placeholder="Например: Коллега не прислал свою часть отчёта к 15:00, как мы договаривались вчера..."></textarea></div>';
    var ev = $("#ps-event", host);
    ev.value = d.event || "";
    ev.addEventListener("input", function () { var cur = getPSData(); cur.event = ev.value; setPSData(cur); });
  }

  function toolPS2(host) {
    var d = getPSData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · проверка фактов</span><span class="tool-sub">шаг 2 из 7</span></div>' +
      '<div class="field"><label for="ps-facts">Проверенные факты (отдельно от домыслов и тревожных мыслей)</label>' +
      '<textarea id="ps-facts" rows="3" placeholder="Факт: письма нет. Мысль: «он меня подставляет». Эмоция оправдана фактами..."></textarea></div>' +
      '<div class="tool-hint" style="margin:12px 0 6px">Отметьте все пункты, которые выполняются:</div>' +
      '<div class="ps-checks">' +
      '<label class="ps-chk"><input type="checkbox"> Факты подтвердились (если нет — вернитесь к Шагу 1)</label>' +
      '<label class="ps-chk"><input type="checkbox"> Моя эмоция оправдана реальными фактами</label>' +
      '<label class="ps-chk"><input type="checkbox"> Ситуацию можно изменить моими действиями</label>' +
      '</div>' +
      '<div class="ps-warn on" id="ps-warn">Пока отмечены не все пункты: если факты неверны — перепишите Шаг 1. Если эмоция не оправдана или ситуацию нельзя изменить — этот буклет не подойдёт: обсудите с терапевтом навыки принятия или противоположного действия, а пережить накал здесь помогут СТОП и ТРУД.</div>' +
      '<div class="tool-hint" id="ps-ok" style="display:none;color:var(--a-deep);font-weight:700;margin-top:10px">Все условия выполнены — можно переходить к Шагу 3 и формулировать цель.</div>';
    var fa = $("#ps-facts", host), warn = $("#ps-warn", host), okMsg = $("#ps-ok", host);
    fa.value = d.facts || "";
    fa.addEventListener("input", function () { var cur = getPSData(); cur.facts = fa.value; setPSData(cur); });
    $$(".ps-chk input", host).forEach(function (cb) {
      cb.addEventListener("change", function () {
        var allOk = $$(".ps-chk input", host).every(function (x) { return x.checked; });
        warn.classList.toggle("on", !allOk);
        okMsg.style.display = allOk ? "block" : "none";
      });
    });
  }

  function toolPS3(host) {
    var d = getPSData();
    var presets = ["Договориться о новых правилах", "Спокойно обозначить границы", "Исправить ошибку", "Прояснить ситуацию"];
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Практика · простая и реалистичная цель</span><span class="tool-sub">шаг 3 из 7</span></div>' +
      '<div class="pick"></div>' +
      '<div class="field"><label for="ps-goal">Что конкретно должно измениться? (зависит от моих действий)</label>' +
      '<input id="ps-goal" type="text" placeholder="Например: Согласовать с коллегой новый срок сдачи до завтра"></div>';
    var pick = $(".pick", host), inp = $("#ps-goal", host);
    inp.value = d.goal || "";
    presets.forEach(function (p) {
      var b = document.createElement("button"); b.type = "button"; b.textContent = p;
      b.addEventListener("click", function () { inp.value = p + ": "; inp.focus(); var cur = getPSData(); cur.goal = inp.value; setPSData(cur); });
      pick.appendChild(b);
    });
    inp.addEventListener("input", function () { var cur = getPSData(); cur.goal = inp.value; setPSData(cur); });
  }
  function toolPS4(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Мозговой штурм · все идеи без критики</span><span class="tool-sub" id="ps-count">0 идей</span></div>' +
      '<div class="ctrls">' +
      '<input id="ps-idea-in" type="text" placeholder="Запишите любую идею, даже смелую..." style="flex:1;min-width:180px;font:inherit;font-size:14px;padding:7px 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink)">' +
      '<button class="btn sm" type="button" id="ps-idea-add"><span>+ Добавить</span></button>' +
      '</div><div class="idea-list" id="ps-ideas"></div>';
    var list = $("#ps-ideas", host), inp = $("#ps-idea-in", host), cnt = $("#ps-count", host);
    function render() {
      var arr = getPSData().ideas || [];
      list.innerHTML = ""; cnt.textContent = arr.length + " идей";
      arr.forEach(function (it, idx) {
        var row = document.createElement("div"); row.className = "idea-item";
        row.innerHTML = '<span>' + (idx + 1) + '. ' + it.text.replace(/</g, "&lt;") + '</span><button type="button" class="del" title="Удалить">×</button>';
        $(".del", row).addEventListener("click", function () { var cur = getPSData(); cur.ideas.splice(idx, 1); setPSData(cur); render(); });
        list.appendChild(row);
      });
    }
    function add() {
      var val = inp.value.trim(); if (!val) return;
      var cur = getPSData(); cur.ideas = cur.ideas || []; cur.ideas.push({ text: val, picked: false });
      setPSData(cur); inp.value = ""; render();
    }
    $("#ps-idea-add", host).addEventListener("click", add);
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); add(); } });
    render();
  }

  function toolPS5(host) {
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Выбор 1–2 лучших решений</span><span class="tool-sub">шаг 5 из 7</span></div>' +
      '<div class="tool-hint">Отметьте галочкой решения из Шага 4, которые лучше всего ведут к вашей цели.</div>' +
      '<div class="idea-list" id="ps-pick-list"></div>' +
      '<div class="ctrls" style="margin-top:10px"><button class="btn ghost sm" type="button" id="ps-sync"><span>Обновить список из Шага 4</span></button></div>';
    var list = $("#ps-pick-list", host);
    function render() {
      var arr = getPSData().ideas || [];
      list.innerHTML = "";
      if (!arr.length) { list.innerHTML = '<div class="tool-hint">Сначала добавьте идеи на Шаге 4.</div>'; return; }
      arr.forEach(function (it, idx) {
        var lbl = document.createElement("label");
        lbl.className = "idea-item" + (it.picked ? " picked" : "");
        lbl.innerHTML = '<input type="checkbox"' + (it.picked ? " checked" : "") + '><span>' + it.text.replace(/</g, "&lt;") + '</span>';
        $("input", lbl).addEventListener("change", function (e) { var cur = getPSData(); cur.ideas[idx].picked = e.target.checked; setPSData(cur); render(); });
        list.appendChild(lbl);
      });
    }
    $("#ps-sync", host).addEventListener("click", render);
    render();
  }

  function toolPS6(host) {
    var d = getPSData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">План действия</span><span class="tool-sub">шаг 6 из 7</span></div>' +
      '<div class="fields">' +
      '<div class="field"><label for="ps-step">Первый конкретный шаг (ближайшие 24 часа)</label><input id="ps-step" type="text" placeholder="Что, где и когда я сделаю"></div>' +
      '<div class="field"><label for="ps-planb">Запасной вариант (из списка идей)</label><input id="ps-planb" type="text" placeholder="Что сделаю при препятствии"></div>' +
      '</div>';
    var st = $("#ps-step", host), pb = $("#ps-planb", host);
    st.value = d.step || ""; pb.value = d.planB || "";
    st.addEventListener("input", function () { var cur = getPSData(); cur.step = st.value; setPSData(cur); });
    pb.addEventListener("input", function () { var cur = getPSData(); cur.planB = pb.value; setPSData(cur); });
  }

  function toolPS7(host) {
    var d = getPSData();
    host.innerHTML =
      '<div class="tool-head"><span class="tool-title">Оценка результата и сохранение</span><span class="tool-sub">шаг 7 из 7</span></div>' +
      '<div class="field"><label for="ps-result">Что получилось? Достигнута ли цель и снизилась ли эмоция?</label>' +
      '<textarea id="ps-result" rows="2" placeholder="Сработало — закрепляю. Не сработало — возвращаюсь к Шагу 5..."></textarea></div>' +
      '<div class="ctrls" style="margin-top:12px">' +
      '<button class="btn sm" type="button" id="ps-save-db"><span>Сохранить в дневник</span></button>' +
      '<button class="btn ghost sm" type="button" id="ps-copy"><span>Скопировать</span></button>' +
      '<button class="btn ghost sm" type="button" id="ps-back5"><span>Не сработало → к Шагу 5</span></button>' +
      '<button class="btn ghost sm" type="button" id="ps-clear"><span>Очистить</span></button>' +
      '</div>';
    var res = $("#ps-result", host), clr = $("#ps-clear", host);
    res.value = d.result || "";
    res.addEventListener("input", function () { var cur = getPSData(); cur.result = res.value; setPSData(cur); });
    function formatPS(cur) {
      var allIdeas = (cur.ideas || []).map(function (x) { return (x.picked ? "[✓] " : "[ ] ") + x.text; }).join("\n");
      return [
        "1. Ситуация: " + (cur.event || "—"),
        "2. Факты: " + (cur.facts || "—"),
        "3. Цель: " + (cur.goal || "—"),
        "4–5. Идеи и выбор:\n" + (allIdeas || "—"),
        "6. Первый шаг: " + (cur.step || "—") + (cur.planB ? " (План Б: " + cur.planB + ")" : ""),
        "7. Результат: " + (cur.result || "—")
      ].join("\n");
    }
    function resetAllPS() {
      store.del("dbt-ps-data");
      res.value = "";
      ["#ps-event", "#ps-facts", "#ps-goal", "#ps-step", "#ps-planb"].forEach(function (sel) {
        var el = $(sel); if (el) el.value = "";
      });
      var idList = $("#ps-ideas"), idCnt = $("#ps-count"), pList = $("#ps-pick-list");
      if (idList) idList.innerHTML = "";
      if (idCnt) idCnt.textContent = "0 идей";
      if (pList) pList.innerHTML = '<div class="tool-hint">Сначала добавьте идеи на Шаге 4.</div>';
      $$(".ps-chk input").forEach(function (cb) { cb.checked = false; });
      var w = $("#ps-warn"), ok = $("#ps-ok");
      if (w) w.classList.add("on");
      if (ok) ok.style.display = "none";
    }
    $("#ps-back5", host).addEventListener("click", function () {
      var target = document.getElementById("step-5");
      if (target) { target.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" }); toast("Выберите другое решение на Шаге 5"); }
    });
    $("#ps-copy", host).addEventListener("click", function () {
      copyText("Решение проблемы · 7 шагов ДБТ (М. Линехан)\n" + formatPS(getPSData()));
    });
    $("#ps-save-db", host).addEventListener("click", function () {
      var cur = getPSData();
      if (!cur.event && !cur.facts && !cur.goal && !(cur.ideas && cur.ideas.length) && !cur.step && !cur.result) {
        toast("Сначала заполните хотя бы один шаг разбора"); return;
      }
      var rInp = $(".rate input[type=range]", host);
      var rateVal = rInp ? parseInt(rInp.value, 10) : null;
      addLog("РЕШЕНИЕ · 7 шагов", rateVal, (cur.goal || cur.event || "").slice(0, 50), formatPS(cur));
      resetAllPS();
      toast("Разбор сохранён в дневник, поля очищены");
    });
    var armed = false, pt;
    clr.addEventListener("click", function () {
      if (!armed) { armed = true; clr.querySelector("span").textContent = "Точно очистить?"; pt = setTimeout(function () { armed = false; clr.querySelector("span").textContent = "Очистить"; }, 3500); return; }
      clearTimeout(pt); armed = false; clr.querySelector("span").textContent = "Очистить";
      resetAllPS();
      toast("Разбор очищен");
    });
    host.appendChild(rateRow("РЕШЕНИЕ · накал", function (v) { addLog("РЕШЕНИЕ · оценка накала", v, getPSData().goal.slice(0, 50)); }));
  }

  var TOOLS = {
    cold: toolCold, relax: toolRelax, move: toolMove, breath: toolBreath,
    freeze: toolFreeze, pause: toolPause, observe: toolObserve, wise: toolWise,
    pc1: toolPC1, pc2: toolPC2, pc3: toolPC3, pc4: toolPC4,
    ps1: toolPS1, ps2: toolPS2, ps3: toolPS3, ps4: toolPS4, ps5: toolPS5, ps6: toolPS6, ps7: toolPS7
  };


  /* ---------- шкала накала ---------- */
  function initScale() {
    var box = $("#scale-live"); if (!box) return;
    var r = $("#scale-range", box), out = $("#scale-value", box), rec = $("#scale-rec", box);
    function paint() {
      var v = parseInt(r.value, 10); out.textContent = v;
      var zone = v <= 4 ? 0 : (v <= 7 ? 1 : 2);
      $$(".zone").forEach(function (z, i) { z.classList.toggle("hot", i === zone); });
      var txt = [
        "Мышление доступно: разбирайте ситуацию, решайте проблему, тренируйте навыки.",
        "Сначала пауза: СТОП. Затем ТРУД или «за/против».",
        "Сначала тело: ТРУД. Слова и анализ пока не работают."
      ][zone];
      rec.textContent = txt;
      rec.dataset.zone = zone;
    }
    r.addEventListener("input", paint);
    var save = $("#scale-save", box);
    if (save) save.addEventListener("click", function () { addLog("Отметка накала", parseInt(r.value, 10), "шкала"); toast("Накал отмечен"); });
    paint();
  }

  /* ---------- карточка на кризис ---------- */
  function initCard() {
    var key = "dbt-card-" + CFG.skill;
    var data = store.get(key, {});
    var saved = $("#card-saved");
    var t;
    $$(".fill textarea").forEach(function (ta) {
      var id = ta.dataset.f;
      if (data[id]) ta.value = data[id];
      ta.addEventListener("input", function () {
        data[id] = ta.value;
        var ok = store.set(key, data);
        if (saved) { saved.textContent = ok ? "сохранено" : "не сохраняется в этом режиме"; saved.classList.add("on"); clearTimeout(t); t = setTimeout(function () { saved.classList.remove("on"); }, 1600); }
      });
    });
    var copy = $("#card-copy");
    if (copy) copy.addEventListener("click", function () {
      var lines = ["Моя карточка на кризис · навык " + CFG.acronym];
      $$(".fill").forEach(function (f) {
        lines.push($(".fl", f).textContent + ": " + ($("textarea", f).value.trim() || "—"));
      });
      copyText(lines.join("\n"));
    });
    var clear = $("#card-clear");
    if (clear) {
      var armed = false, ct;
      clear.addEventListener("click", function () {
        var areas = $$(".fill textarea");
        var hasText = areas.some(function (ta) { return ta.value.trim() !== ""; });
        if (!hasText) { toast("Карточка уже пуста"); return; }
        if (!armed) {
          armed = true;
          clear.querySelector("span").textContent = "Точно очистить?";
          ct = setTimeout(function () { armed = false; clear.querySelector("span").textContent = "Очистить"; }, 3500);
          return;
        }
        clearTimeout(ct); armed = false; clear.querySelector("span").textContent = "Очистить";
        data = {}; store.del(key);
        areas.forEach(function (ta) { ta.value = ""; });
        if (saved) saved.classList.remove("on");
        toast("Карточка очищена");
      });
    }
  }
	

  /* ---------- панель «накрывает сейчас» ---------- */
  function initSOS() {
    var openBtn = $("#sos-open"), panel = $("#sos"), closeBtn = $("#sos-close");
    if (!openBtn || !panel) return;
    var lastFocus = null;
    function open() {
      lastFocus = document.activeElement;
      panel.classList.add("on"); document.body.style.overflow = "hidden";
      var f = $(".sos-step", panel); if (f) f.focus();
    }
    function close() {
      panel.classList.remove("on"); document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }
    openBtn.addEventListener("click", open);
    var coverBtn = $("#cover-sos"); if (coverBtn) coverBtn.addEventListener("click", open);
    closeBtn.addEventListener("click", close);
    panel.addEventListener("click", function (e) { if (e.target === panel) close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("on")) close();
      if (e.key === "Tab" && panel.classList.contains("on")) {
        var f = $$("button, a[href], input, textarea", panel).filter(function (x) { return !x.disabled; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    $$(".sos-step", panel).forEach(function (b) {
      b.addEventListener("click", function () {
        close();
        var target = document.getElementById(b.dataset.target);
        if (target) {
          target.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
          var tool = $(".tool", target);
          if (tool && tool.dataset.autostart === "1") {
            var sb = $$(".btn", tool).filter(function (x) { return /Старт|Продолжить/.test(x.textContent); })[0];
            if (sb) setTimeout(function () { sb.click(); }, reduced ? 0 : 650);
          }
        }
      });
    });
  }

  /* ---------- прокрутка, появление, активная секция ---------- */
  function initScroll() {
    var bar = $("#progress-bar");
    function paint() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (bar) bar.style.width = (h > 0 ? clamp(window.scrollY / h, 0, 1) * 100 : 0) + "%";
    }
    window.addEventListener("scroll", paint, { passive: true });
    window.addEventListener("resize", paint); paint();

    if ("IntersectionObserver" in window && !reduced) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -8% 0px", threshold: .06 });
      $$(".reveal").forEach(function (n) { io.observe(n); });
    } else $$(".reveal").forEach(function (n) { n.classList.add("in"); });

    var links = $$("[data-jump]");
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var t = document.getElementById(a.dataset.jump);
        if (t) { e.preventDefault(); t.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" }); }
      });
    });
    var pb = $("#print-btn"); if (pb) pb.addEventListener("click", function () { window.print(); });
  }

  /* ---------- страница «Дневник» (браузер БД) ---------- */
  function initDiary() {
    var host = $("#diary-app"); if (!host) return;
    var state = { q: "", date: "", skill: "all", selected: {} };

    function escH(s) { return String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
    function ymd(ts) {
      var d = new Date(ts);
      return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
    }
    function dayTitle(ymdStr) {
      var today = ymd(Date.now());
      var yest = ymd(Date.now() - 86400000);
      var p = ymdStr.split("-");
      var months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
      var label = parseInt(p[2], 10) + " " + months[parseInt(p[1], 10) - 1].trim() + " " + p[0];
      if (ymdStr === today) return "Сегодня · " + label;
      if (ymdStr === yest) return "Вчера · " + label;
      return label;
    }
    function downloadFile(name, content, mime) {
      var blob = new Blob([content], { type: mime });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url; a.download = name;
      document.body.appendChild(a); a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }
    function cleanTitle(e) {
      var lbl = String(e.label || "");
      var sk = String(e.skillName || "");
      if (sk && lbl.toUpperCase().indexOf(sk.toUpperCase()) === 0) return lbl;
      return sk + " · " + lbl;
    }
    function formatItemsText(items, headerTitle) {
      var lines = [headerTitle || ("ДБТ · ДНЕВНИК ПРАКТИКИ (" + ymd(Date.now()) + ")"), "========================================", ""];
      var curDay = "";
      items.slice().sort(function (a, b) { return a.ts - b.ts; }).forEach(function (e) {
        var day = ymd(e.ts);
        if (day !== curDay) { curDay = day; lines.push("=== " + dayTitle(day).toUpperCase() + " ==="); }
        var d = new Date(e.ts);
        var r = typeof e.v === "number" ? " | накал: " + (typeof e.prev === "number" ? e.prev + " -> " : "") + e.v : "";
        lines.push("[" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + "] " + cleanTitle(e) + (e.extra ? " (" + e.extra + ")" : "") + r);
        if (e.details) lines.push(e.details);
        lines.push("");
      });
      return lines.join("\n").trim();
    }
    function formatSingleText(e) {
      var d = new Date(e.ts);
      var r = typeof e.v === "number" ? " | накал: " + (typeof e.prev === "number" ? e.prev + " → " : "") + e.v : "";
      var head = dayTitle(ymd(e.ts)) + ", " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + " · " + cleanTitle(e) + (e.extra ? " (" + e.extra + ")" : "") + r;
      return e.details ? head + "\n" + e.details : head;
    }
    function filtered() {
      var db = loadDB().slice().sort(function (a, b) { return b.ts - a.ts; });
      var q = state.q.trim().toLowerCase();
      return db.filter(function (e) {
        if (state.skill !== "all" && e.skill !== state.skill) return false;
        if (state.date && ymd(e.ts) !== state.date) return false;
        if (q) {
          var hay = (e.skillName + " " + e.label + " " + e.extra + " " + e.details).toLowerCase();
          if (hay.indexOf(q) === -1) return false;
        }
        return true;
      });
    }
    function getSelectedItems() {
      var db = loadDB().slice().sort(function (a, b) { return b.ts - a.ts; });
      return db.filter(function (e) { return !!state.selected[e.id]; });
    }
    function updateSelBar() {
      var bar = $("#db-sel-bar"), cnt = $("#db-sel-cnt");
      if (!bar || !cnt) return;
      var sel = getSelectedItems();
      bar.classList.toggle("on", sel.length > 0);
      cnt.textContent = "Выбрано записей: " + sel.length;
    }
    function renderStats() {
      var db = loadDB();
      var totalEl = $("#db-stat-total"), weekEl = $("#db-stat-week"), dropEl = $("#db-stat-drop");
      if (!totalEl) return;
      totalEl.textContent = db.length;
      var weekAgo = Date.now() - 7 * 86400000;
      weekEl.textContent = db.filter(function (e) { return e.ts >= weekAgo; }).length;
      var deltas = db.filter(function (e) { return typeof e.prev === "number" && typeof e.v === "number"; });
      if (deltas.length) {
        var avg = deltas.reduce(function (s, e) { return s + (e.prev - e.v); }, 0) / deltas.length;
        dropEl.textContent = (avg >= 0 ? "−" : "+") + Math.abs(avg).toFixed(1) + " б.";
      } else { dropEl.textContent = "—"; }
    }
    function render() {
      renderStats();
      updateSelBar();
      var listEl = $("#db-list");
      var items = filtered();
      if (!items.length) {
        listEl.innerHTML = '<p class="log-empty" style="padding:16px 0">Записей по выбранным фильтрам не найдено.</p>';
        return;
      }
      var byId = {};
      items.forEach(function (e) { byId[e.id] = e; });
      var groups = [], map = {};
      items.forEach(function (e) {
        var key = ymd(e.ts);
        if (!map[key]) { map[key] = []; groups.push({ key: key, list: map[key] }); }
        map[key].push(e);
      });
      listEl.innerHTML = groups.map(function (g) {
        var cards = g.list.slice().reverse().map(function (e) {
          var d = new Date(e.ts);
          var tm = pad(d.getHours()) + ":" + pad(d.getMinutes());
          var isSel = !!state.selected[e.id];
          var rate = typeof e.v === "number" ? '<span class="db-rate">накал: ' + (typeof e.prev === "number" ? e.prev + " → " : "") + e.v + '</span>' : "";
          var det = e.details ? '<div class="db-details">' + escH(e.details) + '</div>' : "";
          return '<div class="db-item' + (isSel ? ' sel' : '') + '" data-id="' + escH(e.id) + '">' +
            '<div class="db-item-top">' +
            '<input type="checkbox" class="db-chk" aria-label="Выбрать запись"' + (isSel ? ' checked' : '') + '>' +
            '<span class="db-tag ' + escH(e.skill) + '">' + escH(e.skillName) + '</span>' +
            '<span class="db-time">' + tm + '</span>' +
            '<span class="db-title">' + escH(e.label) + (e.extra ? " · " + escH(e.extra) : "") + '</span>' +
            rate +
            '<button type="button" class="db-copy-one" title="Скопировать запись">Копировать</button>' +
            '<button type="button" class="db-del" title="Удалить запись">×</button>' +
            '</div>' + det + '</div>';
        }).join("");
        return '<div class="db-day"><div class="db-day-head"><span>' + dayTitle(g.key) + '</span><span>' + g.list.length + ' зап.</span></div>' + cards + '</div>';
      }).join("");
      $$(".db-chk", listEl).forEach(function (cb) {
        cb.addEventListener("change", function () {
          var card = cb.closest(".db-item"), id = card && card.dataset.id;
          if (!id) return;
          if (cb.checked) state.selected[id] = true; else delete state.selected[id];
          card.classList.toggle("sel", cb.checked);
          updateSelBar();
        });
      });
      $$(".db-copy-one", listEl).forEach(function (b) {
        b.addEventListener("click", function () {
          var card = b.closest(".db-item"), item = card && byId[card.dataset.id];
          if (item) copyText(formatSingleText(item));
        });
      });
      $$(".db-del", listEl).forEach(function (b) {
        b.addEventListener("click", function () {
          var card = b.closest(".db-item"), id = card && card.dataset.id;
          if (!id) return;
          delete state.selected[id];
          saveDB(loadDB().filter(function (x) { return x.id !== id; }));
          render();
          toast("Запись удалена");
        });
      });
    }

    var qInp = $("#db-q"), dInp = $("#db-date"), clrDate = $("#db-date-clear");
    if (qInp) qInp.addEventListener("input", function () { state.q = qInp.value; render(); });
    if (dInp) dInp.addEventListener("change", function () { state.date = dInp.value; render(); });
    if (clrDate) clrDate.addEventListener("click", function () { state.date = ""; if (dInp) dInp.value = ""; render(); });

    $$(".db-chip", host).forEach(function (ch) {
      ch.addEventListener("click", function () {
        state.skill = ch.dataset.skill || "all";
        $$(".db-chip", host).forEach(function (x) { x.classList.toggle("on", x === ch); });
        render();
      });
    });

    var expTxt = $("#db-exp-txt"), expJson = $("#db-exp-json"), impJson = $("#db-imp-json"), impFile = $("#db-imp-file");
    if (expTxt) expTxt.addEventListener("click", function () {
      var items = filtered();
      if (!items.length) { toast("Нет записей для экспорта"); return; }
      var lines = ["ДБТ · ДНЕВНИК ПРАКТИКИ (" + ymd(Date.now()) + ")", "========================================", ""];
      var curDay = "";
      items.forEach(function (e) {
        var day = ymd(e.ts);
        if (day !== curDay) { curDay = day; lines.push("=== " + dayTitle(day).toUpperCase() + " ==="); }
        var d = new Date(e.ts);
        var r = typeof e.v === "number" ? " | накал: " + (typeof e.prev === "number" ? e.prev + " -> " : "") + e.v : "";
        lines.push("[" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + "] " + e.skillName + " — " + e.label + (e.extra ? " (" + e.extra + ")" : "") + r);
        if (e.details) lines.push(e.details);
        lines.push("");
      });
      downloadFile("dbt-diary-" + ymd(Date.now()) + ".txt", lines.join("\n"), "text/plain;charset=utf-8");
      toast("Текстовый отчёт (.txt) скачан");
    });

    if (expJson) expJson.addEventListener("click", function () {
      var backup = {
        version: 1,
        exportedAt: new Date().toISOString(),
        journal: loadDB(),
        cards: {
          trud: store.get("dbt-card-trud", {}),
          stop: store.get("dbt-card-stop", {}),
          pros_cons: store.get("dbt-card-pros_cons", {}),
          problem_solving: store.get("dbt-card-problem_solving", {})
        }
      };
      downloadFile("dbt-backup-" + ymd(Date.now()) + ".json", JSON.stringify(backup, null, 2), "application/json;charset=utf-8");
      toast("Резервная копия (.json) скачана");
    });

    if (impJson && impFile) {
      impJson.addEventListener("click", function () { impFile.click(); });
      impFile.addEventListener("change", function () {
        var f = impFile.files && impFile.files[0]; if (!f) return;
        var reader = new FileReader();
        reader.onload = function () {
          try {
            var parsed = JSON.parse(reader.result);
            var incoming = Array.isArray(parsed) ? parsed : (parsed.journal || []);
            var cur = loadDB();
            var ids = {}; cur.forEach(function (x) { ids[x.id] = true; });
            var added = 0;
            incoming.forEach(function (item) {
              if (item && item.ts && !ids[item.id]) { cur.push(item); ids[item.id] = true; added++; }
            });
            cur.sort(function (a, b) { return a.ts - b.ts; });
            saveDB(cur);
            if (parsed.cards) {
              Object.keys(parsed.cards).forEach(function (k) {
                if (parsed.cards[k] && Object.keys(parsed.cards[k]).length) store.set("dbt-card-" + k, parsed.cards[k]);
              });
            }
            render();
            toast("Загружено новых записей: " + added);
          } catch (err) {
            toast("Ошибка чтения файла резервной копии");
          }
          impFile.value = "";
        };
        reader.readAsText(f);
      });
    }

    var selCopy = $("#db-sel-copy"), selTxt = $("#db-sel-txt"), selAll = $("#db-sel-all"), selNone = $("#db-sel-none");
    if (selCopy) selCopy.addEventListener("click", function () {
      var sel = getSelectedItems();
      if (!sel.length) return;
      copyText(sel.length === 1 ? formatSingleText(sel[0]) : formatItemsText(sel, "ДБТ · ВЫБРАННЫЕ ЗАПИСИ (" + sel.length + ")"));
    });
    if (selTxt) selTxt.addEventListener("click", function () {
      var sel = getSelectedItems();
      if (!sel.length) return;
      downloadFile("dbt-selected-" + ymd(Date.now()) + ".txt", formatItemsText(sel, "ДБТ · ВЫБРАННЫЕ ЗАПИСИ (" + sel.length + ")"), "text/plain;charset=utf-8");
      toast("Выбранные записи скачаны (.txt)");
    });
    if (selAll) selAll.addEventListener("click", function () {
      filtered().forEach(function (e) { state.selected[e.id] = true; });
      render();
    });
    if (selNone) selNone.addEventListener("click", function () {
      state.selected = {};
      render();
    });

    render();
  }

  /* ---------- запуск ---------- */

  /* ---------- запуск ---------- */
  function init() {
    $$(".tool").forEach(function (host) {
      var kind = host.dataset.tool;
      if (TOOLS[kind]) { try { TOOLS[kind](host); } catch (e) { host.innerHTML = '<div class="tool-hint">Инструмент недоступен в этом режиме. Шаги навыка описаны выше.</div>'; } }
    });
    initScale(); initCard(); initSOS(); initScroll(); renderLog(); initDiary();
    var lc = $("#log-copy"), lx = $("#log-clear");
    if (lc) lc.addEventListener("click", function () { copyText(logText()); });
    if (lx) {
      var armed = false, t;
      lx.addEventListener("click", function () {
        if (!armed) { armed = true; lx.querySelector("span").textContent = "Точно очистить?"; t = setTimeout(function () { armed = false; lx.querySelector("span").textContent = "Очистить"; }, 3500); return; }
        clearTimeout(t); armed = false; lx.querySelector("span").textContent = "Очистить";
        var rest = loadDB().filter(function (e) { return e.skill !== CFG.skill; });
        saveDB(rest); store.del("dbt-log-" + CFG.skill); renderLog(); toast("Записи этого навыка очищены");
      });
    }
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) window.dispatchEvent(new Event("scroll"));
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
