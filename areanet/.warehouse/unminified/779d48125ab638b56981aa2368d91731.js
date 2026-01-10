YUI.add("takeover", function(a) {
  let i = a.one(".takeover"),
    r = .5,
    s = .2,
    l = ".takeover-close",
    c = ".takeover-open";
  if (i) {
    let n = i.get("id"),
      e = a.one(".takeover-hero-controls"),
      o = a.one(".takeover-hero-controls-bg");
    a.Cookie.get(n) ? f(c) : (k(), window.dataLayer = window.dataLayer || [], window.dataLayer.push({
      event: "takeover_hero_auto"
    })), a.one("doc").on("keydown", function(t) {
      27 === t.keyCode && y()
    }), e.all(c).each(function(t) {
      t.on("click", function() {
        k()
      })
    });
    e.all(l).each(function(t) {
      t.on("click", function() {
        y()
      })
    });
    var t = i.one(".letter");

    function d(t) {
      300 < window.scrollY && (y(), document.removeEventListener("scroll", d))
    }

    function u(t) {
      o.transition({
        duration: s,
        transform: "translateY(-100%)"
      }, function() {
        this.setStyle("display", "none")
      }), e.one(t).transition({
        duration: s,
        transform: "translateY(-100%)",
        opacity: 0
      }, function() {
        this.setStyle("display", "none")
      })
    }

    function f(t) {
      o.setStyle("display", "block").transition({
        duration: s,
        transform: "translateY(0)"
      }), e.one(t).setStyle("display", "block").transition({
        duration: s,
        transform: "translateY(0)",
        opacity: 1
      })
    }

    function y() {
      u(l), document.removeEventListener("scroll", d), i.transition({
        duration: r,
        transform: "translateY(-100%)",
        opacity: 0
      }, function() {
        f(c)
      });
      var t = new Date;
      t.setFullYear(t.getFullYear() + 10), a.Cookie.set(n, (new Date).toJSON(), {
        path: "/",
        expires: t
      })
    }

    function k() {
      u(c), document.addEventListener("scroll", d), i.setStyle("display", "block").transition({
        duration: r,
        transform: "translateY(0)",
        opacity: 1
      }, function() {
        f(l)
      })
    }
    t && t.on("click", function() {
      y()
    })
  }
}, "@VERSION@", {
  requires: ["node", "event", "event-key", "transition", "cookie"]
});