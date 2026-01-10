YUI.add("release-carousel", function(e) {
  var r = "carousel-foreground",
    t = "disabled",
    u = "transition",
    d = "current-slide",
    s = e.all("#carousel-nav a"),
    n = e.one("#carousel-nav .prev"),
    a = e.one("#carousel-nav .next"),
    i = e.one("#carousel-slides ." + d),
    c = "ease-out",
    f = "ease-in",
    h = .8,
    v = "linear",
    C = "linear",
    x = .8,
    p = "30%",
    S = {
      left: 0,
      width: "auto",
      "z-index": 0
    };

  function l(e, t, s) {
    var n = "-",
      a = "",
      i = e.all("." + r),
      l = t.all("." + r),
      o = e.get("offsetWidth");
    "left" === s && (n = "", a = "-"), e.setStyle("width", o + "px").addClass(u), t.setStyles({
      width: o,
      left: a + o + "px",
      zIndex: 2
    }).addClass(u), l.each(function() {
      this.setStyle("left", a + p)
    }), e.transition({
      easing: f,
      left: n + o + "px",
      duration: h
    }, function() {
      this.setStyles(S).removeClass(u).removeClass(d)
    }), i.each(function(e) {
      e.transition({
        easing: C,
        left: n + p,
        duration: x
      }, function() {
        this.setStyles(S)
      })
    }), t.transition({
      easing: c,
      left: 0,
      duration: h
    }, function() {
      this.setStyles(S).removeClass(u).addClass(d)
    }), l.each(function(e) {
      e.transition({
        easing: v,
        left: 0,
        duration: x
      }, function() {
        this.setStyles(S)
      })
    })
  }

  function o() {
    i.previous() ? n.removeClass(t) : n.addClass(t), i.next() ? a.removeClass(t) : a.addClass(t)
  }
  s.each(function(e) {
    e.on("click", function(e) {
      e.preventDefault(), this.hasClass("prev") && (l(i, i.previous(), "left"), i = i.previous(), o()), this.hasClass("next") && (l(i, i.next(), "right"), i = i.next(), o())
    })
  })
}, "@VERSION@", {
  requires: ["node"]
});