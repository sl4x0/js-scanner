const HOM_config = {
  ignore: ['skin-sam-overlay', 'skin-sam-widget', 'skin-sam-widget-stack', 'skin-sam-tabview'],
  groups: {
    'js/': {
      combine: !0,
      comboBase: 'https://2hom.staticwars.com/combo/_',
      root: '/js/',
      base: '/js/',
      modules: {
        'hom-character-search': {
          path: 'character-search.5d64adc9.js',
          requires: ['cookie', 'event', 'transition', 'gallery-boxshadow-anim', 'anim-easing', 'hom-points']
        },
        'details-page': {
          path: 'details-page.65fc7926.js',
          requires: ['event', 'tabview', 'hom-points', 'main-page', 'hom-points-header', 'hom-reward-meter', 'hom-points-animator', 'details-page-css', 'hom-loader-details']
        },
        'hom-item-modal': {
          path: 'item-modal.59100bda.js',
          requires: ['base', 'overlay', 'anim', 'gallery-outside-events', 'gallery-overlay-extras', 'gallery-event-nav-keys', 'gallery-overlay-transition']
        },
        'hom-link-btn': {
          path: 'link-btn.5c34039a.js',
          requires: ['event-mouseenter', 'anim', 'transition']
        },
        'hom-loader-details': {
          path: 'loader-details.1d30b28a.js',
          requires: ['gallery-dispatcher']
        },
        'hom-loader-main': {
          path: 'loader-main.92c16671.js',
          requires: ['gallery-dispatcher', 'node', 'event-custom']
        },
        'hom-loader-monitor': {
          path: 'loader-monitor.27a16db.js',
          requires: ['gallery-dispatcher']
        },
        'main-page': {
          path: 'main-page.f0763edf.js',
          requires: ['event-custom', 'transition', 'anim', 'hom-item-modal', 'hom-points-header', 'hom-reward-meter', 'hom-points', 'hom-points-animator', 'hom-loader-main', 'main-page-css']
        },
        'hom-page-control': {
          path: 'page-control.3da3e336.js',
          requires: ['base', 'event-delegate', 'history-hash', 'hom-points']
        },
        'hom-points-animator': {
          path: 'points-anim.b0f4ffd3.js',
          requires: ['node', 'gallery-generic-anim']
        },
        'hom-points-header': {
          path: 'points-header.4b047ff3.js',
          requires: ['node', 'hom-points', 'hom-todo', 'hom-points-animator', 'hom-print-btn', 'hom-link-btn', 'hom-loader-monitor']
        },
        'hom-points': {
          path: 'points.1dd99894.js',
          requires: ['base', 'arena-base64']
        },
        'hom-print-btn': {
          path: 'print-btn.6eebd4fa.js',
          requires: ['event-mouseenter', 'transition']
        },
        'print-page': {
          path: 'print-page.5a4e56fc.js',
          requires: ['base', 'node', 'print-page-css', 'io-base', 'hom-character-search']
        },
        'hom-reward-meter-overlay': {
          path: 'reward-meter-overlay.6dc173d8.js',
          requires: ['node', 'event-mouseenter', 'overlay', 'gallery-overlay-transition']
        },
        'hom-reward-meter': {
          path: 'reward-meter.899e9564.js',
          requires: ['event', 'transition', 'hom-points', 'gallery-generic-anim', 'hom-todo', 'hom-reward-meter-overlay', 'hom-loader-monitor', 'reward-monitor-css', 'icons-css']
        },
        'hom-todo': {
          path: 'todo.906ecd95.js',
          requires: ['base', 'event-mouseenter', 'hom-points', 'oop', 'json', 'cookie']
        },
        'welcome-page': {
          path: 'welcome-page.8694a321.js',
          requires: ['event', 'node', 'hom-character-search', 'hom-page-control']
        }
      }
    },
    'js/gallery/': {
      combine: !0,
      comboBase: 'https://2hom.staticwars.com/combo/_',
      root: '/js/gallery/',
      base: '/js/gallery/',
      modules: {
        'gallery-boxshadow-anim': {
          path: 'boxshadow-anim.411441ac.js',
          requires: ['anim-base']
        },
        'gallery-dispatcher': {
          path: 'dispatcher.b6f8b33d.js',
          requires: ['base', 'node-base', 'io-base', 'get', 'async-queue', 'classnamemanager']
        },
        'gallery-generic-anim': {
          path: 'generic-anim.f946de23.js',
          requires: ['base', 'base-build']
        },
        'gallery-overlay-extras': {
          path: 'overlay-extras.8b77c590.js',
          supersedes: ['gallery-overlay-modal'],
          requires: ['overlay', 'plugin', 'event-resize', 'event-outside']
        }
      }
    },
    'js/lib/': {
      combine: !0,
      comboBase: 'https://2hom.staticwars.com/combo/_',
      root: '/js/lib/',
      base: '/js/lib/',
      modules: {
        'arena-base64': {
          path: 'Base64Codec.2e2f6a63.js',
          requires: []
        }
      }
    },
    css: {
      combine: !0,
      comboBase: 'https://2hom.staticwars.com/combo/_',
      root: '/css/',
      base: '/css/',
      modules: {
        'icons-css': {
          path: 'icons.3bdf6a84.css',
          type: 'css'
        },
        'main-page-css': {
          path: 'main-page.1f3c1616.css',
          type: 'css'
        },
        'details-page-css': {
          path: 'details-page.69272956.css',
          type: 'css'
        },
        'reward-monitor-css': {
          path: 'reward-monitor.66eb93b.css',
          type: 'css'
        },
        'print-page-css': {
          path: 'print-page.32fc1a61.css',
          type: 'css'
        }
      }
    }
  }
}
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