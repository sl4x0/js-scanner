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
YUI.add("details-page", (function(t) {
  "use strict";
  const e = t.Lang,
    o = t.namespace("hom");

  function s() {
    t.once("loader_details:ready", (function() {
      const e = new t.TabView({
        srcNode: "#details .tabs"
      }).render();
      this._tabs = e, e.after("selectionChange", this._tabDraw, this), e.on("init", e.deselectAll, e), e.after("render", (function() {
        this.activate()
      }), this), t.delegate("click", (function(t) {
        t.preventDefault(), o.pageControl.set("page", "main")
      }), "#details", "a.back"), o.points.after("characterChange", this._resetTabs, this), o.points.after("valueChange", (function(t) {
        this._listUpdate(t), this._ruleUpdate(t), this._pointUpdate(t)
      }), this), o.todo.after(["change", "hover", "displayChange"], this._todoUpdate, this), this._devotionInteractions()
    }), this)
  }
  s.TEMPLATES = {
    rule: "<li><p class='pts cronos-reg ib'><span class='pts{points}'>{points}</span></p><div class='details'><p class='desc'><span class='rule'>{rule}</span></p><p class='bar'><span class='complete'></span><span class='todo todo-bg'></span><span class='hover todo-hover-bg'></span><span class='outline'></span></p></div></li>",
    item: "<li class='{todoClass} item' title=\"{title}\"><p class='ib hide-txt todo-bg'>active</p><span class='txt'>{item}</span>{add}{del}</li>",
    todo: "<a href='#todo' class='ib {state}-todo hide-txt'>{title}</a>",
    devotion: "<li>{type}&nbsp;<span class='count'>({count})</span></li>",
    devotion_todo: "<li class='type-{name}'><span class='txt'>{type}</span>&nbsp;<span class='count'>({count})</span><a href='#up' class='todo-up hide-txt'>Up</a><a href='#down' class='todo-down hide-txt'>Down</a></li>"
  }, s.prototype = {
    activate() {
      this._tabs.selectChild(o.tab || 0)
    },
    _resetTabs() {
      this._tabs.each((function(t) {
        t.get("panelNode").removeClass("ready")
      })), this._tabs.deselectAll()
    },
    _tabDraw(e) {
      if (!e.newVal) return;
      const s = e.newVal.get("panelNode"),
        n = s.get("id").split("-")[1],
        a = o.points.get(n),
        i = HOM.urls.wiki;
      if (!s.hasClass("ready")) {
        s.addClass("blanked");
        const e = t.one("#tabSkeleton").cloneNode(!0);
        e.set("id", ""), e.removeClass("hide"), s.setContent(e), s.all(".have ul, .want ul").addClass(`section-${n}`);
        const l = s.one("h2");
        l.one("span").setContent(HOM.cols.details[n].title);
        l.one("a").set("href", i._base + i[n]);
        const d = {
          newVal: a,
          attrName: n
        };
        this._listDraw(d), this._pointDraw(d), this._ruleDraw(d), s.one(".points .total").setContent(`/${a.possible}`), s.replaceClass("blanked", "ready");
        const r = o.Todo.data({
          section: n
        });
        this._listUpdate(r), this._pointUpdate(r), this._ruleUpdate(r)
      }
    },
    _pointDraw(e) {
      const s = t.one(`#tab-${e.attrName}`),
        n = e.newVal;
      s.hasClass("yui3-tab-panel-selected") ? o.pointsAnim(s.one(".points"), n.total) : (s.one(".points .count").setContent(n.total), s.one(".points").replaceClass("points\\d+", `points${n.total}`))
    },
    _listDraw(n) {
      if ("devotion" === n.attrName) return void this._devotionDraw(n);
      const a = t.one(`#tab-${n.attrName}`);
      if (a) {
        const t = a.one(".have ul"),
          i = a.one(".want ul"),
          l = o.points.get(`character.${n.attrName}`),
          d = [],
          r = [],
          p = s.TEMPLATES,
          c = HOM.strings;
        for (const t in l) l.hasOwnProperty(t) && t.length && (l[t] ? r : d).push(e.sub(p.item, {
          todoClass: l[t] ? "" : "todo-item",
          section: n.attrName,
          item: t,
          add: l[t] ? "" : e.sub(p.todo, {
            state: "add",
            title: c.TodoAdd
          }),
          del: l[t] ? "" : e.sub(p.todo, {
            state: "del",
            title: c.TodoDel
          })
        }));
        r.length && t.setContent(r.join("")), d.length && i.setContent(d.join("")), a.one(".have h3 span").setContent(`(${r.length})`), a.one(".want h4 span").setContent(`(${d.length})`)
      }
    },
    _ruleDraw(n) {
      const a = t.one(`#tab-${n.attrName}`);
      if (a) {
        const t = [],
          i = a.one(".rules"),
          l = o.rules[n.attrName];
        for (let o = 0; o < l.length; o++) t.push(e.sub(s.TEMPLATES.rule, {
          points: l[o].points,
          rule: HOM.rules.rules[n.attrName][o]
        }));
        i.setContent(t.join(""))
      }
    },
    _pointUpdate(e) {
      const s = t.one(`#tab-${e.details.section}`);
      let n, a;
      if (!s || !s.hasClass("ready")) return;
      const i = s.one(".hd .points");
      n = e.points.complete.total, o.todo.get("display") && e.points.todo.total > e.points.complete.total && (a = !0, n = e.points.todo.total), i[a ? "addClass" : "removeClass"]("todo-txt"), o.pointsAnim(i, n, .1)
    },
    _listUpdate(e) {
      const s = HOM.strings;
      if ("devotion" === e.details.section) return void this._devotionUpdate(e);
      const n = t.one(`#tab-${e.details.section}`);
      if (!n || !n.hasClass("ready")) return;
      const a = n.one(".want"),
        i = o.todo.get(e.details.section);
      a.all("li").each((function(t) {
        const e = t.one(".txt").get("innerHTML").replace(/\./g, "-");
        t.set("title", s["Todo" + (i[e] ? "Del" : "Add")]), i[e] ? t.addClass("todo-txt on-todo") : t.removeClass("(todo-txt|on-todo)")
      }))
    },
    _ruleUpdate(e) {
      const s = t.one(`#tab-${e.details.section}`);
      if (!s || !s.hasClass("ready")) return;
      const n = s.all(".rules li"),
        a = o.rules[e.details.section],
        i = o.todo.get("display"),
        l = parseInt(n.item(0).one(".bar").getComputedStyle("width"), 10);
      n.each((function(t, o) {
        const s = a[o].test(e.points.complete),
          n = i ? a[o].test(e.points.todo) : 0,
          d = i && a[o].test(e.points.hover) || 0;
        let r = "";
        1 === s ? r = "active" : i && (1 === n ? r = "todo" : 1 === d && (r = "hover"));
        const p = n > s ? `, ${Math.floor(100*n)}% on 'to do' list` : "";
        t.replaceClass("(active|todo|hover)", r), t.set("title", `${Math.floor(100*s)}% completed${p}`), t.one(".complete").transition({
          width: s * l + "px",
          duration: .1,
          easing: "ease-out"
        }), t.one(".todo").transition({
          width: n * l + "px",
          duration: .1,
          easing: "ease-out"
        }), t.one(".hover").transition({
          width: (d > n ? d : n) * l + "px",
          duration: .1,
          easing: "ease-out"
        })
      }), this)
    },
    _todoUpdate(t) {
      let e;
      "displayChange" === t.type && (e = this._tabs.get("selection").get("panelNode").get("id").split("-")[1], t = o.Todo.data({
        section: e,
        value: t.newVal
      })), this._ruleUpdate(t), this._listUpdate(t), this._pointUpdate(t)
    },
    _devotionInteractions() {
      function e(t) {
        const e = t.ancestor("li"),
          o = e.get("className").match(/type-(\w+)/)[1].toLowerCase();
        return {
          li: e,
          type: o
        }
      }

      function s(t) {
        const s = t.currentTarget,
          n = e(s),
          a = "mouseenter" === t.type,
          i = s.hasClass("todo-up") ? 1 : -1,
          l = o.Todo.data({
            section: "devotion",
            item: n.type,
            on: a ? i : 0
          }, a);
        o.todo.fire("hover", l)
      }
      t.delegate("click", (function(t) {
        t.preventDefault();
        const s = t.target,
          n = e(s),
          a = `devotion.${n.type}`;
        let i = o.todo.get(a) || 0;
        i += s.hasClass("todo-up") ? 1 : -1, i = Math.max(i, 0), i ? n.li.addClass("todo-txt") : (s.addClass("todo-disabled"), n.li.removeClass("todo-txt")), o.todo.set(a, i)
      }), "#tab-devotion", ".todo-up,.todo-down"), t.delegate("mouseenter", s, "#tab-devotion", ".todo-up,.todo-down"), t.delegate("mouseleave", s, "#tab-devotion", ".todo-up,.todo-down")
    },
    _devotionDraw() {
      const n = t.one("#tab-devotion"),
        a = n.one(".have"),
        i = n.one(".want"),
        l = o.points.get("character").devotion,
        d = s.TEMPLATES;
      let r = "",
        p = "",
        c = 0;
      t.each(l, (function(t, o) {
        const s = e.sub(HOM.strings.js.Minis, {
          type: HOM.strings.js.minis[o]
        });
        c += t, r += e.sub(d.devotion, {
          type: s,
          count: t
        }), p += e.sub(d.devotion_todo, {
          name: o,
          type: s,
          count: 0
        })
      })), a.one("ul").setContent(r), i.one("ul").setContent(p), a.one("h3 .quantity").setContent(`(${c})`)
    },
    _devotionUpdate(e) {
      const s = t.one("#tab-devotion .want");
      if (!s) return;
      const n = s.one("h4 .quantity"),
        a = s.one("ul"),
        i = o.points.get("character.devotion");
      let l = 0;
      t.each(e.items.todo, (function(t, e) {
        const o = a.one(`.type-${e}`);
        t -= i[e], l += t, o[t ? "addClass" : "removeClass"]("todo-txt"), o.one(".todo-down")[t ? "removeClass" : "addClass"]("todo-disabled"), o.one(".count").setContent(`(${t})`)
      })), n.setContent(`(${l})`)
    }
  }, t.augment(s, t.EventTarget), o.pageControl.constructors.details = s
}), "@VERSION@", {
  requires: ["event", "tabview", "hom-points", "main-page", "hom-points-header", "hom-reward-meter", "hom-points-animator", "details-page-css", "hom-loader-details"]
});