YUI.add("home", function(o) {
  var e, n, t, i, r = ["hobbit"];
  for (new o.Charrousel({
      srcNode: ".home .yui3-charrousel-content",
      boundingBox: ".home .yui3-charrousel",
      contentBox: ".home .yui3-charrousel-content",
      render: !0,
      "show.next": !1,
      "show.prev": !1,
      "show.location": ".yui3-charrousel-nav",
      plugins: [{
        fn: o.CharrouselTimer,
        cfg: {
          delay: 1e4
        }
      }, {
        fn: o.CharrouselFade,
        cfg: {
          "transition.base.duration": .4
        }
      }],
      after: {
        render: function() {
          this.get("contentBox").one("ol").removeClass("hide")
        }
      }
    }), new o.TabView({
      boundingBox: ".yui3-tabview",
      contentBox: ".yui3-tabview-content",
      render: !0
    }), (n = o.one(".interstitial")) && (n = n.get("id"), e = o.Cookie.get(n), n) && !e && (t = new o.Panel({
      srcNode: ".interstitial",
      centered: !0,
      render: !0,
      modal: !0,
      zIndex: 9998,
      hideOn: [{
        eventName: "clickoutside"
      }],
      buttons: [{
        value: "",
        action: function(e) {
          e.preventDefault(), o.all(".yui3-panel, .yui3-widget-mask").transition({
            opacity: 0,
            duration: 1
          }, function() {
            t.hide()
          })
        },
        section: o.WidgetStdMod.HEADER
      }]
    }), o.Cookie.set(n, "shown", {
      path: "/",
      expires: new Date("January 1, 2015")
    })), i = 0; i < r.length; i++) o.Cookie.remove(r[i], {
    path: "/"
  })
}, "@VERSION@", {
  requires: ["node", "event-delegate", "tabview", "charrousel-timer", "charrousel-fade", "panel", "cookie"]
});
YUI.add("skip-to-main-content", function(e) {
  var n = e.one("#skip-to-main-content");
  n && n.on("keydown", function(e) {
    32 === e.keyCode && (e.preventDefault(), n.simulate("click"))
  })
}, "@VERSION", {
  requires: ["node", "event", "dom-base"]
});
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
YUI.add("main-menu", function(e) {
  let o = "sub-open";
  var n = e.one("#menu-header-nav");
  let t = !0;
  e.one("#main-hamburger").on("click", () => {
    t && (t = !1, window.document.body.classList.add("main-nav-opened")), window.document.body.classList.toggle("main-nav-open")
  }), n.delegate("click", function(e) {
    if (e.target === e.currentTarget) {
      let n = e.target.getDOMNode().parentNode;
      var e = n,
        t = e => {
          n === e ? n.classList.toggle(o) : e.classList.remove(o)
        },
        a = e.parentNode.children;
      for (let e = 0; e < a.length; e++) t(a[e], e, a)
    }
  }, ".menu-item-has-children .menu-expand")
}, "@VERSION@", {
  requires: ["node", "event-hover", "transition"]
});
YUI.add("yulb", function(r) {
  var e = r.all(".yulb-launcher"),
    t = window.document.body.clientWidth,
    t = t < 1e3 ? t - 60 : 1e3,
    s = {
      width: t,
      height: .5625 * t,
      params: {
        autoplay: 1,
        modestbranding: 1,
        showinfo: 0,
        rel: 0,
        autohide: 1,
        wmode: "transparent",
        enablejsapi: 1
      }
    },
    t = new URLSearchParams(location.search).get("play"),
    i = r.one(".yulb-launcher"),
    a = r.one(`[data-vidid=${t}]`);
  r.yulb = {
    defaults: s,
    launchers: e
  }, e.isEmpty() || (e.each(function(o) {
    o.on("click", function(e) {
      var t = {
          vidid: o.getData("vidid"),
          width: parseInt(o.getData("vidwidth"), 10) || s.width,
          height: parseInt(o.getData("vidheight"), 10) || s.height,
          params: r.Array.map(r.Object.keys(s.params), function(e) {
            return e + "=" + s.params[e]
          }).join("&")
        },
        i = {
          width: r.DOM.winWidth(),
          height: r.DOM.winHeight()
        },
        a = {
          width: t.width,
          height: t.height
        },
        d = {
          launcher: o,
          vidid: t.vidid
        },
        n = r.Node.create(r.Lang.sub("<div class='yulb-overlay' style='width:{width}px; height: {height}px;'></div>", i)),
        h = r.Node.create(r.Lang.sub("<div class='yulb-container' style='width:{width}px; height:{height}px;'></div>", a));
      e.preventDefault(), h.appendTo(n), r.Node.create("<div class='yulb-close'>close</div>").appendTo(h), r.Node.create(r.Lang.sub("<iframe type='text/html' width='{width}' height='{height}' src='https://www.youtube.com/embed/{vidid}?{params}' frameborder='0' allow='autoplay'/>", t)).appendTo(h), n.appendTo(document.body), r.fire("yulb:open", d), s.params.mute = 0, n.on("click", function() {
        var e = this;
        h.getDOMNode().getElementsByTagName("iframe")[0].contentWindow.postMessage(JSON.stringify({
          event: "command",
          func: "stopVideo"
        }), "*"), setTimeout(function() {
          e.remove(!0)
        }, 100), r.fire("yulb:close", d)
      }), r.on("windowresize", function() {
        n.setStyles({
          width: r.DOM.winWidth(),
          height: r.DOM.winHeight()
        })
      })
    })
  }), t && (i || a) && (s.params.mute = 1, (i || a).getDOMNode().click()))
}, "@VERSION@", {
  requires: ["node", "event", "array-extras"]
});
YUI.add("media", function(n) {
  var o, e, t, r, s = n.one(".video-selector");

  function c(e) {
    return new n.Lightbox({
      items: e,
      render: !0
    })
  }
  s && (o = s.one(".featured iframe"), s.delegate("click", function(e) {
    var t = e.currentTarget.getData("vidid");
    t && (e.preventDefault(), o.set("src", n.Lang.sub("//www.youtube.com/embed/{vidId}?rel=0&modestbranding=1&showinfo=0", {
      vidId: t
    })))
  }, ".inl-video")), e = c(".screenshots .screenshot"), t = c(".lb-screenshots .screenshot"), r = c(".concept-art .concept"), n.on({
    "screenshotLightbox:init": function() {
      e.destroy(), t.destroy(), e = c(".screenshots .screenshot"), t = c(".lb-screenshots .screenshot")
    },
    "conceptartLightbox:init": function() {
      r.destroy(), r = c(".concept-art .concept")
    }
  })
}, "@VERSION@", {
  requires: ["lightbox-widget"]
});
YUI.add("rating", function(e) {
  var s = "/ws/rating",
    r = e.parseUri(location.href).queryKey.fakeip,
    o = "esrb",
    a = ["usk", "pegi"],
    i = e.one("html"),
    t = e.one("a.rating"),
    n = e.one(".gw2-footer");
  t && n && (r && (s += "?fakeip=" + r), e.io(s, {
    on: {
      complete: function(e, s) {
        !s.responseText || a.indexOf(s.responseText) < 0 || ("usk" === s.responseText ? (i.removeClass(o), n.removeClass(o), t.remove()) : (i.removeClass(o), n.removeClass(o).addClass("pegi"), t.removeClass(o).addClass("pegi").setAttribute("href", "https://pegi.info").setHTML("PEGI")))
      }
    }
  }))
}, "@VERSION@", {
  requires: ["node", "io-base", "gallery-parseuri"]
});
YUI.add("snow", function(t) {
  var o, i, r = window.innerHeight,
    e = window.innerWidth,
    d = `<canvas id='snow' style='position: fixed; pointer-events: none; z-index: 1000;' width='${e}' height='${r}'></canvas>`,
    a = e * r / 1e3,
    s = [],
    w = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65],
    c = 0,
    n = (new Date).getMonth(),
    h = 0;

  function u(e, n, t) {
    n = Math.random() * (n - e) + e;
    return n = t ? Math.floor(n) : n
  }

  function l() {
    return {
      x: u(0, e),
      r: u(1, 4, !0),
      v: u(.02, .05),
      y: 0
    }
  }

  function y(n) {
    h = h || n - 16, s.length < a && s.push(l()), i.clearRect(0, 0, e, r), i.beginPath(), s.forEach(function(e) {
      return e.y += e.r * (n - h) * e.v, r < e.y && Object.assign(e, l()), i.moveTo(e.x, e.y), i.arc(e.x, e.y, e.r, 0, 2 * Math.PI), !0
    }), i.fill(), h = n, requestAnimationFrame(y)
  }!window.requestAnimationFrame || n < 10 && 2 < n || window.addEventListener("keydown", function e(n) {
    w[c] === n.keyCode ? (c++, w.length === c && (o = t.Node.create(d), t.one(document.body).prepend(o), (i = document.getElementById("snow").getContext("2d")).fillStyle = "hsl(0, 0%, 95%)", y(), window.removeEventListener("keydown", e))) : c = 0
  })
}, "@VERSION", {
  requires: ["node"]
});