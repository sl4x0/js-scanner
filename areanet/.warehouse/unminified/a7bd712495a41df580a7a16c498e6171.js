YUI.add("gallery-boxshadow-anim", (function(o) {
  var e = function() {
      var o, e, t = document.createElement("boxshadowtest"),
        n = ["boxShadow", "MozBoxShadow", "WebkitBoxShadow", "KhtmlBoxShadow"];
      for (o = 0, e = n.length; o < e; o++)
        if (void 0 !== t.style[n[o]]) return t = null, n[o]
    }(),
    t = function(o) {
      return parseInt(o, 10)
    },
    n = /(\-?[\d\.]+(px)?)/,
    l = /\s*(rgb\(.+\)|#\w{3,6}|[^#]?[a-z]{3,})\s*/i,
    r = function(e) {
      var t, r, h, s, g, i, c, a, d, f = [0, 0, 0, 0],
        u = ["rgb(0, 0, 0)", 0, 0, 0];
      if (!e || "none" === e) return {
        lengths: f,
        color: u,
        inset: !1
      };
      for (t = {
          lengths: f,
          inset: -1 != e.indexOf("inset")
        }, g = 0, i = (r = e.split(l)).length; g < i; g++)
        if (r[g].length)
          if (l.test(r[g]) && !t.color) t.color = o.Color.re_RGB.exec(o.Color.toRGB(r[g]));
          else
            for (d = 0, c = 0, a = (h = r[g].split(" ")).length; c < a; c++)(s = h[c].match(n)) && s.length && (t.lengths[d++] = s[0]);
      return t.color || (t.color = u), t.lengths.length || o.error("sending back bad output!"), t
    };
  o.Anim.behaviors.boxShadow = {
    set: function(n, l, h, s, g, i, c) {
      var a;
      h = r("object" == typeof h ? h.getStyle(e) : h), s = r("object" == typeof s ? s.getStyle(e) : s), (!h.color || h.color.length < 3 || !s.color || s.color.length < 3) && o.error("invalid from or to passed to color behavior"), h.lengths.length != s.lengths.length && o.error("invalid from or to length definition"), a = c(g, t(h.lengths[0]), t(s.lengths[0]) - t(h.lengths[0]), i) + "px " + c(g, t(h.lengths[1]), t(s.lengths[1]) - t(h.lengths[1]), i) + "px " + c(g, t(h.lengths[2]), t(s.lengths[2]) - t(h.lengths[2]), i) + "px " + c(g, t(h.lengths[3]), t(s.lengths[3]) - t(h.lengths[3]), i) + "px rgb(" + [Math.floor(c(g, t(h.color[1]), t(s.color[1]) - t(h.color[1]), i)), Math.floor(c(g, t(h.color[2]), t(s.color[2]) - t(h.color[2]), i)), Math.floor(c(g, t(h.color[3]), t(s.color[3]) - t(h.color[3]), i))].join(", ") + ")" + (s.inset ? "inset" : ""), n._node.setStyle(e, a)
    },
    get: function(o, t) {
      return o._node.getComputedStyle(e) || o._node
    }
  }
}), "@VERSION@", {
  requires: ["anim-base"]
});
YUI.add("hom-character-search", (function(e) {
  "use strict";
  const n = e.Lang,
    o = e.namespace("hom"),
    t = o.points,
    a = new e.Anim({
      node: "#hd .char",
      from: {
        boxShadow: "0 0 5px 2px #493401"
      },
      to: {
        boxShadow: "0 0 16px 2px #FFBA00"
      },
      easing: e.Easing.easeOut,
      duration: 2,
      iterations: "infinite",
      direction: "alternate"
    }),
    r = new e.Anim({
      node: "#hd .char",
      to: {
        boxShadow: "0 0 10px 2px red"
      },
      easing: e.Easing.easeOut
    }),
    s = new e.Anim({
      node: "#hd .char",
      to: {
        boxShadow: "0 0 #FFF"
      },
      easing: e.Easing.easeOut
    });
  let i, c, l;

  function u() {
    r.stop(), h(), s.run(), e.one("#hd .char").removeClass("error"), i.detach(), i = null, c && n.isFunction(c.cancel) && (c.cancel(), c = null)
  }

  function d() {
    l && (l.show(), l.get("boundingBox").transition({
      duration: .5,
      easing: "ease-out",
      top: "85px"
    }))
  }

  function h() {
    l && l.get("boundingBox").transition({
      duration: .5,
      easing: "ease-out",
      top: "-5px"
    }, (function() {
      l.hide()
    }))
  }

  function g(n) {
    e.one("#char-error").replaceClass("(default|lose-todo|no-data)", n)
  }

  function p(n) {
    if (arguments[1] && arguments[1].responseText) try {
      n = e.JSON.parse(arguments[1].responseText).error
    } catch (e) {}
    g(!0 === n || 238 === n ? "no-data" : "default"), a.stop(), d(), i = e.on("keydown", u, "#char-name"), c = e.later(5e3, null, u), e.one("#hd .char").addClass("error"), r.run()
  }
  e.on("available", (function() {
    "placeholder" in e.Node.getDOMNode(this) || (this.set("value", this.getAttribute("placeholder")), this.on(["focus", "click"], (function(e) {
      e.target.select()
    })), this.on("blur", (function(e) {
      const n = e.target;
      n.get("value").length || n.set("value", n.getAttribute("placeholder"))
    })))
  }), "#char-name"), e.on("domready", (function() {
    e.one("#char-name").get("value").length || o.history.get("details") || a.run(), e.use("overlay", (function(e) {
      l = new e.Overlay({
        boundingBox: "#char-error",
        contentBox: "#char-error .bd",
        visible: !1,
        render: !0,
        zIndex: 3
      }), l.get("boundingBox").removeClass(`(${l.getClassName("hidden")}|hide)`), l.set("align", {
        node: e.one("#hd fieldset"),
        points: [e.WidgetPositionAlign.BC, e.WidgetPositionAlign.TC]
      })
    }))
  })), t.on("updateSuccess", (function() {
    a.stop(), s.run(), o.pageControl.set("page", "main")
  })), t.on("updateFailure", p, this), e.once("keydown", (function() {
    e.use("io-base", "json-parse", "main-page")
  }), "#char-name"), e.on("focus", (function() {
    const n = e.Cookie.getSub("todo", "values");
    !!n && n.match(/[^A]/) && "welcome" !== o.pageControl.get("page") && (g("lose-todo"), d())
  }), "#char-name"), e.on("blur", (function() {
    !e.one("#char-error").hasClass("lose-todo") || c || i || h()
  }), "#char-name"), e.on("submit", (function(n) {
    n.preventDefault(), n.target.hasClass("loading") || (n.target.addClass("loading"), e.use("io-base", "json-parse", (function(e) {
      const n = e.namespace("hom").points;
      let t = e.one("#char-name").get("value");
      e.one("#hd .char").removeClass("error"), h(), t = t.toLowerCase().replace(/\b([a-z])/gi, (function(e) {
        return e.toUpperCase()
      })), e.io(`/character/${encodeURIComponent(t)}`, {
        on: {
          success: function(a, r) {
            let s;
            try {
              s = e.JSON.parse(r.responseText)
            } catch (e) {
              return
            }
            e.one("#char-name").set("value", t), s.legacy_bits && (o.todo.reset(), n.update(s.legacy_bits))
          },
          failure: p,
          complete: function() {
            e.one("#hd form").removeClass("loading")
          }
        }
      })
    })))
  }), "#hd form")
}), "@VERSION@", {
  requires: ["cookie", "event", "transition", "gallery-boxshadow-anim", "anim-easing", "hom-points"]
});
YUI.add("welcome-page", (function(e) {
  "use strict";
  e.namespace("hom").pageControl.constructors.welcome = function() {}
}), "@VERSION@", {
  requires: ["event", "node", "hom-character-search", "hom-page-control"]
});