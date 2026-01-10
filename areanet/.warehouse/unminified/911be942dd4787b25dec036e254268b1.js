YUI.add("arena-base64", (function(t) {
  var s = function(t, s) {
      return t * Math.pow(2, s)
    },
    r = function(t, s) {
      return t / Math.pow(2, s)
    };

  function i(t) {
    this.str = t ? String(t) : ""
  }
  i.base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", i.BASE64_BITS = 6, i.prototype = {
    str: "",
    pval: 0,
    pused: 0,
    gval: 0,
    gused: i.BASE64_BITS,
    gnext: 0,
    put: function(t, e) {
      var n = this.pval,
        u = this.pused,
        h = i.BASE64_BITS - u;
      if (t > s(1, e)) console.error("Base64Codec.put: %o to large for field (%o bits)", t, e);
      else {
        for (this.str + "[" + n + "," + u + "] + " + t + " (" + e + " bits)"; e > h;) n += s(t, u) % 64, t = r(t, h), e -= h, this.str += i.base64.charAt(n), n = 0, u = 0, h = i.BASE64_BITS;
        e && (n += s(t, u), (u += e) == i.BASE64_BITS && (this.str += i.base64.charAt(n), n = 0, u = 0)), this.pval = n, this.pused = u
      }
    },
    putBoundary: function() {
      var t = this.pval;
      this.pused && (this.str += i.base64.charAt(t)), this.pval = 0, this.pused = 0
    },
    putTail: function(t) {
      this.putBoundary(), this.str += t
    },
    get: function(t) {
      for (var s = 0, r = this.gval, e = this.gused, n = i.BASE64_BITS - e, u = t; n < u;) n && (s += r >>> e << t - u, u -= n), this.gnext >= this.str.length ? r = 0 : (r = i.base64.indexOf(this.str.charAt(this.gnext)), this.gnext += 1), e = 0, n = i.BASE64_BITS;
      return u && (s += (r >>> e) % (1 << u) << t - u, e += u), this.gval = r, this.gused = e, s
    },
    skipBoundary: function() {
      this.gused = i.BASE64_BITS
    },
    getTail: function() {
      this.skipBoundary();
      var t = this.str.substr(this.gnext);
      return this.gnext = this.str.length, t
    }
  }, i.dumpBits = function(t) {
    var s, r, e = new i(t),
      n = "<pre>";
    for (n += "   0      1      2      3      4      5      6      7      8      9", n += "<br>", s = 0; s < t.length; ++s) r = Number(e.get(6)).toString(2), n += (r = "000000".substr(r.length) + r) + " ", s % 10 == 9 && (n += "   " + t.substr(s - 9, 10), n += "<br>");
    for (; s % 10; ++s) n += "       ", s % 10 == 9 && (n += "   " + t.substr(s - 9, 10), n += "<br>");
    return n += "\n</pre>"
  }, t.Base64Codec = i
}), "@VERSION@", {
  requires: []
});
YUI.add("hom-points", (function(t) {
  "use strict";
  const e = t.Lang,
    o = t.namespace("hom");

  function n(t) {
    return Math.max(0, Math.min(Number(t), 1))
  }
  o.Points = t.Base.create("Points", t.Base, [], {
    initializer() {
      this.publish("valueChange", {
        emitFacade: !1,
        preventable: !1
      }), this.after(["devotionChange", "fellowshipChange", "honorChange", "resilienceChange", "valorChange"], (function(t) {
        let e = this.get("total");
        e -= t.prevVal.total, e += t.newVal.total, this.set("total", Math.max(0, e)), this.fire("valueChange", t)
      }), this)
    },
    update(t) {
      const e = o.Points.parseBits(t);
      e ? (this.set("character", e), this.setAttrs(o.Points.parseObject(e)), this.fire("updateSuccess", t)) : this.fire("updateFailure", !1 === e)
    },
    getValues(t) {
      return this.getAttrs(t || ["devotion", "fellowship", "honor", "resilience", "valor"])
    }
  }, {
    ATTRS: {
      character: {
        valueFn: () => HOM.character
      },
      total: {
        value: 0,
        validator: e.isNumber
      },
      valor: {
        value: {
          total: 0,
          count: 0,
          destroyer: 0,
          tormented: 0
        }
      },
      honor: {
        value: {
          total: 0,
          count: 0,
          pvp: 0
        }
      },
      devotion: {
        value: {
          total: 0,
          count: 0,
          rare: 0,
          unique: 0
        }
      },
      fellowship: {
        value: {
          total: 0,
          count: 0,
          heroes: 0,
          pets: 0,
          rare: 0
        }
      },
      resilience: {
        value: {
          total: 0,
          count: 0,
          vabbian: 0,
          obsidian: 0,
          kurzick_luxon: 0
        }
      }
    },
    parseBits(e) {
      t.namespace("hom");
      const o = HOM.character,
        n = {
          devotion: {},
          fellowship: {},
          honor: {},
          resilience: {},
          valor: {}
        },
        s = new t.Base64Codec(e);
      let i;
      if (0 === Number(e)) return !1;
      i = 0;
      for (const t in o.resilience) t.length ? n.resilience[t] = s.get(1) : s.get(1), i++;
      s.get(32 - i), i = 0;
      for (const t in o.fellowship) t.length ? n.fellowship[t] = s.get(1) : s.get(1), i++;
      s.get(32 - i), i = 0;
      for (const t in o.honor) t.length ? n.honor[t] = s.get(1) : s.get(1), i++;
      s.get(64 - i), i = 0;
      for (const t in o.valor) t.length ? n.valor[t] = s.get(1) : s.get(1), i++;
      return s.get(64 - i), n.devotion = {
        common: s.get(7),
        uncommon: s.get(7),
        rare: s.get(7),
        unique: s.get(7)
      }, n
    },
    putBits(e) {
      t.namespace("hom");
      const o = HOM.character,
        n = new t.Base64Codec("");
      let s;
      s = 0;
      for (const t in o.resilience) n.put(e.resilience[t] || 0, 1), s++;
      n.put(0, 32 - s), s = 0;
      for (const t in o.fellowship) n.put(e.fellowship[t] || 0, 1), s++;
      n.put(0, 32 - s), s = 0;
      for (const t in o.honor) n.put(e.honor[t] || 0, 1), s++;
      n.put(0, 64 - s), s = 0;
      for (const t in o.valor) n.put(e.valor[t] || 0, 1), s++;
      return n.put(0, 64 - s), n.put(e.devotion.common || 0, 7), n.put(e.devotion.uncommon || 0, 7), n.put(e.devotion.rare || 0, 7), n.put(e.devotion.unique || 0, 7), n.putBoundary(), n.str
    },
    parseObject(e) {
      const n = {};
      let s = 0;
      return t.each(e, (function(t, e) {
        "function" == typeof o.Points[`${e}Points`] && (n[e] = o.Points[`${e}Points`](t), s += n[e].total)
      })), t.merge(n, {
        total: s
      })
    },
    devotionPoints(t) {
      const e = t.common + t.uncommon + t.rare + t.unique;
      let o = 0;
      return e && o++, t.rare && o++, t.unique && o++, e >= 20 && (o += 2), e >= 30 && o++, e >= 40 && o++, e >= 50 && o++, {
        possible: HOM.cols.details.devotion.total,
        total: o,
        count: e,
        rare: t.rare,
        unique: t.unique
      }
    },
    fellowshipPoints(e) {
      const o = HOM.rules.items.fellowship;
      let n = 0,
        s = 0,
        i = 0,
        r = 0,
        a = 0;
      for (const n in e) e.hasOwnProperty(n) && e[n] && (n === o.pet ? i++ : -1 !== t.Array.indexOf(o.rare, n) ? (a = 1, i++) : r++);
      return s = r + i, r && n++, i && n++, a && n++, s >= 5 && (n += 2), s >= 10 && n++, s >= 20 && n++, s >= 30 && n++, {
        possible: HOM.cols.details.fellowship.total,
        total: n,
        count: s,
        heroes: r,
        pets: i,
        rare: a
      }
    },
    honorPoints(e) {
      const o = HOM.rules.items.honor;
      let n, s = 3,
        i = 0,
        r = 0;
      for (const s in e) e.hasOwnProperty(s) && e[s] && (n || -1 === t.Array.indexOf(o.codex_commander, s) || (n = !0, r++), -1 !== t.Array.indexOf(o.pvp, s) && r++, i++);
      return i && (s += 2), r && (s += 3), i >= 5 && (s += 3), i >= 10 && s++, i >= 15 && s++, i >= 20 && s++, i >= 25 && s++, i >= 30 && s++, i >= 35 && s++, i >= 40 && s++, {
        possible: HOM.cols.details.honor.total,
        total: s,
        count: i,
        pvp: r
      }
    },
    resiliencePoints(e) {
      const o = HOM.rules.items.resilience;
      let n = 0,
        s = 0,
        i = 0,
        r = 0,
        a = 0;
      for (const n in e) e.hasOwnProperty(n) && e[n] && (s++, -1 !== t.Array.indexOf(o.vabbian, n) ? i = 1 : -1 !== t.Array.indexOf(o.obsidian, n) ? r = 1 : -1 !== t.Array.indexOf(o.kurzick_luxon, n) && (a = 1));
      return s && n++, s >= 3 && n++, s >= 5 && (n += 2), s >= 7 && n++, a && n++, i && n++, r && n++, {
        possible: HOM.cols.details.resilience.total,
        total: n,
        count: s,
        vabbian: i,
        obsidian: r,
        kurzick_luxon: a
      }
    },
    valorPoints(e) {
      const o = HOM.rules.items.valor;
      let n = 0,
        s = 0,
        i = 0,
        r = 0;
      for (const n in e) e.hasOwnProperty(n) && e[n] && (-1 !== t.Array.indexOf(o.destroyer, n) ? s++ : -1 !== t.Array.indexOf(o.tormented, n) ? i++ : -1 !== t.Array.indexOf(o.oppressor, n) && r++);
      const a = s + i + r;
      return a && n++, s && n++, i && n++, r && n++, a >= 5 && n++, a >= 11 && (n += 2), a >= 15 && n++, {
        possible: HOM.cols.details.valor.total,
        total: n,
        count: a,
        destroyer: s,
        tormented: i,
        oppressor: r
      }
    }
  }), o.points = new o.Points, o.rules = {
    valor: [{
      points: 1,
      test: t => n(t.count >= 1)
    }, {
      points: 1,
      test: t => n(t.destroyer >= 1)
    }, {
      points: 1,
      test: t => n(t.tormented >= 1)
    }, {
      points: 1,
      test: t => n(t.oppressor >= 1)
    }, {
      points: 1,
      test: t => n(t.count / 5)
    }, {
      points: 2,
      test: t => n(t.count / 11)
    }, {
      points: 1,
      test: t => n(t.count / 15)
    }],
    honor: [{
      points: 3,
      test: () => n(!0)
    }, {
      points: 2,
      test: t => n(t.count >= 1)
    }, {
      points: 3,
      test: t => n(t.pvp >= 1)
    }, {
      points: 3,
      test: t => n(t.count / 5)
    }, {
      points: 1,
      test: t => n(t.count / 10)
    }, {
      points: 1,
      test: t => n(t.count / 15)
    }, {
      points: 1,
      test: t => n(t.count / 20)
    }, {
      points: 1,
      test: t => n(t.count / 25)
    }, {
      points: 1,
      test: t => n(t.count / 30)
    }, {
      points: 1,
      test: t => n(t.count / 35)
    }, {
      points: 1,
      test: t => n(t.count / 40)
    }],
    devotion: [{
      points: 1,
      test: t => n(t.count >= 1)
    }, {
      points: 1,
      test: t => n(t.rare >= 1)
    }, {
      points: 1,
      test: t => n(t.unique >= 1)
    }, {
      points: 2,
      test: t => n(t.count / 20)
    }, {
      points: 1,
      test: t => n(t.count / 30)
    }, {
      points: 1,
      test: t => n(t.count / 40)
    }, {
      points: 1,
      test: t => n(t.count / 50)
    }],
    fellowship: [{
      points: 1,
      test: t => n(t.heroes >= 1)
    }, {
      points: 1,
      test: t => n(t.pets >= 1)
    }, {
      points: 1,
      test: t => n(t.rare >= 1)
    }, {
      points: 2,
      test: t => n(t.count / 5)
    }, {
      points: 1,
      test: t => n(t.count / 10)
    }, {
      points: 1,
      test: t => n(t.count / 20)
    }, {
      points: 1,
      test: t => n(t.count / 30)
    }],
    resilience: [{
      points: 1,
      test: t => n(t.count >= 1)
    }, {
      points: 1,
      test: t => n(t.count / 3)
    }, {
      points: 2,
      test: t => n(t.count / 5)
    }, {
      points: 1,
      test: t => n(t.count / 7)
    }, {
      points: 1,
      test: t => n(t.kurzick_luxon)
    }, {
      points: 1,
      test: t => n(t.vabbian)
    }, {
      points: 1,
      test: t => n(t.obsidian)
    }]
  }
}), "@VERSION@", {
  requires: ["base", "arena-base64"]
});
YUI.add("hom-page-control", (function(e) {
  "use strict";
  const t = window.ga || function() {},
    n = e.Lang,
    a = e.namespace("hom"),
    s = a.history = new e.HistoryHash,
    i = a.points,
    o = "pageActive";
  let g = "";
  e.delegate("click", (function(e) {
    const t = e.currentTarget.get("href");
    t && (e.preventDefault(), window.open(t))
  }), "body", "a.external");
  const c = e.Base.create("PageControl", e.Base, [], {
    constructors: {},
    pages: {},
    _requested: {},
    initializer() {
      this.on("pageChange", (function(t) {
        if (!t.newVal) return;
        const s = t.newVal,
          i = this.pages[s];

        function g() {
          e.one("#bd").set("className", s)
        }
        if (i || this._requested[s]) {
          if (!i) return void t.preventDefault();
          g(), n.isFunction(i.activate) && i.activate(), this.fire(o, s), this._historyPageChange(s)
        } else this._requested[s] = !0, e.use(`${s}-page`, (function() {
          const e = a.pageControl,
            i = e.constructors[s];
          n.isFunction(i) ? (g(), e.pages[s] = new i, e.fire(o, s), e._historyPageChange(s)) : t.preventDefault()
        }))
      }), this), s.on("pageChange", (function(e) {
        "add" !== e.src && (t(`${g}.send`, "event", "Pages", "PageChange", e.newVal), this.set("page", e.newVal))
      }), this), s.on("detailsChange", (function(e) {
        "add" !== e.src && (t(`${g}.send`, "event", "Pages", "DetailsChange", e.newVal), i.update(e.newVal))
      }), this), s.on(["detailsRemove", "pageRemove"], (function() {
        this.set("page", "welcome")
      }), this), e.on("history:change", this._i18nLinkUpdate, this), i.on("updateSuccess", (function(e) {
        const t = s.get("page");
        s.add({
          details: e.details[0],
          page: "welcome" === t ? "main" : t
        })
      })), e.on("click", (function(e) {
        e.preventDefault(), s.add({
          page: "welcome",
          details: null
        })
      }), "#hom", this), this.publish("pageActive", {
        broadcast: 2,
        bubbles: !1,
        emitFacade: !1,
        preventable: !1
      }), this.on(o, (function(e) {
        t(`${g}.send`, "event", "Pages", "PageChange", e)
      }));
      const c = s.get("details") || 0,
        l = s.get("todo");
      let h = s.get("page") || "welcome";
      c && (a.points.update(c), t(`${g}.send`, "event", "Pages", "DetailsChange"), "welcome" === h && (h = "main")), l && (s.replaceValue("todo", null), a.todo.parse(l)), h && e.on("domready", (function() {
        this.set("page", h), t(`${g}.send`, "event", "Pages", "PageChange", h)
      }), this), this._i18nLinkUpdate()
    },
    _historyPageChange(e) {
      const t = "page";
      s[(s.get(t) ? "add" : "replace") + "Value"](t, e)
    },
    _i18nLinkUpdate() {
      e.all("#lang a").each((function(t) {
        const n = t.get("href");
        if (n) {
          const a = `#${e.HistoryHash.getHash()}`;
          t.set("href", -1 !== n.indexOf("#") ? n.replace(c._i18nRegex, `/${a}`) : n + a)
        }
      }))
    }
  }, {
    ATTRS: {
      page: {}
    },
    _i18nRegex: /\/#.+$/
  });
  a.pageControl = new c, e.on("domready", (function() {
    g = t.getAll ? t.getAll().pop().get("name") : ""
  }))
}), "@VERSION@", {
  requires: ["base", "event-delegate", "history-hash", "hom-points"]
});