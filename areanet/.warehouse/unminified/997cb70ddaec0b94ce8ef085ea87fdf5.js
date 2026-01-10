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
YUI.add("hom-reward-meter-overlay", (function(e) {
  "use strict";
  e.once("loader_monitor:ready", (function() {
    const t = e.Lang,
      i = new e.Overlay({
        boundingBox: "#meter-overlay",
        contentBox: "#meter-overlay .bd",
        constrain: "#meter-overlay-container",
        zIndex: 100,
        render: !0,
        visible: !1
      }),
      n = e.all("#monitor .meter li"),
      o = (i.get("boundingBox"), i.get("contentBox")),
      s = {
        height: 0,
        duration: .1
      },
      r = {
        item: "<li><div><a class='icon iconm r{icon}m hide-txt'>Icon {icon}</a></div><h5><span class='ib hide-txt'>Locked</span> {name}</h5><p>{desc}</p></li>",
        title: `<li class='title'><div><a class='icon iconm hide-txt'>Title</a></div><h5><span class='ib hide-txt'>Locked</span> {title}</h5><p>${HOM.titles.desc}</p></li>`
      };

    function a(e) {
      if (e) return t.isObject(e) ? t.sub(r.item, {
        name: e.name,
        icon: e.id + 1 + (e.ver ? e.ver : ""),
        desc: e.desc
      }) : t.sub(r.title, {
        title: e
      })
    }
    i.after("render", (function() {
      this.get("boundingBox").removeClass("hide")
    })), o.setStyle("height", 0), o.on("transition:end", (function(e) {
      parseInt(e.config.height, 10) || i.hide()
    })), o.on("transition:start", (function(e) {
      parseInt(e.config.height, 10) && i.show()
    })), e.delegate("mouseenter", (function(r) {
      const l = n.indexOf(this),
        d = HOM.titles[l + 1],
        c = o.one("ul"),
        h = i.getClassName("hidden"),
        g = this.hasClass("active"),
        m = HOM.rewards.regular;
      let u, v = "";
      u = m[l] ? t.isArray(m[l]) ? m[l].slice(0) : [m[l]] : [];
      const p = Number(u.length);
      d && (u[u.length] = d), o.addClass(h), o.one("h6").setContent(l + 1), o.replaceClass("active", g ? "active" : ""), o.replaceClass("reward-\\d", `reward-${u.length}`);
      for (let i = 0, n = u.length; i < n; i++) v += a(t.isObject(u[i]) ? e.merge(u[i], {
        id: l,
        ver: p > 1 ? "ab".charAt(i) : null
      }) : u[i]);
      c.setContent(v), i.set("align", {
        node: this,
        points: [e.WidgetPositionAlign.TL, e.WidgetPositionAlign.BL]
      }), o.setStyle("height", "auto");
      const f = o.getComputedStyle("height");
      o.removeClass(h), i.get("visible") ? o.transition({
        height: f,
        duration: 0
      }) : (o.setStyle("height", "0px"), o.transition(e.merge(s, {
        height: f
      })))
    }), "#monitor", ".meter .reward"), e.delegate("mouseleave", (function() {
      o.transition(s)
    }), "#monitor", ".rewards ol"), e.delegate("mouseenter", (function() {
      o.transition(s)
    }), "#monitor", ".meter .empty")
  }))
}), "@VERSION@", {
  requires: ["node", "event-mouseenter", "overlay", "gallery-overlay-transition"]
});