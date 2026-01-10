YUI.add("skip-to-main-content", function(e) {
  var n = e.one("#skip-to-main-content");
  n && n.on("keydown", function(e) {
    32 === e.keyCode && (e.preventDefault(), n.simulate("click"))
  })
}, "@VERSION", {
  requires: ["node", "event", "dom-base"]
});
YUI.add("popup-launcher", function(e) {
  e.all(".popup-launcher").on("click", function(e) {
    var t = e.target.ancestor("a", !0);
    e.preventDefault(), window.open(t.get("href"), t.get("title"), `menubar=no,resizable=yes,width=${t.getData("width")},height=` + t.getData("height"))
  })
}, "@VERSION", {
  requires: ["node"]
});
YUI.add("social-share", function(s) {
  var c, t, a = s.config.doc.getElementsByTagName("script")[0];
  switch (GW2.lang) {
    case "de":
      t = "de_DE";
      break;
    case "fr":
      t = "fr_FR";
      break;
    case "es":
      t = "es_ES";
      break;
    case "uk":
      t = "en_GB";
      break;
    default:
      t = "en_us"
  }
  s.Object.each({
    addthis: {
      id: "addthis-js",
      src: "//s7.addthis.com/js/250/addthis_widget.js#pubid=xa-4f8730771a002a63"
    },
    facebook: {
      id: "facebook-jssdk",
      src: "//connect.facebook.net/{lc}/all.js#xfbml=1"
    },
    googleplus: {
      id: "googleplus-js",
      src: "https://apis.google.com/js/plusone.js"
    },
    twitter: {
      id: "twitter-wjs",
      src: "//platform.twitter.com/widgets.js"
    }
  }, function(e) {
    s.config.doc.getElementById(e.id) || ((c = s.config.doc.createElement("script")).id = e.id, c.src = s.Lang.sub(e.src, {
      lc: t
    }), a.parentNode.insertBefore(c, a))
  })
}, "@VERSION");
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