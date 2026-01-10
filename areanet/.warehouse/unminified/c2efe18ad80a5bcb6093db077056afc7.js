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
YUI.add("hom-link-btn", (function(e) {
  "use strict";
  e.once("loader_monitor:ready", (function() {
    const o = e.Lang,
      t = e.namespace("hom"),
      n = e.one("#monitor .link");
    let s, i;

    function l() {
      const i = `${window.location}&todo=${t.todo.urlData()}`,
        l = HOM.urls.sharing;
      s && s.ready && s.setText(i), e.each(l, (function(e, t) {
        n.one(`.${t.toLowerCase()}`).set("href", o.sub(e, {
          url: i,
          text: encodeURIComponent(HOM.strings[`${t}Text`])
        }))
      }))
    }
    const a = new e.Anim({
      node: n.one(".main"),
      duration: .5,
      to: {
        backgroundColor: "#000"
      },
      after: {
        end: function() {
          n.removeClass("complete"), this._node.setAttribute("style", "")
        }
      }
    });
    e.delegate("mouseenter", (function(e) {
      n.one("ul").transition({
        height: "90px",
        duration: .1
      })
    }), "#monitor", ".link"), e.delegate("mouseleave", (function(e) {
      n.one("ul").transition({
        height: 0,
        duration: .1
      }), i || (n.one(".instructions").addClass("hide"), n.one(".success").addClass("hide"), n.one(".title").removeClass("hide"))
    }), "#monitor", ".link"), e.delegate("mouseenter", (function(e) {
      i || (n.one(".title").addClass("hide"), n.one(".instructions").removeClass("hide")), l()
    }), "#monitor", ".zeroClipGlue"), e.delegate("mouseleave", (function(e) {
      i || (n.one(".title").removeClass("hide"), n.one(".instructions").addClass("hide"))
    }), "#monitor", ".zeroClipGlue"), e.Get.script("https://2hom.staticwars.com/js/lib/ZeroClipboard.d54ec92.js", {
      onSuccess: function() {
        ZeroClipboard.setMoviePath("https://2hom.staticwars.com/swf/ZeroClipboard.ac2f3f1b.swf"), s = new ZeroClipboard.Client, s.addEventListener("load", l), s.addEventListener("complete", (function() {
          n.one(".title").addClass("hide"), n.one(".instructions").addClass("hide"), n.one(".success").removeClass("hide"), n.addClass("complete"), i = e.later(5e3, null, (function() {
            i = null, n.one(".title").removeClass("hide"), n.one(".instructions").addClass("hide"), n.one(".success").addClass("hide"), a.run()
          }))
        }));
        let o = e.later(50, null, (function() {
          if (n.get("offsetHeight")) {
            o.cancel(), o = null, s.glue(e.Node.getDOMNode(n.one(".main")), e.Node.getDOMNode(n));
            const t = n.all("> div");
            t.item(t.size() - 1).addClass("zeroClipGlue")
          }
        }), null, !0)
      },
      autoPurge: !0
    })
  }))
}), "@VERSION@", {
  requires: ["event-mouseenter", "anim", "transition"]
});